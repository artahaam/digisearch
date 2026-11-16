import pytest

from digisearch import config
from digisearch.database.client import get_db
from digisearch.pipeline.store_embeddings import embed_pending
from digisearch.pipeline.store_products import save_product
from digisearch.services.fingerprint import document_and_hash

pytestmark = pytest.mark.integration


def point_ids(qdrant):
    points, _ = qdrant.scroll(
        collection_name=config.QDRANT_COLLECTION, limit=1000, with_payload=False, with_vectors=False
    )
    return sorted(p.id for p in points)


def test_new_products_are_embedded_and_marked(add_product, fake_model, qdrant):
    for pid in (1, 2, 3):
        add_product(pid)

    stats = embed_pending(batch_size=2)

    assert stats == {"embedded": 3, "skipped": 0, "failed": 0}
    assert point_ids(qdrant) == [1, 2, 3]
    doc = get_db()["products"].find_one({"product_id": 1})
    assert doc is not None
    assert doc["embedded_hash"] == doc["content_hash"]
    assert "embedded_at" in doc


def test_qdrant_payload_contains_the_searchable_fields(add_product, fake_model, qdrant):
    add_product(
        1,
        product_title_fa="گوشی",
        brand_title_fa="برند",
        product_categories=["Mobile", None, "Phones"],
        product_price=500,
    )

    embed_pending()

    (point,) = qdrant.retrieve(collection_name=config.QDRANT_COLLECTION, ids=[1], with_payload=True)
    payload = point.payload
    assert payload is not None
    assert payload["product_id"] == 1
    assert payload["title_en"] == "Product 1"
    assert payload["title_fa"] == "گوشی"
    assert payload["brand_en"] == "Acme"
    assert payload["brand_fa"] == "برند"
    assert payload["categories"] == ["Mobile", "Phones"]      # None entries removed
    assert payload["price"] == 500


def test_second_run_embeds_nothing(add_product, fake_model, qdrant):
    for pid in (1, 2, 3):
        add_product(pid)
    embed_pending(batch_size=2)
    calls_after_first_run = len(fake_model.calls)

    stats = embed_pending(batch_size=2)

    assert stats == {"embedded": 0, "skipped": 0, "failed": 0}
    assert len(fake_model.calls) == calls_after_first_run     # the model was not even called
    assert point_ids(qdrant) == [1, 2, 3]


def test_changed_text_is_re_embedded(add_product, fake_model):
    for pid in (1, 2, 3):
        add_product(pid)
    embed_pending()

    add_product(2, product_title_en="Renamed")
    stats = embed_pending()

    assert stats["embedded"] == 1
    assert len(fake_model.calls[-1]) == 1
    assert "Renamed" in fake_model.calls[-1][0]


def test_price_only_change_does_not_trigger_re_embedding(add_product, fake_model):
    add_product(1, product_price=1000)
    embed_pending()

    add_product(1, product_price=999)

    assert embed_pending()["embedded"] == 0


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN GAP: a price-only change does not re-embed, so the price stored in "
    "the Qdrant payload goes stale. Remove this marker once the payload is refreshed.",
)
def test_price_change_is_reflected_in_the_qdrant_payload(add_product, fake_model, qdrant):
    add_product(1, product_price=1000)
    embed_pending()
    add_product(1, product_price=999)
    embed_pending()

    (point,) = qdrant.retrieve(collection_name=config.QDRANT_COLLECTION, ids=[1], with_payload=True)
    assert point.payload is not None
    assert point.payload["price"] == 999


def test_force_re_embeds_everything(add_product, fake_model):
    for pid in (1, 2, 3):
        add_product(pid)
    embed_pending()

    assert embed_pending(force=True)["embedded"] == 3


def test_limit_caps_the_number_of_products_per_run(add_product, fake_model):
    for pid in (1, 2, 3):
        add_product(pid)

    assert embed_pending(limit=2)["embedded"] == 2
    assert embed_pending()["embedded"] == 1


def test_failed_batch_stays_pending_and_is_retried(add_product, fake_model, qdrant):
    for pid in (1, 2, 3):
        add_product(pid)
    fake_model.fail_times = 1

    stats = embed_pending()

    assert stats == {"embedded": 0, "skipped": 0, "failed": 3}
    assert point_ids(qdrant) == []
    assert get_db()["products"].count_documents({"embedded_hash": {"$exists": True}}) == 0

    assert embed_pending()["embedded"] == 3                   # next run picks them up again


def test_products_with_an_empty_document_are_skipped(fake_model, qdrant):
    save_product({"product_id": 9})
    assert document_and_hash({"product_id": 9})[0] == ""

    stats = embed_pending()

    assert stats == {"embedded": 0, "skipped": 1, "failed": 0}
    assert point_ids(qdrant) == []
