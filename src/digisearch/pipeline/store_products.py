import requests
from digisearch.pipeline.canonicalize import extract_questions_data, extract_details_data

from digisearch.database.client import get_client

client = get_client()


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



def store(filters: list[int] = []) -> None:

    db_categories = client["digisearch"]["categories"]
    db_products = client["digisearch"]["products"]

    query = {}
    if filters:
        query["id"] = {"$in": filters}

    for cat in db_categories.find(query):
        cat_id = cat.get("id")
        cat_title = cat.get("title_en") or cat.get("title_fa", "-")
        try:
            category_page_url = f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products"
            category_page_json = requests.get(category_page_url).json()

        except (requests.exceptions.ProxyError, requests.exceptions.SSLError) as e:
            continue

        try:
            pager = find_all_keys(category_page_json, "pager")[0]

        except (IndexError, KeyError, TypeError):
            continue

        total_items = pager["total_items"]
        total_slots = pager["total_slots"]

        approximate_page_numbers = total_items // 20 + 1

        if approximate_page_numbers > 500:
            approximate_page_numbers = 500


        for category_pn in range(approximate_page_numbers + 1):

            if total_slots == 0:
                break

            try:
                data = requests.get(
                    f"https://api.digikala.com/discovery/api/v2/categories/{cat_id}/products?page={category_pn}"
                ).json()
            except requests.exceptions.RequestException as e:
                continue

            try:
                widget = find_all_keys(data, "widgets")[1]
                items = find_all_keys(widget, "data")
            except (IndexError, KeyError, TypeError):
                continue

            # products storage 
            for item in items:

                try:
                    product_id = item["id"]
                except KeyError:
                    continue
                
                product_url = f"https://api.digikala.com/v2/product/{product_id}/"

                try:
                    product = requests.get(product_url).json()
                except requests.exceptions.RequestException as e:
                    continue
                
                # comments storage 
                comments_page_url = f"https://api.digikala.com/v1/rate-review/products/{product_id}/"
                comments_page_json = requests.get(comments_page_url).json()
                try:
                    pager = find_all_keys(comments_page_json, "pager")[0]
                except (IndexError, KeyError, TypeError):
                    continue
                total_comments = pager["total_items"]
                total_pages = pager["total_pages"]
                all_comments = []
                for comments_pn in range(1, total_pages + 1):
                    try:
                        data = requests.get(
                            f"https://api.digikala.com/v1/rate-review/products/{product_id}/?page={comments_pn}"
                        ).json()
                    except requests.exceptions.RequestException as e:
                        continue
                    current_page_comments = find_all_keys(data, "data")
                    all_comments.extend(current_page_comments)

                # questions storage 
                question_page_url = f"https://api.digikala.com/v1/product/{product_id}/carousel-questions/"
                question_page_json = requests.get(question_page_url).json()
                try:
                    pager = find_all_keys(question_page_json, "pager")[0]
                except (IndexError, KeyError, TypeError):
                    continue
                total_questions = pager["total_items"]
                total_pages = pager["total_pages"]
                all_questions = []

                for question_pn in range(1, total_pages + 1):
                    try:
                        data = requests.get(
                            f"https://api.digikala.com/v1/product/{product_id}/carousel-questions/?page={question_pn}"
                        ).json()
                    except requests.exceptions.RequestException as e:
                        continue
                    current_page_questinos = find_all_keys(data, "data")
                    all_questions.extend(current_page_questinos)

                details = extract_details_data(product)
                questions = extract_questions_data(all_questions[0])
                details.update(questions.items())

                #store canonical product in products collection
                db_products.insert_one(details)
