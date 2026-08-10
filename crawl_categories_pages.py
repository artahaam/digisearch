import requests
import json
import csv
import os
from pathlib import Path
import logging





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


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CATEGORY_DIR = RAW_DIR / "category"
CHECKPOINT_DIR = DATA_DIR / "checkpoints"
LOG_DIR = BASE_DIR / "logs"

for directory in (RAW_DIR, CATEGORY_DIR, CHECKPOINT_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)




logger = logging.getLogger('crawler')
logger.setLevel(logging.DEBUG)  

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_DIR / 'crawler.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)




logger.debug("Directories set up finished.")


with open("clothes_category.csv", "r", encoding="utf-8") as csv_file:

    logger.debug("clothes_category.csv opened.")
    reader = csv.DictReader(csv_file)

    logger.info("reading file started")


    for row in reader:

        cat_id = row["id"]

        try:
            base_page_url = f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products/"
            base_page_json = requests.get(base_page_url).json()
            logger.info(f"categoy {cat_id} fetched from {base_page_url}")

        except (requests.exceptions.ProxyError, requests.exceptions.SSLError) as e:

            logger.error(e)
            logger.info("skipped due to connectino error")

            continue

        try:

            pager = find_all_keys(base_page_json, "pager")[0]

        except:

            logger.error("invalid response or no pager found")
            logger.info(f"URL: {base_page_json}")
            logger.info("skipping to the next category")

            continue

        
        current_page = pager["current_page"]
        total_items = pager["total_items"]
        total_pages = pager["total_pages"]
        total_slots = pager["total_slots"]

        approximate_page_numbers = total_items // 20 + 1

        logger.info("category id: " + cat_id + " fetched")
        logger.info("approximate page numbers: " + str(approximate_page_numbers))

        for pn in range(1, approximate_page_numbers + 1):


            if total_slots != 0:

                try:

                    data = requests.get(f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products?page={pn}").json()

                except requests.exceptions.RequestException as e:
                    logger.error(e)
                    logger.info("skipping the current page")
                    continue

                category_dir = CATEGORY_DIR / f"{cat_id}" 
                category_dir.mkdir(parents=True, exist_ok=True)

                page_dir = CATEGORY_DIR / f"{cat_id}" / "page"
                page_dir.mkdir(parents=True, exist_ok=True)

                product_dir = (CATEGORY_DIR / f"{cat_id}" / "product")
                product_dir.mkdir(parents=True, exist_ok=True)


                with open(f"{CATEGORY_DIR}/{cat_id}/page/page_{pn}.json", "w", encoding="utf-8") as json_file:
                    json.dump(data, json_file, indent=4, ensure_ascii=False)
                json_file.close()

                try:
                    widget = find_all_keys(data, "widgets")[1]    
                    items = find_all_keys(widget, "data")
                except:

                    logger.error("invalid response or data unavailable")
                    logger.info("could not find 'widget' in response")
                    logger.info("skipping this page")
                    continue


                logger.info(f"fetching products from page {pn} with {total_slots} slots started")

                                    
                for item in items:

                    try:
                        product_id = item["id"]
                    except KeyError:
                        logger.info(f"skipping item without id: {item}")
                        continue

                    url = f"https://api.digikala.com/v2/product/{product_id}/"


                    try:
                        product = requests.get(url).json()
                        logger.debug(f"product {product_id} fetched" + f" from {url}")
                    except requests.exceptions.ProxyError as e:
                        logger.error(e)
                        logger.info("aborted due to connection error")
                        continue

                    current_product_dir = f"{CATEGORY_DIR}/{cat_id}/product/{product_id}.json" 

                    with open(current_product_dir, "w", encoding="utf-8") as json_file:

                        json.dump(product, json_file, indent=4, ensure_ascii=False)
                        logger.debug(f"json data dumped to {json_file.name}")

                    json_file.close()
                    logger.debug(f"{json_file.name} closed")

                    
                    logger.info(f"product {product_id} saved at " + f"{current_product_dir}")

                logger.info(f'category page_{pn} saved at ' + f"{page_dir}/page_{pn}.json")


            else:
                logger.info("no more products to fetch")
                break


csv_file.close()
