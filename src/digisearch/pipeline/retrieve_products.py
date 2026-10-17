import logging
from qdrant_client.models import ScoredPoint
from digisearch.config import DEFAULT_THRESHOLD
from digisearch.pipeline.store_embeddings import get_embedding_model
from digisearch.qdrant.qdrant_init import QDRANT_COLLECTION, get_qdrant_client

log = logging.getLogger(__name__)


def retrieve(query: str, threshold: float | int = DEFAULT_THRESHOLD, top_k: int = 10) -> list[ScoredPoint] | list:
    client = get_qdrant_client()

    if not client.collection_exists(QDRANT_COLLECTION):
        log.warning("collection %s does not exist yet", QDRANT_COLLECTION)
        return []

    query_vector = get_embedding_model().encode([query])["dense_vecs"][0]

    return client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=query_vector,  # type: ignore
        with_payload=True,
        limit=top_k,
        score_threshold=threshold,
    ).points