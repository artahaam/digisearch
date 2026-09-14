"""Shared Digikala category dictionary fetch.

Kept separate from ingest_page.py (which is a full Streamlit script with
its own top-level UI code) so any page can import just the fetch function
without triggering that script's side effects.
"""
import requests


CATEGORY_TREE_URL = (
    "https://api.digikala.com/v1/dictionaries/"
    "?hashes%5B0%5D=854520e5da5b50175e401c36b8002ecc"
    "&hashes%5B1%5D=0b848e3d0eda54da5e1235d2d96b863c"
    "&hashes%5B2%5D=4ee2c70608fae0b62a7aefe875e714e1"
    "&hashes%5B3%5D=ebc1db8a4bada2b70d1aa833850c7318"
    "&hashes%5B4%5D=ec2077e41fa92a963fd7b54c80c84453"
    "&hashes%5B5%5D=9c48d184680ce36796b22d7eed2bd1ae"
    "&hashes%5B6%5D=2ea0f9b20be91246b5165aba96fc4493"
    "&hashes%5B7%5D=b0e7555f1d9f7820ec58302d44c3b545"
    "&hashes%5B8%5D=8f518757777a2bb85a316b5fd36fbd24"
    "&types%5B0%5D=states&types%5B1%5D=cities&types%5B2%5D=user_jobs"
    "&types%5B3%5D=mega_menu&types%5B4%5D=universal&types%5B5%5D=category_tree"
    "&types%5B6%5D=districts&types%5B7%5D=seo_content&types%5B8%5D=superapp_services"
)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/139.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}


def fetch_categories_dict(timeout: int = 20) -> dict:
    """Fetch the full Digikala category tree, keyed by category id.

    Raises requests.exceptions.RequestException on network failure, and
    (IndexError, KeyError, TypeError) if the response shape is unexpected —
    callers should handle both and degrade gracefully rather than crash.
    """
    response = requests.get(CATEGORY_TREE_URL, headers=_HEADERS, timeout=timeout)
    response.raise_for_status()

    category_dict = response.json()["data"][5]
    _categories = category_dict["data"]["data"]

    categories_dict = {}
    for cat in _categories:
        category = cat["category"]
        category_id = category["id"]
        if category_id not in categories_dict:
            categories_dict[category_id] = cat
    return categories_dict