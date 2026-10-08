from pymongo import UpdateOne

from digisearch.database.client import get_client

client = get_client()
db_categories = client["digisearch"]["categories"]

def store_categories(categories_dict: dict):
    if not categories_dict:
        return

    ops = [
        UpdateOne({"category_id": cat["id"]}, {"$set": cat}, upsert=True)
        for cat in categories_dict.values()
    ]
    
    result = db_categories.bulk_write(ops, ordered=False)
