from os import walk
import json
import logging
from digisearch.paths import RAW_DIR, CANONICAL_DIR, LOG_DIR


logger = logging.getLogger('list_products')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / 'process.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


CATEGORY_DIR = RAW_DIR / "category"


def count_categories() -> int:
    """Cheap count of crawled categories, useful as a progress denominator."""
    if not CATEGORY_DIR.exists():
        return 0
    return sum(1 for p in CATEGORY_DIR.iterdir() if p.is_dir())


def build_product_list(progress_callback=None) -> dict:

    logger.info("Listing products started.")

    if not CATEGORY_DIR.exists():
        logger.warning(f"{CATEGORY_DIR} does not exist yet; nothing crawled.")
        return {"categories": 0, "products": 0}

    categories = sorted(p.name for p in CATEGORY_DIR.iterdir() if p.is_dir())
    total_categories = len(categories)
    products = []

    for i, category in enumerate(categories):
        cat_dir = CATEGORY_DIR / category
        product_dir = cat_dir / "product"

        if product_dir.exists():
            for product_path in product_dir.iterdir():
                if not product_path.is_dir():
                    continue

                product_id = product_path.name
                questions_path = product_path / "questions.json"
                details_path = product_path / "details.json"
                comments_path = product_path / "comments.json"

                if not details_path.exists():
                    logger.info(f"skipping product {product_id} (no details.json)")
                    continue

                products.append({
                    "product": {
                        "id": product_id,
                        "questions_path": str(questions_path),
                        "details_path": str(details_path),
                        "comments_path": str(comments_path),
                        "category": category,
                    },
                })

        if progress_callback:
            progress_callback(i + 1, total_categories, category)

    with open(CANONICAL_DIR / "product_list.json", "w", encoding="utf-8") as file:
        json.dump(products, file, indent=4)

    logger.info(f"{len(products)} products listed at {CANONICAL_DIR / 'product_list.json'}")

    return {"categories": total_categories, "products": len(products)}


if __name__ == "__main__":
    build_product_list()
