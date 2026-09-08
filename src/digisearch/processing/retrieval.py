import json
from pathlib import Path
import argparse
import numpy as np
import logging

from digisearch.processing.embedding import model
from digisearch.paths import BGE_EMBEDDINGS_DIR, LOG_DIR


logger = logging.getLogger('retrieval')
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(LOG_DIR / 'search.log')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.debug("Retrieval process started.")


def load_embeddings():
    products = []

    for path in BGE_EMBEDDINGS_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))

        products.append({
            "product_id": data["product_id"],
            "vector": np.array(data["vector"]),
        })

    logger.info(f"{len(products)} product embeddings loaded")
    return products


def search(query, top_k=10):
    products = load_embeddings()

    query_vector = model.encode([query])["dense_vecs"][0]

    logger.info(f"Retrieval started with the query: {query}")

    scores = []

    for product in products:
        score = query_vector @ product["vector"]

        scores.append({
            "product_id": product["product_id"],
            "score": float(score),
            "product_url" : f'https://www.digikala.com/product/{product['product_id']}/'
        })

    scores.sort(
        key=lambda x: x["score"],
        reverse=True,
    )
    return scores[:top_k]




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

    results = search(query, top_k)
    logger.info(f"{top_k} products retrieved")
    for result in results:
        print(result)


