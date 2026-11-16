import pytest
from qdrant_client.models import Distance, VectorParams

from digisearch import config
from digisearch.pipeline.store_embeddings import embed_pending
from digisearch.qdrant import qdrant_init
from digisearch.qdrant.qdrant_init import (
    QdrantUnavailableError,
    get_collection_count,
    get_qdrant_client,
)

pytestmark = pytest.mark.integration


def test_collection_is_created_with_the_expected_configuration(qdrant):
    info = qdrant.get_collection(config.QDRANT_COLLECTION)

    vectors = info.config.params.vectors
    assert isinstance(vectors, VectorParams)
    assert vectors.size == int(config.VECTOR_SIZE)
    assert vectors.distance == Distance.COSINE
    assert {"price", "brand_fa", "brand_en", "categories"} <= set(info.payload_schema)


def test_client_is_cached():
    assert get_qdrant_client() is get_qdrant_client()


def test_existing_collection_with_the_wrong_vector_size_is_rejected(qdrant):
    qdrant.delete_collection(config.QDRANT_COLLECTION)
    qdrant.create_collection(
        collection_name=config.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=8, distance=Distance.COSINE),
    )
    get_qdrant_client.cache_clear()

    with pytest.raises(ValueError, match="size"):
        get_qdrant_client()


def test_unreachable_qdrant_raises_a_clear_error_and_count_is_none(monkeypatch):
    monkeypatch.setattr(qdrant_init, "QDRANT_URL", "http://127.0.0.1:1")
    get_qdrant_client.cache_clear()

    with pytest.raises(QdrantUnavailableError):
        get_qdrant_client()
    assert get_collection_count() is None


def test_collection_count_follows_the_stored_points(add_product, fake_model):
    assert get_collection_count() == 0

    add_product(1)
    add_product(2)
    embed_pending()

    assert get_collection_count() == 2
