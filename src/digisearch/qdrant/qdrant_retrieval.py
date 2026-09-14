import json
from pathlib import Path
import argparse
import numpy as np
import logging

from digisearch.processing.embedding import get_model
from digisearch.paths import BGE_EMBEDDINGS_DIR, LOG_DIR
from digisearch.qdrant.qdrant_init import get_client, COLLECTION_NAME, QdrantUnavailableError

logger = logging.getLogger('retrieval')
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler(LOG_DIR / 'search.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def load_embeddings():
    products = []

    for path in BGE_EMBEDDINGS_DIR.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read embedding file {path}: {e}")
            continue

        products.append({
            "product_id": data["product_id"],
            "vector": np.array(data["vector"]),
        })

    logger.info(f"{len(products)} product embeddings loaded")
    return products


def search(query, top_k=10):

    model = get_model()
    query_vector = model.encode([query])["dense_vecs"][0]

    logger.info(f"Retrieval started with the query: {query}")

    client = get_client()  

    try:
        if not client.collection_exists(COLLECTION_NAME):
            logger.warning(f"Collection '{COLLECTION_NAME}' does not exist yet; no embeddings uploaded.")
            return []

        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,  # type: ignore
            with_payload=True,
            limit=top_k,
        ).points
    except QdrantUnavailableError:
        raise
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise

    logger.info("Retrieval finished")

    return search_result[:top_k]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Retrieval")
    parser.add_argument(
        'query',
        type=str,
        help='Retrieval Query, e.g. "تی‌شرت نخی مناسب ورزش"'
    )
    parser.add_argument(
        "--topk",
        type=int,
        default=10,
        help='Retrieve top-k related products'
        )
    args = parser.parse_args()
    query = args.query
    top_k = args.topk

    try:
        results = search(query, top_k)
    except QdrantUnavailableError as e:
        logger.error(str(e))
        raise SystemExit(str(e))

    logger.info(f"{top_k} products retrieved")
    for result in results:
        print(result)
