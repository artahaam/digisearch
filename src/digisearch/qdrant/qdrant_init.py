from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


def get_client():
    client = QdrantClient(url="http://localhost:6333")

    if not client.collection_exists:
        client.create_collection(
            collection_name="test_collection",
            vectors_config=VectorParams(size=1024, distance=Distance.DOT),
        )
    return client