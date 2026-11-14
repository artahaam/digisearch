from pathlib import Path
from types import SimpleNamespace

import pytest
from airflow.models import DagBag # type: ignore

# Airflow's `dags/` folder isn't an installed package, so import the module from its path
import importlib.util

DAG_FILE = Path(__file__).resolve().parents[2] / "airflow" / "dags" / "digisearch_pipeline.py"
spec = importlib.util.spec_from_file_location("digisearch_pipeline", DAG_FILE)
dag_module = importlib.util.module_from_spec(spec) # type: ignore
spec.loader.exec_module(dag_module) # type: ignore


# ---------------------------------------------------------------------------
# 1. DAG Integrity & Wiring (DagBag)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def dag_bag():
    return DagBag(dag_folder=str(DAG_FILE.parent))


def test_dag_loads_with_no_import_errors(dag_bag):
    assert dag_bag.import_errors == {}
    assert "digisearch_pipeline" in dag_bag.dags


def test_dag_schedule_and_safety_settings(dag_bag):
    dag = dag_bag.dags["digisearch_pipeline"]

    assert dag.schedule == "@daily"
    assert dag.catchup is False
    assert dag.max_active_runs == 1
    assert dag.default_args["retries"] == 2


def test_dag_task_dependencies_and_rules(dag_bag):
    dag = dag_bag.dags["digisearch_pipeline"]

    assert set(dag.task_ids) == {
        "setup",
        "categories",
        "list_categories",
        "products",
        "embed",
        "prune",
    }

    # Check exact upstream -> downstream chain
    assert dag.get_task("setup").downstream_task_ids == {"categories"}
    assert dag.get_task("categories").downstream_task_ids == {"list_categories"}
    assert dag.get_task("list_categories").downstream_task_ids == {"products"}
    assert dag.get_task("products").downstream_task_ids == {"embed"}
    assert dag.get_task("embed").downstream_task_ids == {"prune"}

    # Critical guardrails: embed runs even if one category failed, and max 2 categories run at once
    assert dag.get_task("embed").trigger_rule == "all_done"
    assert dag.get_task("products").max_active_tis_per_dag == 2

# ---------------------------------------------------------------------------
# 2. Helper & Task Logic (`run_stage` and `list_categories`)
# ---------------------------------------------------------------------------


def test_run_stage_raises_on_nonzero_exit_code(monkeypatch):
    def fake_popen(cmd, **kwargs):
        return SimpleNamespace(stdout=iter(["step failed\n"]), wait=lambda: 1)

    monkeypatch.setattr(dag_module.subprocess, "Popen", fake_popen)

    with pytest.raises(RuntimeError, match="failed with exit code 1"):
        dag_module.run_stage("products", "--category", "10")


def test_list_categories_prefers_explicit_category_ids(monkeypatch):
    # Even if DB has categories, explicit `category_ids` param wins
    fake_db = {"categories": SimpleNamespace(distinct=lambda field: [1, 2, 3])}
    monkeypatch.setattr("digisearch.database.client.get_db", lambda: fake_db)
    monkeypatch.setattr(
        dag_module,
        "get_current_context",
        lambda: {"params": {"category_ids": "9504, 1234", "max_categories": 1}},
    )

    # `.function` unwraps the Airflow @task decorator so we can call the plain Python function
    assert dag_module.list_categories.function() == [9504, 1234]


def test_list_categories_reads_sorted_db_ids_and_applies_limit(monkeypatch):
    fake_db = {"categories": SimpleNamespace(distinct=lambda field: [30, 10, 20])}
    monkeypatch.setattr("digisearch.database.client.get_db", lambda: fake_db)
    monkeypatch.setattr(
        dag_module,
        "get_current_context",
        lambda: {"params": {"category_ids": "", "max_categories": 2}},
    )

    assert dag_module.list_categories.function() == [10, 20]