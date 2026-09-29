from time import perf_counter

from fastapi import APIRouter

from digisearch.api import services
from digisearch.api.schemas import SearchResponse, SearchRequest

router = APIRouter(tags=["search"])

@router.post("/search", response_model=SearchResponse)
def search(body: SearchRequest):
    start = perf_counter()
    results = services.search_products(body.query, body.top_k)
    return SearchResponse(
        query=body.query,
        count=len(results),
        took_ms=int((perf_counter() - start) * 1000),
        results=results,  # type: ignore
    )
