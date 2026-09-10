from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
from digisearch.processing.retrieval import load_embeddings
import logging

from digisearch.paths import LOG_DIR
from digisearch.processing.embedding import model

logger = logging.getLogger('vecdb')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_DIR / 'vecdb.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)



client = QdrantClient(url="http://localhost:6333")

if not client.collection_exists:
    client.create_collection(
        collection_name="test_collection",
        vectors_config=VectorParams(size=1024, distance=Distance.DOT),
    )

logger.info("Qdrant create_collection succeeded")

embeddings = load_embeddings()
logger.info(f"{len(embeddings)} embeddings loaded")

points = []

for embedding in embeddings:
    product_id = embedding['product_id']
    vector = embedding['vector']
    points.append(
        PointStruct(id=int(product_id),
                     vector=vector,
                     payload={
                         'url':f'https://www.digikala.com/product/{product_id}/',
                              }
                              )
                              )

logger.info(f'{len(embeddings)} PointStructs created')

operation_info = client.upsert(
    collection_name="test_collection",
    wait=True,
    points=points,
)

logger.info("PointStructs inserted")
logger.info(str(operation_info))
