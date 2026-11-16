import time
from datetime import UTC, datetime, timedelta

import pytest

from digisearch.database.client import get_db
from digisearch.pipeline import store_products as sp
from digisearch.services.fingerprint import document_and_hash

pytestmark = pytest.mark.integration


def install_fake_api(monkeypatch, ids_by_category, fail=()):
    fetched = []

    def fake_product(pid):
        fetched.append(pid)
        return None if pid in fail else {"product_id": pid, "product_title_en": f"Product {pid}"}

    monkeypatch.setattr(sp, "fetch_category_pages", lambda cat: 1)
    monkeypatch.setattr(sp, "fetch_product_ids", lambda cat, page: ids_by_category.get(cat, []))
    monkeypatch.setattr(sp, "fetch_product", fake_product)
    return fetched


def add_categories(*ids):
    get_db()["categories"].insert_many([{"category_id": i} for i in ids])


# --------------------------------------------------------------------------
# save_product
# --------------------------------------------------------------------------


def test_save_product_inserts_then_updates_the_same_document():
    products = get_db()["products"]
    first = {"product_id": 7, "product_title_en": "Phone"}
    sp.save_product(first)
    stored_first = products.find_one({"product_id": 7})
    assert stored_first is not None

    time.sleep(0.02)
    sp.save_product({"product_id": 7, "product_title_en": "Phone Pro"})

    assert products.count_documents({"product_id": 7}) == 1     # upsert, no duplicate
    stored = products.find_one({"product_id": 7})
    assert stored is not None
    assert stored["product_title_en"] == "Phone Pro"
    assert stored["fetched_at"] > stored_first["fetched_at"]
    assert stored["content_hash"] == document_and_hash(
        {"product_id": 7, "product_title_en": "Phone Pro"}
    )[1]


# --------------------------------------------------------------------------
# store()
# --------------------------------------------------------------------------


def test_store_saves_products_with_their_category(monkeypatch):
    add_categories(10, 20)
    install_fake_api(monkeypatch, {10: [1, 2], 20: [3]})

    assert sp.store() == {"saved": 3, "failed": 0, "skipped": 0}

    stored = {d["product_id"]: d["category_id"] for d in get_db()["products"].find()}
    assert stored == {1: 10, 2: 10, 3: 20}


def test_second_run_skips_recently_fetched_products(monkeypatch):
    add_categories(10, 20)
    fetched = install_fake_api(monkeypatch, {10: [1, 2], 20: [3]})
    sp.store()
    fetched.clear()

    assert sp.store() == {"saved": 0, "failed": 0, "skipped": 3}
    assert fetched == []


def test_zero_window_refetches_everything(monkeypatch):
    add_categories(10)
    install_fake_api(monkeypatch, {10: [1, 2]})
    sp.store()

    assert sp.store(max_age_hours=0) == {"saved": 2, "failed": 0, "skipped": 0}


def test_products_older_than_the_window_are_refetched(monkeypatch):
    add_categories(10)
    install_fake_api(monkeypatch, {10: [1, 2]})
    sp.store()
    get_db()["products"].update_many(
        {}, {"$set": {"fetched_at": datetime.now(UTC) - timedelta(hours=48)}}
    )

    assert sp.store() == {"saved": 2, "failed": 0, "skipped": 0}     # default window is 24 h


def test_store_only_visits_the_requested_categories(monkeypatch):
    add_categories(10, 20)
    install_fake_api(monkeypatch, {10: [1, 2], 20: [3]})

    sp.store(filters=[20])

    assert [d["product_id"] for d in get_db()["products"].find()] == [3]


def test_failed_products_are_counted_and_not_stored(monkeypatch):
    add_categories(10)
    install_fake_api(monkeypatch, {10: [1, 2, 3]}, fail={2})

    assert sp.store() == {"saved": 2, "failed": 1, "skipped": 0}
    assert get_db()["products"].count_documents({"product_id": 2}) == 0
