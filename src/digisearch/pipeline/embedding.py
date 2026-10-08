import gc
import numpy as np
from qdrant_client.models import PointStruct
from functools import lru_cache
from digisearch.database.client import get_client as get_mongo_client
from digisearch.qdrant.qdrant_init import get_client as get_qdrant_client, COLLECTION_NAME, QdrantUnavailableError
from digisearch.pipeline.document import generate_document

DEFAULT_BATCH_SIZE = 8
DEFAULT_MAX_LENGTH = 1024
MODEL_NAME = "BAAI/bge-m3"


@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = MODEL_NAME):

    from FlagEmbedding import BGEM3FlagModel

    try:
        model = BGEM3FlagModel(model_name, use_fp16=True)
    except Exception:
        raise
    return model


def get_product(product_id: int) -> dict:
    product = get_mongo_client()["digisearch"]["products"].find_one({"product_id": product_id})
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


def generate_and_save_embedding(product_id: int, max_length: int = DEFAULT_MAX_LENGTH) -> None:
    product = get_product(product_id)
    document = generate_document(product)
    vector = get_embedding_model().encode([document], max_length=max_length)["dense_vecs"][0].tolist() #type: ignore

    get_qdrant_client().upsert(
        collection_name=COLLECTION_NAME,
        wait=True,
        points=[
            PointStruct(
            id=int(product_id),
            vector=vector,
            payload=build_payload(product))
        ],
    )