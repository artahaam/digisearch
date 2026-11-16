import logging
import subprocess
import sys
from datetime import datetime, timedelta

from airflow.sdk import DAG, get_current_context, task  #type: ignore

log = logging.getLogger(__name__)


def run_stage(*args: str) -> None:
    cmd = [sys.executable, "-m", "digisearch.pipeline.run", *args]
    log.info("Running: %s", " ".join(cmd))
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in proc.stdout: #type: ignore
        log.info(line.rstrip())
    rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"stage {' '.join(args)} failed with exit code {rc}")


with DAG(
    dag_id="digisearch_pipeline",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 2, "retry_delay": timedelta(seconds=30)},
    params={
        "max_categories": 0,      # 0 = all categories
        "category_ids": "",       # e.g. "9504" or "9504,1234"; empty = not used
    },
    tags=["digisearch"],
):

    @task
    def setup():
        run_stage("setup")

    @task
    def categories():
        run_stage("categories")

    @task
    def list_categories() -> list:
        from digisearch.database.client import get_db

        params = get_current_context()["params"]
        wanted = [int(x) for x in str(params["category_ids"]).split(",") if x.strip()]
        if wanted:
            return wanted

        ids = sorted(get_db()["categories"].distinct("category_id"))
        limit = params["max_categories"]
        return ids[:limit] if limit else ids

    @task(max_active_tis_per_dag=2)
    def products(category_id):
        run_stage("products", "--category", str(category_id))

    @task(trigger_rule="all_done", execution_timeout=timedelta(hours=3))
    def embed():
        run_stage("embed")

    @task
    def prune():
        run_stage("prune")

    ids = list_categories()
    mapped = products.expand(category_id=ids)  # type: ignore

    setup() >> categories() >> ids  # type: ignore
    mapped >> embed() >> prune()  # type: ignore