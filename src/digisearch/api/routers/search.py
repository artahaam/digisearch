from time import perf_counter

from fastapi import APIRouter, Query

from digisearch.api import services
from digisearch.api.schemas import SearchResponse

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, max_length=300, description="Natural-language query"),
    top_k: int = Query(10, ge=1, le=20),
):
    start = perf_counter()
    results = services.search_products(q.strip(), top_k)
    return SearchResponse(
        query=q,
        count=len(results),
        took_ms=int((perf_counter() - start) * 1000),
        results=results, #type: ignore
    )
