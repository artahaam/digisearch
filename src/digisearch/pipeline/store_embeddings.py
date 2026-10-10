import gc
import numpy as np
from qdrant_client.models import PointStruct
from functools import lru_cache
from digisearch.database.client import get_db
from digisearch.qdrant.qdrant_init import get_qdrant_client, QDRANT_COLLECTION, QdrantUnavailableError
from digisearch.services.document import generate_document
from digisearch.config import DEFAULT_BATCH_SIZE, DEFAULT_MAX_LENGTH, MODEL_NAME 


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = MODEL_NAME):

    from FlagEmbedding import BGEM3FlagModel

    try:
        model = BGEM3FlagModel(model_name, use_fp16=True)
    except Exception:
        raise
    return model


def get_product(product_id: int) -> dict:
    product = get_db()["products"].find_one({"product_id": product_id})
    if product is None:
        raise ValueError(f"product {product_id} not found")
    return product


def build_payload(product: dict) -> dict:
    return {
        "product_id": product["product_id"],
        "url": product.get("product_url") or "",
        "title_fa": (product.get("product_title_fa") or "").strip(),
        "title_en": (product.get("product_title_en") or "").strip(),
        "brand_fa": product.get("brand_title_fa") or "",
        "brand_en": product.get("brand_title_en") or "",
        "categories": [c for c in product.get("product_categories") or [] if c],
        "price": product.get("product_price") or 0,
    }


def generate_and_save_embedding(product_id: int, max_length: int = int(DEFAULT_MAX_LENGTH)) -> None:
    product = get_product(product_id)
    document = generate_document(product)
    vector = get_embedding_model().encode([document], max_length=max_length)["dense_vecs"][0].tolist() #type: ignore

    get_qdrant_client().upsert(
        collection_name=QDRANT_COLLECTION,
        wait=True,
        points=[
            PointStruct(
            id=int(product_id),
            vector=vector,
            payload=build_payload(product))
        ],
    )