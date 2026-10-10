from digisearch.pipeline.store_embeddings import get_embedding_model
from digisearch.qdrant.qdrant_init import get_qdrant_client, COLLECTION_NAME, QdrantUnavailableError


def retrieve(query, threshold:float|int=0.4, top_k=10):

    model = get_embedding_model()
    query_vector = model.encode([query])["dense_vecs"][0]
    client = get_qdrant_client()  

    try:
        if not client.collection_exists(COLLECTION_NAME):
            return []

        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,  # type: ignore
            with_payload=True,
            limit=top_k,
            score_threshold=threshold,
        ).points
    except QdrantUnavailableError:
        raise
    except Exception as e:
        raise
    return search_result[:top_k]