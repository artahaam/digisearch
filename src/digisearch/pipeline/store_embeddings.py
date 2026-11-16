import logging
from datetime import UTC, datetime
from functools import lru_cache

from pymongo import UpdateOne
from qdrant_client.models import PointStruct

from digisearch.config import DEFAULT_BATCH_SIZE, DEFAULT_MAX_LENGTH, MODEL_NAME
from digisearch.database.client import get_db
from digisearch.qdrant.qdrant_init import QDRANT_COLLECTION, get_qdrant_client
from digisearch.services.fingerprint import document_and_hash

log = logging.getLogger(__name__)

PENDING = {"$or": [
    {"embedded_hash": {"$exists": False}},
    {"$expr": {"$ne": ["$content_hash", "$embedded_hash"]}},
]}

@lru_cache(maxsize=1)
def get_embedding_model(model_name: str = MODEL_NAME):

    from FlagEmbedding import BGEM3FlagModel

    try:
        model = BGEM3FlagModel(model_name, use_fp16=True)
    except Exception:
        raise
    return model


def _chunks(seq: list, n: int):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


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


def embed_products(products: list[dict], max_length: int, batch_size: int) -> int:

    items = []
    for p in products:
        doc, h = document_and_hash(p)
        if doc:
            items.append((p, doc, h))
    if not items:
        return 0

    vectors = get_embedding_model().encode(
        [doc for _, doc, _ in items], batch_size=batch_size, max_length=max_length
    )["dense_vecs"]

    get_qdrant_client().upsert(
        collection_name=QDRANT_COLLECTION,
        wait=True,
        points=[
            PointStruct(id=int(p["product_id"]), vector=v.tolist(), payload=build_payload(p)) #type: ignore
            for (p, _, _), v in zip(items, vectors)
        ],
    )

    now = datetime.now(UTC)
    get_db()["products"].bulk_write(
        [UpdateOne({"product_id": p["product_id"]},
                   {"$set": {"content_hash": h, "embedded_hash": h, "embedded_at": now}})
         for p, _, h in items],
        ordered=False,
    )
    return len(items)


def embed_pending(batch_size: int = int(DEFAULT_BATCH_SIZE),
                  max_length: int = int(DEFAULT_MAX_LENGTH),
                  limit: int | None = None,
                  force: bool = False) -> dict:
    products = get_db()["products"]
    get_qdrant_client()                      

    cursor = products.find({} if force else PENDING, {"product_id": 1})
    if limit:
        cursor = cursor.limit(limit)
    ids = [d["product_id"] for d in cursor]
    log.info("%d products to embed", len(ids))

    stats = {"embedded": 0, "skipped": 0, "failed": 0}
    for chunk in _chunks(ids, batch_size):
        batch = list(products.find({"product_id": {"$in": chunk}}))
        try:
            n = embed_products(batch, max_length, batch_size)
        except Exception:
            log.exception("batch of %d failed; it stays pending", len(batch))
            stats["failed"] += len(batch)
            continue
        stats["embedded"] += n
        stats["skipped"] += len(batch) - n
        log.info("progress: %s / %d", stats["embedded"], len(ids))
    log.info("done: %s", stats)
    return stats


def generate_and_save_embedding(product_id: int, max_length: int = int(DEFAULT_MAX_LENGTH)) -> None:
    embed_products([get_product(product_id)], max_length, batch_size=1)