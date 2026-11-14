import pytest
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError

from digisearch import config
from digisearch.database import setup as db_setup
from digisearch.database.client import get_db, get_db_client

pytestmark = pytest.mark.integration


def test_setup_creates_unique_indexes_on_a_fresh_database():
    assert "test" in config.MONGO_DB
    get_db_client().drop_database(config.MONGO_DB)

    db_setup.setup()

    products = get_db()["products"].index_information()
    categories = get_db()["categories"].index_information()
    assert products["product_id_1"]["unique"] is True
    assert "fetched_at_1" in products
    assert categories["category_id_1"]["unique"] is True


def test_setup_is_idempotent():
    db_setup.setup()
    first = get_db()["products"].index_information()

    db_setup.setup()
    second = get_db()["products"].index_information()

    assert first == second


def test_duplicate_product_ids_are_rejected():
    products = get_db()["products"]
    products.insert_one({"product_id": 1})

    with pytest.raises(DuplicateKeyError):
        products.insert_one({"product_id": 1})


def test_ping_exits_with_a_clear_message_when_mongo_is_down(monkeypatch):
    class DownClient:
        class admin:
            @staticmethod
            def command(name):
                raise ServerSelectionTimeoutError("no server")

    monkeypatch.setattr(db_setup, "get_db_client", lambda: DownClient)

    with pytest.raises(SystemExit) as exc:
        db_setup.ping()
    assert "Cannot reach MongoDB" in str(exc.value)
