# app/domains/llmtest/router.py
from fastapi import APIRouter, status
from fastapi.params import Depends

from app.domains.llmtest.schemas import ChatRequest, ChatResponse
from app.domains.llmtest.service import LlmTestService

router = APIRouter(prefix="/chat", tags=["chat"])

def get_llmtest_service() -> LlmTestService:
    return LlmTestService()

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_lagchain(
        request: ChatRequest,
        service: LlmTestService = Depends(get_llmtest_service)
):
    """
    [LangChain 추상화 적용] LCEL 기반 로컬 EXAONE 3.5 연동 API
    """
    return await service.get_llm_answer(request)