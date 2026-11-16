from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

from digisearch.config import REFETCH_AFTER_HOURS
from digisearch.pipeline import store_products as sp
from digisearch.services.fingerprint import document_and_hash

# --------------------------------------------------------------------------
# helpers: a tiny in-memory stand-in for the two Mongo calls the code makes
# --------------------------------------------------------------------------


class FakeCategories:
    def __init__(self, category_ids):
        self.docs = [{"category_id": c} for c in category_ids]
        self.find_calls = []

    def find(self, query, projection=None):
        self.find_calls.append(query)
        wanted = (query.get("category_id") or {}).get("$in")
        return [d for d in self.docs if wanted is None or d["category_id"] in wanted]


class FakeProducts:
    def __init__(self, recent_ids=()):
        self.recent_ids = list(recent_ids)
        self.distinct_calls = []
        self.update_calls = []

    def distinct(self, key, query=None):
        self.distinct_calls.append((key, query))
        return self.recent_ids

    def update_one(self, flt, update, upsert=False):
        self.update_calls.append({"filter": flt, "update": update, "upsert": upsert})


class FakeDb:
    def __init__(self, category_ids=(), recent_ids=()):
        self.categories = FakeCategories(category_ids)
        self.products = FakeProducts(recent_ids)

    def __getitem__(self, name):
        return {"categories": self.categories, "products": self.products}[name]


def install_crawl_fakes(monkeypatch, db, ids_by_category, pages=1, fail=()):
    """Replace every network/DB function used by store(). Returns a recorder."""
    rec = SimpleNamespace(page_calls=[], fetched=[], saved=[])

    monkeypatch.setattr(sp, "get_db", lambda: db)
    monkeypatch.setattr(sp, "fetch_category_pages", lambda cat: pages)

    def fake_ids(cat, page):
        rec.page_calls.append((cat, page))
        return ids_by_category.get(cat, [])

    def fake_product(pid):
        rec.fetched.append(pid)
        return None if pid in fail else {"product_id": pid}

    monkeypatch.setattr(sp, "fetch_product_ids", fake_ids)
    monkeypatch.setattr(sp, "fetch_product", fake_product)
    monkeypatch.setattr(sp, "save_product", lambda details: rec.saved.append(dict(details)))
    return rec


# --------------------------------------------------------------------------
# find_all_keys
# --------------------------------------------------------------------------


def test_find_all_keys_searches_nested_dicts_and_lists():
    obj = {"a": {"x": 1}, "b": [{"x": 2}, {"c": {"x": 3}}], "x": 0}
    assert sorted(sp.find_all_keys(obj, "x")) == [0, 1, 2, 3]


def test_find_all_keys_returns_empty_list_when_missing_or_not_a_container():
    assert sp.find_all_keys({"a": 1}, "x") == []
    assert sp.find_all_keys("text", "x") == []
    assert sp.find_all_keys(None, "x") == []


# --------------------------------------------------------------------------
# fetch_category_pages
# --------------------------------------------------------------------------


def pager_response(**pager):
    return {"data": {"pager": pager}}


def test_category_pages_rounds_up(monkeypatch):
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: pager_response(total_items=41, total_slots=3))
    assert sp.fetch_category_pages(10) == 3      # ceil(41 / 20)


def test_category_pages_is_zero_without_data(monkeypatch):
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: None)
    assert sp.fetch_category_pages(10) == 0

    monkeypatch.setattr(sp, "get_json", lambda url, **kw: {"data": {}})
    assert sp.fetch_category_pages(10) == 0


def test_category_pages_is_zero_when_no_slots(monkeypatch):
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: pager_response(total_items=100, total_slots=0))
    assert sp.fetch_category_pages(10) == 0


def test_category_pages_is_capped_at_max_pages(monkeypatch):
    huge = sp.ITEMS_PER_PAGE * (sp.MAX_PAGES + 100)
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: pager_response(total_items=huge, total_slots=9))
    assert sp.fetch_category_pages(10) == sp.MAX_PAGES


def test_category_pages_requests_the_right_url(monkeypatch):
    seen = []
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: seen.append(url))
    sp.fetch_category_pages(9504)
    assert seen == [f"{sp.API}/discovery/api/v2/categories/9504/products"]


# --------------------------------------------------------------------------
# fetch_product_ids
# --------------------------------------------------------------------------

LISTING = {
    "first": {"widgets": ["ignored"]},
    "second": {
        "widgets": [
            {"data": {"id": 1}},
            {"data": {"id": 2}},
            {"data": {"title": "no id"}},
            {"data": "not a dict"},
        ]
    },
}


def test_product_ids_come_from_the_second_widgets_block(monkeypatch):
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: LISTING)
    assert sp.fetch_product_ids(10, 1) == [1, 2]


def test_product_ids_empty_when_response_is_missing_or_has_one_widgets_block(monkeypatch):
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: None)
    assert sp.fetch_product_ids(10, 1) == []

    monkeypatch.setattr(sp, "get_json", lambda url, **kw: {"only": {"widgets": []}})
    assert sp.fetch_product_ids(10, 1) == []


def test_product_ids_pass_the_page_number(monkeypatch):
    calls = []
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: calls.append((url, kw)))
    sp.fetch_product_ids(10, 7)
    assert calls == [(f"{sp.API}/discovery/api/v2/categories/10/products", {"page": 7})]


# --------------------------------------------------------------------------
# fetch_questions / fetch_product
# --------------------------------------------------------------------------


def test_fetch_questions_extracts_questions(monkeypatch):
    payload = {"data": {"questions": [{"text": "q?", "answers": [{"text": "a"}]}]}}
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: payload)
    assert sp.fetch_questions(5) == {"questions": [{"question": "q?", "answers": ["a"]}]}


def test_fetch_questions_is_empty_on_failure_or_missing_data(monkeypatch):
    for response in (None, {}, {"data": None}, {"data": {}}):
        monkeypatch.setattr(sp, "get_json", lambda url, r=response, **kw: r)
        assert sp.fetch_questions(5) == {"questions": []}


def test_fetch_questions_requests_page_one(monkeypatch):
    calls = []
    monkeypatch.setattr(sp, "get_json", lambda url, **kw: calls.append((url, kw)))
    sp.fetch_questions(5)
    assert calls == [(f"{sp.API}/v1/product/5/carousel-questions/", {"page": 1})]


def fake_api(product_payload):
    """get_json stand-in that answers the product and the questions endpoint."""

    def get_json(url, **kw):
        if "carousel-questions" in url:
            return {"data": {"questions": [{"text": "q?", "answers": []}]}}
        return product_payload

    return get_json


def test_fetch_product_merges_details_and_questions(monkeypatch):
    raw = {"data": {"product": {"id": 7, "title_en": "Phone"}}}
    monkeypatch.setattr(sp, "get_json", fake_api(raw))

    product = sp.fetch_product(7)
    assert product is not None
    assert product["product_id"] == 7
    assert product["product_title_en"] == "Phone"
    assert product["questions"] == [{"question": "q?", "answers": []}]


def test_fetch_product_returns_none_when_request_fails(monkeypatch):
    monkeypatch.setattr(sp, "get_json", fake_api(None))
    assert sp.fetch_product(7) is None


def test_fetch_product_returns_none_when_payload_has_no_id(monkeypatch):
    monkeypatch.setattr(sp, "get_json", fake_api({"data": {"product": {}}}))
    assert sp.fetch_product(7) is None


# --------------------------------------------------------------------------
# save_product
# --------------------------------------------------------------------------


def test_save_product_upserts_by_product_id_with_hash_and_timestamp(monkeypatch):
    db = FakeDb()
    monkeypatch.setattr(sp, "get_db", lambda: db)
    details = {"product_id": 7, "product_title_en": "Phone", "category_id": 10}

    before = datetime.now(UTC)
    sp.save_product(details)
    after = datetime.now(UTC)

    (call,) = db.products.update_calls
    assert call["filter"] == {"product_id": 7}
    assert call["upsert"] is True

    saved = call["update"]["$set"]
    assert saved["product_title_en"] == "Phone"
    assert saved["category_id"] == 10
    assert saved["content_hash"] == document_and_hash(details)[1]
    assert before <= saved["fetched_at"] <= after
    assert saved["fetched_at"].tzinfo is not None      # timezone-aware (UTC)


# --------------------------------------------------------------------------
# store()
# --------------------------------------------------------------------------


def test_store_saves_every_product_and_tags_it_with_its_category(monkeypatch):
    db = FakeDb(category_ids=[10, 20])
    rec = install_crawl_fakes(monkeypatch, db, {10: [1, 2], 20: [3]})

    stats = sp.store()

    assert stats == {"saved": 3, "failed": 0, "skipped": 0}
    assert {(d["product_id"], d["category_id"]) for d in rec.saved} == {(1, 10), (2, 10), (3, 20)}


def test_store_skips_recently_fetched_products(monkeypatch):
    db = FakeDb(category_ids=[10], recent_ids=[1])
    rec = install_crawl_fakes(monkeypatch, db, {10: [1, 2]})

    stats = sp.store()

    assert stats == {"saved": 1, "failed": 0, "skipped": 1}
    assert rec.fetched == [2]                  # product 1 was never requested


def test_store_counts_failed_products_and_does_not_save_them(monkeypatch):
    db = FakeDb(category_ids=[10])
    rec = install_crawl_fakes(monkeypatch, db, {10: [1, 2, 3]}, fail={2})

    stats = sp.store()

    assert stats == {"saved": 2, "failed": 1, "skipped": 0}
    assert [d["product_id"] for d in rec.saved] == [1, 3]


def test_store_filters_categories_and_coerces_ids_to_int(monkeypatch):
    db = FakeDb(category_ids=[10, 20])
    rec = install_crawl_fakes(monkeypatch, db, {10: [1], 20: [3]})

    sp.store(filters=["20"]) #type: ignore

    assert db.categories.find_calls == [{"category_id": {"$in": [20]}}]
    assert [d["product_id"] for d in rec.saved] == [3]


def test_store_without_filters_queries_all_categories(monkeypatch):
    db = FakeDb(category_ids=[10])
    install_crawl_fakes(monkeypatch, db, {})

    sp.store()
    sp.store(filters=[])

    assert db.categories.find_calls == [{}, {}]


def test_store_walks_every_page_of_every_category(monkeypatch):
    db = FakeDb(category_ids=[10, 20])
    rec = install_crawl_fakes(monkeypatch, db, {}, pages=2)

    sp.store()

    assert rec.page_calls == [(10, 1), (10, 2), (20, 1), (20, 2)]


def test_store_does_nothing_for_categories_without_pages(monkeypatch):
    db = FakeDb(category_ids=[10])
    rec = install_crawl_fakes(monkeypatch, db, {10: [1]}, pages=0)

    assert sp.store() == {"saved": 0, "failed": 0, "skipped": 0}
    assert rec.page_calls == []


def test_store_default_recency_window_uses_config(monkeypatch):
    db = FakeDb(category_ids=[10])
    install_crawl_fakes(monkeypatch, db, {})

    before = datetime.now(UTC)
    sp.store()
    after = datetime.now(UTC)

    ((key, query),) = db.products.distinct_calls
    cutoff = query["fetched_at"]["$gte"]
    window = timedelta(hours=REFETCH_AFTER_HOURS)
    assert key == "product_id"
    assert before - window <= cutoff <= after - window


def test_store_custom_window_overrides_the_default(monkeypatch):
    db = FakeDb(category_ids=[10])
    install_crawl_fakes(monkeypatch, db, {})

    before = datetime.now(UTC)
    sp.store(max_age_hours=2)
    after = datetime.now(UTC)

    cutoff = db.products.distinct_calls[0][1]["fetched_at"]["$gte"]
    assert before - timedelta(hours=2) <= cutoff <= after - timedelta(hours=2)


def test_store_with_zero_window_refetches_everything(monkeypatch):
    db = FakeDb(category_ids=[10], recent_ids=[1, 2])
    rec = install_crawl_fakes(monkeypatch, db, {10: [1, 2]})

    stats = sp.store(max_age_hours=0)

    assert db.products.distinct_calls == []    # the recency lookup is skipped entirely
    assert stats == {"saved": 2, "failed": 0, "skipped": 0}
    assert rec.fetched == [1, 2]