import requests
import json
import csv
import os
from datetime import datetime


def find_all_keys(obj, target_key):
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



with open("clothes_category.csv", "r", encoding="utf-8") as csv_file:

    reader = csv.DictReader(csv_file)

    print(csv_file.name + " opened")

    for row in reader:

        cat_id = row["id"]
        base_page = requests.get(f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products").json()
        pager = find_all_keys(base_page, "pager")[0]

        current_page = pager["current_page"]
        total_items = pager["total_items"]
        total_pages = pager["total_pages"]
        total_slots = pager["total_slots"]

        approximate_page_numbers = total_items // 20 + 1

        print("Category id: " + cat_id)
        print("Approximate page numbers: " + str(approximate_page_numbers))

        for pn in range(1, approximate_page_numbers + 1):

            if total_slots != 0:
                data = requests.get(f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products?page={pn}").json()

                category = cat_id
                timestamp = datetime.now().strftime("%Y-%m-%d")
                directory = os.path.join("category_page_json", category, timestamp)
                os.makedirs(directory, exist_ok=True)
                
                with open(f"{directory}/page_{pn}.json", "w", encoding="utf-8") as json_file:
                    json.dump(data, json_file, indent=4, ensure_ascii=False)
                json_file.close()

                print('Saved at ' + f"{directory}/page_{pn}.json")

            else:
                break


csv_file.close()
    