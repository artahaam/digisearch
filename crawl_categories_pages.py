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
    print("Started", datetime.now().strftime("%H:%M:%S"))
    print("Reading " + csv_file.name)

    for row in reader:

        cat_id = row["id"]

        try:
            
            base_page = requests.get(f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products/").json()

        except (requests.exceptions.ProxyError, requests.exceptions.SSLError) as e:

            print(e)
            print("Aborted due to connectino error.")

            continue

        try:

            pager = find_all_keys(base_page, "pager")[0]

        except:

            print("Invalid response")
            print(f"URL: {base_page}")
            print("Skipping to the next category")

            continue


        current_page = pager["current_page"]
        total_items = pager["total_items"]
        total_pages = pager["total_pages"]
        total_slots = pager["total_slots"]

        approximate_page_numbers = total_items // 20 + 1

        print("="*20)
        print("Category id: " + cat_id)
        print("Approximate page numbers: " + str(approximate_page_numbers))

        for pn in range(1, approximate_page_numbers + 1):

            print(f"Current page: {pn}")
            
            if total_slots != 0:

                try:
                    data = requests.get(f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products?page={pn}").json()


                    category = cat_id
                    timestamp = datetime.now().strftime("%Y-%m-%d")
                    directory = os.path.join("category_page_json", category, timestamp)
                    os.makedirs(directory, exist_ok=True)
                    
                    with open(f"{directory}/page_{pn}.json", "w", encoding="utf-8") as json_file:
                        json.dump(data, json_file, indent=4, ensure_ascii=False)
                    json_file.close()


                    widget = find_all_keys(data, "widgets")[1]
                    
                    items = find_all_keys(widget, "data")

                    print("*** Started to store each product page ***")
                                        
                    for item in items:

                        print("*"*20)
                        try:
                            product_id = item["id"]
                        except KeyError:
                            print(f"Skipping item without id: {item}")
                            continue

                        url = f"https://api.digikala.com/v2/product/{product_id}/"

                        print(f"Trying to save {product_id}" + f" From {url}")

                        try:
                            product = requests.get(url).json()
                        except requests.exceptions.ProxyError as e:
                            print(e)
                            print("Aborted due to connection")
                            continue

                        directory = os.path.join("products", category)
                        os.makedirs(directory, exist_ok=True)

                        with open(f"{directory}/{product_id}.json", "w", encoding="utf-8") as json_file:
                            json.dump(product, json_file, indent=4, ensure_ascii=False)
                        json_file.close()

                        print("Product saved at " +f"{directory}/{product_id}.json", "---", datetime.now().strftime("%H:%M:%S"))
                        print("*"*20 + "\n\n")

                    print('Saved at ' + f"{directory}/page_{pn}.json", "---", datetime.now().strftime("%Y-%m-%d"))

                except:
                    continue

            else:
                break


csv_file.close()
