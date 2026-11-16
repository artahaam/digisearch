import pytest

from digisearch import config
from digisearch.database.client import get_db
from digisearch.pipeline.store_embeddings import embed_pending
from digisearch.pipeline.sync_qdrant import prune_orphans, qdrant_point_ids

pytestmark = pytest.mark.integration


def point_ids(qdrant):
    points, _ = qdrant.scroll(
        collection_name=config.QDRANT_COLLECTION, limit=1000, with_payload=False, with_vectors=False
    )
    return sorted(p.id for p in points)


@pytest.fixture
def five_embedded(add_product, fake_model):
    for pid in range(1, 6):
        add_product(pid)
    embed_pending()


def test_prune_deletes_points_whose_product_is_gone(five_embedded, qdrant):
    assert "test" in config.MONGO_DB
    get_db()["products"].delete_one({"product_id": 2})

    stats = prune_orphans()

    assert stats["mongo"] == 4
    assert stats["qdrant"] == 5
    assert stats["orphans"] == 1
    assert stats["deleted"] == 1
    assert stats["mongo_db"] == config.MONGO_DB
    assert point_ids(qdrant) == [1, 3, 4, 5]


def test_dry_run_reports_but_deletes_nothing(five_embedded, qdrant):
    assert "test" in config.MONGO_DB
    
    get_db()["products"].delete_one({"product_id": 2})

    stats = prune_orphans(dry_run=True)

    assert stats["orphans"] == 1
    assert stats["deleted"] == 0
    assert point_ids(qdrant) == [1, 2, 3, 4, 5]


def test_prune_deletes_in_batches(five_embedded, qdrant):
    get_db()["products"].delete_many({"product_id": {"$in": [1, 2, 3]}})

    stats = prune_orphans(batch_size=1)

    assert stats["deleted"] == 3
    assert point_ids(qdrant) == [4, 5]


def test_prune_refuses_when_mongo_is_empty_unless_forced(five_embedded, qdrant):
    get_db()["products"].delete_many({})

    with pytest.raises(RuntimeError, match="refusing to prune"):
        prune_orphans()
    assert point_ids(qdrant) == [1, 2, 3, 4, 5]               # nothing was touched

    assert prune_orphans(force=True)["deleted"] == 5
    assert point_ids(qdrant) == []


def test_products_not_yet_embedded_are_reported_as_missing(five_embedded, add_product):
    add_product(6)                                            # stored but never embedded

    stats = prune_orphans()

    assert stats["missing_in_qdrant"] == 1
    assert stats["orphans"] == 0


def test_point_ids_are_read_across_scroll_pages(five_embedded):
    assert sorted(qdrant_point_ids(page_size=2)) == [1, 2, 3, 4, 5]
