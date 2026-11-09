import logging
from datetime import datetime, timedelta, timezone
from math import ceil

from digisearch.database.client import get_db
from digisearch.services.canonicalize import extract_details_data, extract_questions_data
from digisearch.services.http_client import get_json
from digisearch.config import REFETCH_AFTER_HOURS
from digisearch.services.fingerprint import document_and_hash

log = logging.getLogger(__name__)

API = "https://api.digikala.com"
ITEMS_PER_PAGE = 20
MAX_PAGES = 500


def find_all_keys(obj, target_key) -> list:
    results = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == target_key:
                results.append(value)
            results.extend(find_all_keys(value, target_key))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_all_keys(item, target_key))
    return results


def fetch_category_pages(cat_id: int) -> int:
    data = get_json(f"{API}/discovery/api/v2/categories/{cat_id}/products")
    pagers = find_all_keys(data, "pager") if data else []
    if not pagers:
        return 0
    pager = pagers[0]
    if pager.get("total_slots") == 0:
        return 0
    return min(ceil(pager.get("total_items", 0) / ITEMS_PER_PAGE), MAX_PAGES)


def fetch_product_ids(cat_id: int, page: int) -> list[int]:
    data = get_json(f"{API}/discovery/api/v2/categories/{cat_id}/products", page=page)
    if not data:
        return []
    widgets = find_all_keys(data, "widgets")
    if len(widgets) < 2:
        return []
    items = find_all_keys(widgets[1], "data")
    return [i["id"] for i in items if isinstance(i, dict) and "id" in i]


def fetch_questions(product_id: int) -> dict:
    data = get_json(f"{API}/v1/product/{product_id}/carousel-questions/", page=1)
    payload = (data or {}).get("data") or {}
    return extract_questions_data(payload.get("questions"))


def fetch_product(product_id: int) -> dict | None:
    raw = get_json(f"{API}/v2/product/{product_id}/")
    if raw is None:
        return None
    details = extract_details_data(raw)
    if details.get("product_id") is None:
        return None
    details.update(fetch_questions(product_id))
    return details


def save_product(details: dict) -> None:
    _, content_hash = document_and_hash(details)
    get_db()["products"].update_one(
        {"product_id": details["product_id"]},
        {"$set": {**details, "content_hash": content_hash,
                  "fetched_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def store(filters: list[int] | None = None,
          max_age_hours: float | None = REFETCH_AFTER_HOURS) -> dict:   
    filters = [int(i) for i in filters] if filters else None
    db = get_db()
    query = {"category_id": {"$in": filters}} if filters else {}
    category_ids = [c["category_id"] for c in db["categories"].find(query, {"category_id": 1})]

    recent: set[int] = set()
    if max_age_hours:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        recent = set(db["products"].distinct("product_id", {"fetched_at": {"$gte": cutoff}}))

    stats = {"saved": 0, "failed": 0, "skipped": 0}
    for cat_id in category_ids:
        pages = fetch_category_pages(cat_id)
        log.info("category %s: %d pages", cat_id, pages)
        for page in range(1, pages + 1):
            for product_id in fetch_product_ids(cat_id, page):
                if product_id in recent:
                    stats["skipped"] += 1
                    continue
                details = fetch_product(product_id)
                if details is None:
                    stats["failed"] += 1
                    log.warning("product %s failed, skipping", product_id)
                    continue
                details["category_id"] = cat_id
                save_product(details)
                stats["saved"] += 1
    log.info("done: %s", stats)
    return stats