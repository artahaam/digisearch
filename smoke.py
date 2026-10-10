from digisearch.services.get_categories import fetch_categories_dict
from digisearch.pipeline.store_categories import store_categories

cats = fetch_categories_dict()
print(len(cats), "categories")
store_categories(cats)