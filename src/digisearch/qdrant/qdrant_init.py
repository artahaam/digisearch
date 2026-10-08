from functools import lru_cache
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PayloadSchemaType


QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "digisearch"
VECTOR_SIZE = 1024
DEFAULT_THRESHOLD = 0.4

class QdrantUnavailableError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    try:
        client = QdrantClient(url=QDRANT_URL, timeout=10)

        if not client.collection_exists(COLLECTION_NAME):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
            for field, schema in (("price", PayloadSchemaType.FLOAT),
                                  ("brand_fa", PayloadSchemaType.KEYWORD),
                                  ("brand_en", PayloadSchemaType.KEYWORD),
                                  ("categories", PayloadSchemaType.KEYWORD)):
                client.create_payload_index(COLLECTION_NAME, field_name=field, field_schema=schema)

        else:
            vectors = client.get_collection(COLLECTION_NAME).config.params.vectors

            if isinstance(vectors, VectorParams) and vectors.size != VECTOR_SIZE:
                raise ValueError(f"'{COLLECTION_NAME}' has size {vectors.size}, expected {VECTOR_SIZE}")

        return client

    except ValueError:
        raise

    except Exception as e:
        raise QdrantUnavailableError(f"Could not reach Qdrant at {QDRANT_URL}: {e}") from e


def get_collection_count() -> int | None:
    try:
        client = get_client()
        info = client.get_collection(COLLECTION_NAME)
        return info.points_count
    except QdrantUnavailableError:
        return None
