# app/domains/llmtest/schemas.py
from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    model: str
    reply: str