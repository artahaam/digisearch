import requests
from bs4 import BeautifulSoup
import requests
import csv

base_url = "https://api.digikala.com/v1/categories/"

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


with open("categories.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    with open("categories_api.csv", "w", encoding="utf-8") as api:
        writer = csv.writer(api)
        writer.writerows([["title", "api-url"]])
        for row in reader:

            url = row["url"]
            slug = url.split('/')[-2]
            api_url = base_url + slug + '/'
            writer.writerow([slug, api_url])

    api.close()
file.close()
