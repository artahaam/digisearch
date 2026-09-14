from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "test_collection"
VECTOR_SIZE = 1024


class QdrantUnavailableError(RuntimeError):
    pass


def get_client() -> QdrantClient:
    try:
        client = QdrantClient(url=QDRANT_URL, timeout=10)

        if not client.collection_exists(COLLECTION_NAME):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.DOT),
            )
        return client

    except Exception as e:

        raise QdrantUnavailableError(
            f"Could not reach Qdrant at {QDRANT_URL}. Make sure the Qdrant "
            f"docker container is running:\n\n"
            f'docker run -p 6333:6333 -p 6334:6334 -v "$(pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant'
        ) from e


def get_collection_count() -> int | None:

    try:
        client = get_client()
        info = client.get_collection(COLLECTION_NAME)
        return info.points_count
    except QdrantUnavailableError:
        return None
