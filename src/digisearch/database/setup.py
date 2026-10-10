from pymongo.errors import ServerSelectionTimeoutError

from digisearch.database.client import get_db_client, get_db


def ping():
    try:
        get_db_client().admin.command("ping")
    except ServerSelectionTimeoutError as e:
        raise SystemExit(f"Cannot reach MongoDB: {e}")


def setup_categories():
    coll = get_db()["categories"]
    coll.create_index("category_id", unique=True)


def setup_products():
    coll = get_db()["products"]
    coll.create_index("product_id", unique=True)


def setup():
    ping()
    setup_categories()
    setup_products()


if __name__ == "__main__":
    setup()