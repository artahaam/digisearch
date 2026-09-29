from fastapi import APIRouter

from digisearch.api import services
from digisearch.api.schemas import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest):
    history = [m.model_dump() for m in body.history]
    reply, sources = services.chat(body.message, history, body.top_k)
    return ChatResponse(reply=reply, sources=sources) #type: ignore
