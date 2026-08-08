import requests
from bs4 import BeautifulSoup
import requests
import csv

url = "https://api.digikala.com/v1/widget-factory/touchpoint-group/7/"
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
json_response = response.json()
items = json_response["data"]["items"]


with open("categories.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows([["title", "url"]])


    for item in items:

        url = item["link"]["url"]
        title = item["title"]

        writer.writerow([title, url])
        
file.close()
