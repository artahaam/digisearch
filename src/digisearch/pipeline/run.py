import argparse
import logging

from digisearch.logging_config import setup_logging
from digisearch.pipeline.store_categories import store_categories
from digisearch.pipeline.store_products import store
from digisearch.services.get_categories import fetch_categories_dict

log = logging.getLogger(__name__)


def refresh_categories() -> int:
    n = store_categories(fetch_categories_dict())
    log.info("categories written: %d", n)
    return n


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("stage", choices=["categories", "products"])
    p.add_argument("--category", type=int, nargs="*", help="limit products to these category ids")
    args = p.parse_args()

    setup_logging()
    if args.stage == "categories":
        refresh_categories()
    else:
        store(args.category)


if __name__ == "__main__":
    main()