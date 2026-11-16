from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

from digisearch.config import QDRANT_COLLECTION, QDRANT_URL, VECTOR_SIZE


class QdrantUnavailableError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    try:
        client = QdrantClient(url=QDRANT_URL, timeout=10)

        if not client.collection_exists(QDRANT_COLLECTION):
            client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE), #type: ignore
            )
            for field, schema in (("price", PayloadSchemaType.FLOAT),
                                  ("brand_fa", PayloadSchemaType.KEYWORD),
                                  ("brand_en", PayloadSchemaType.KEYWORD),
                                  ("categories", PayloadSchemaType.KEYWORD)):
                client.create_payload_index(QDRANT_COLLECTION, field_name=field, field_schema=schema)

        else:
            vectors = client.get_collection(QDRANT_COLLECTION).config.params.vectors

            if isinstance(vectors, VectorParams) and vectors.size != VECTOR_SIZE:
                raise ValueError(f"'{QDRANT_COLLECTION}' has size {vectors.size}, expected {VECTOR_SIZE}")

        return client

    except ValueError:
        raise

    except Exception as e:
        raise QdrantUnavailableError(f"Could not reach Qdrant at {QDRANT_URL}: {e}") from e


def get_collection_count() -> int | None:
    try:
        client = get_qdrant_client()
        info = client.get_collection(QDRANT_COLLECTION)
        return info.points_count
    except QdrantUnavailableError:
        return None
