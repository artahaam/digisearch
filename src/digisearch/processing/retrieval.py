import json
from pathlib import Path

import numpy as np

from digisearch.processing.embedding import model
from digisearch.paths import BGE_EMBEDDINGS_DIR



def load_embeddings():
    products = []

    for path in BGE_EMBEDDINGS_DIR.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))

        products.append({
            "product_id": data["product_id"],
            "vector": np.array(data["vector"]),
        })

    return products


def search(query, top_k=10):
    products = load_embeddings()

    query_vector = model.encode([query])["dense_vecs"][0]

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

    results = search("جوراب ورزشی نخی مردانه")
    for result in results:
        print(result)


