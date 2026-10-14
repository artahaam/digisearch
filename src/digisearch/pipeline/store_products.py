import logging
from datetime import datetime, timezone
from math import ceil

from digisearch.database.client import get_db
from digisearch.services.canonicalize import extract_details_data, extract_questions_data
from digisearch.services.http_client import get_json

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
    get_db()["products"].update_one(
        {"product_id": details["product_id"]},
        {"$set": {**details, "fetched_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def store(filters: list[int] | None = None) -> dict:
    db = get_db()
    query = {"id": {"$in": filters}} if filters else {}
    category_ids = [c["id"] for c in db["categories"].find(query, {"id": 1})]

    stats = {"saved": 0, "failed": 0}
    for cat_id in category_ids:
        pages = fetch_category_pages(cat_id)
        log.info("category %s: %d pages", cat_id, pages)
        for page in range(1, pages + 1):
            for product_id in fetch_product_ids(cat_id, page):
                details = fetch_product(product_id)
                if details is None:
                    stats["failed"] += 1
                    log.warning("product %s failed, skipping", product_id)
                    continue
                details.update({"category_id":cat_id})
                save_product(details)
                stats["saved"] += 1
    log.info("done: %s", stats)
    return stats