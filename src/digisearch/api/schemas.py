from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Product(BaseModel):
    id: int
    score: float | None = Field(None, description="Similarity score from Qdrant (higher = closer)")
    title_fa: str = ""
    title_en: str = ""
    brand_fa: str = ""
    brand_en: str = ""
    price: int = 0
    image: str | None = None
    url: str | None = None


class SearchResponse(BaseModel):
    query: str
    count: int
    took_ms: int
    results: list[Product]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(StrictModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=50)
    top_k: int = Field(5, ge=1, le=10)


class ChatResponse(BaseModel):
    reply: str
    sources: list[Product]


class HealthResponse(BaseModel):
    status: str
    qdrant: bool
    products_indexed: int | None = None
