from pymongo import UpdateOne

from digisearch.database.client import get_client
from digisearch.ingest.categories import fetch_categories_dict

client = get_client()
categories = client["digisearch"]["categories"]

def store_categories(categories_dict: dict):
    if not categories_dict:
        return

    ops = [
        UpdateOne({"id": cat["id"]}, {"$set": cat}, upsert=True)
        for cat in categories_dict.values()
    ]
    
    result = categories.bulk_write(ops, ordered=False)
