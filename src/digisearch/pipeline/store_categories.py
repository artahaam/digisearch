from pymongo import UpdateOne

from digisearch.database.client import get_db


def store_categories(categories_dict: dict) -> int:
    if not categories_dict:
        return 0

    db_categories = get_db()["categories"]

    ops = [
        UpdateOne({"category_id": cat["id"]}, {"$set": cat}, upsert=True)
        for cat in categories_dict.values()
    ]

    result = db_categories.bulk_write(ops, ordered=False)
    return result.upserted_count + result.modified_count