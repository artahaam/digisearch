import json
import logging
from functools import lru_cache

from digisearch.paths import CANONICAL_PRODUCTS_DIR
from digisearch.qdrant.qdrant_init import QdrantUnavailableError, get_collection_count
from digisearch.qdrant.qdrant_retrieval import search as qdrant_search

logger = logging.getLogger("api")

MAX_HISTORY_MESSAGES = 5
ONLINE_LLM_MODEL = "@cf/qwen/qwen3-30b-a3b-fp8"

class UpstreamError(RuntimeError):
    """An outside dependency (Qdrant, Cloudflare LLM) failed."""


# ---------------------------------------------------------------- products
@lru_cache(maxsize=4096)
def _read_canonical(product_id: int) -> dict | None:
    path = CANONICAL_PRODUCTS_DIR / f"{product_id}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("canonical file missing/unreadable for product %s", product_id)
        return None


def _full_url(url: str | None) -> str | None:
    if url and not url.startswith(("http://", "https://")):
        return "https://" + url.lstrip("/")
    return url


def to_product(point) -> dict:
    product_id = int(point.id)
    payload = point.payload or {}
    canonical = _read_canonical(product_id) or {}

    images = canonical.get("product_images") or []
    return {
        "id": product_id,
        "score": point.score,
        "title_fa": canonical.get("product_title_fa", ""),
        "title_en": canonical.get("product_title_en", ""),
        "brand_fa": canonical.get("brand_title_fa") or payload.get("brand_title_fa", ""),
        "brand_en": canonical.get("brand_title_en") or payload.get("brand_title_en", ""),
        "price": canonical.get("product_price") or payload.get("product_price", 0),
        "image": images[0] if images else None,
        "url": _full_url(canonical.get("product_url")) or payload.get("url"),
    }


def search_products(query: str, top_k: int) -> list[dict]:
    try:
        points = qdrant_search(query, top_k)
    except QdrantUnavailableError as e:
        raise UpstreamError(str(e)) from e
    return [to_product(p) for p in points]



def chat(message: str, history: list[dict], top_k: int) -> tuple[str, list[dict]]:
    try:
        from digisearch.rag import online_llm
        from digisearch.rag.context import build_context, get_url, resolve_product_links
    except (KeyError, ImportError) as e:
        raise UpstreamError(f"Chat is not configured: {e!r}") from e

    try:
        points = qdrant_search(message, top_k)
    except QdrantUnavailableError as e:
        raise UpstreamError(str(e)) from e

    context, _refs = build_context(points)
    trimmed_history = history[-MAX_HISTORY_MESSAGES:]
    prompt = online_llm.get_prompt(message, context, trimmed_history)

    try:
        output = online_llm.run(ONLINE_LLM_MODEL, prompt)
        raw = output["result"]["response"]
    except Exception as e:
        logger.exception(f"LLM call failed, error: {e}")
        raise UpstreamError("The language model did not respond correctly.") from e

    reply = resolve_product_links(raw, get_url)
    return reply, [to_product(p) for p in points]



def qdrant_status() -> tuple[bool, int | None]:
    count = get_collection_count()
    return count is not None, count
