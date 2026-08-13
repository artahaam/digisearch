import requests
import csv
import argparse


def main():

    parser = argparse.ArgumentParser(description="filtering categories.")
    parser.add_argument(
        '--filters',
        type=str,
        required=False,
        default="",
        help='Comma-separated list of filter keywords, e.g. "clothes,men,jeans"'
    )
    parser.add_argument(
        '--ignores',
        type=str,
        required=False,
        default="",
        help='Comma-separated list of filter keywords, e.g. "clothes,men,jeans"'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=False,
        default="categories.csv",
        help='Output CSV file name, e.g. "clothes_categories.csv"'
    )
    args = parser.parse_args()

    filters = [f.strip().lower() for f in args.filters.split(',') if args.filters]
    ignores = [i.strip().lower() for i in args.ignores.split(',') if args.ignores]

    
    output_file_name = args.output


    url = "https://api.digikala.com/v1/dictionaries/?hashes%5B0%5D=854520e5da5b50175e401c36b8002ecc&hashes%5B1%5D=0b848e3d0eda54da5e1235d2d96b863c&hashes%5B2%5D=4ee2c70608fae0b62a7aefe875e714e1&hashes%5B3%5D=ebc1db8a4bada2b70d1aa833850c7318&hashes%5B4%5D=ec2077e41fa92a963fd7b54c80c84453&hashes%5B5%5D=9c48d184680ce36796b22d7eed2bd1ae&hashes%5B6%5D=2ea0f9b20be91246b5165aba96fc4493&hashes%5B7%5D=b0e7555f1d9f7820ec58302d44c3b545&hashes%5B8%5D=8f518757777a2bb85a316b5fd36fbd24&types%5B0%5D=states&types%5B1%5D=cities&types%5B2%5D=user_jobs&types%5B3%5D=mega_menu&types%5B4%5D=universal&types%5B5%5D=category_tree&types%5B6%5D=districts&types%5B7%5D=seo_content&types%5B8%5D=superapp_services"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
    }

    response = requests.get(url, headers=headers, timeout=20)
    category_dict = response.json()["data"][5]
    categories = category_dict["data"]["data"]



    with open(output_file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows([["id", "title_fa", "title_en", "code", "parent_id"]])

        for cat in categories:

            category = cat["category"] 
            parent_id = cat.get("parent_id", 0)
            category_id = category["id"]
            title_fa = category["title_fa"]
            title_en = category["title_en"]
            code = category["code"]
            codes = code.split('-')

            ignore_flag = False

            if ignores:
                for ignore in ignores:
                    if ignore.lower() in codes:
                        ignore_flag = True
                        break
            else:
                pass

            if ignore_flag:
                continue

            elif filters:
                for filter in filters:
                    if filter.lower() in codes:
                        writer.writerow([category_id, title_fa, title_en, code, parent_id])
                    else:
                        continue

            else:
                writer.writerow([category_id, title_fa, title_en, code, parent_id])


if __name__ == "__main__":
    main()