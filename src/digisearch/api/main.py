import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from digisearch.api import services
from digisearch.api.routers import chat, search
from digisearch.api.schemas import HealthResponse

API_V1_PREFIX = "/api/v1"
logger = logging.getLogger("api")




@asynccontextmanager
async def lifespan(app: FastAPI):
    from digisearch.processing.embedding import get_model

    logger.info("Loading embedding model...")
    get_model()
    logger.info("Ready.")
    yield


app = FastAPI(title="DigiSearch API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(services.UpstreamError)
async def upstream_error_handler(request: Request, exc: services.UpstreamError):
    logger.error("Upstream failure on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.get("/health", response_model=HealthResponse, tags=["meta"])
def health():
    ok, count = services.qdrant_status()
    return HealthResponse(status="ok" if ok else "degraded", qdrant=ok, products_indexed=count)


app.include_router(search.router, prefix=API_V1_PREFIX)
app.include_router(chat.router, prefix=API_V1_PREFIX)
