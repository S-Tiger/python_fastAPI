# app/domains/llmtest/service.py
from app.core.config import settings
from app.domains.llmtest.client import OllamaLangChainClient
from app.domains.llmtest.schemas import ChatRequest


class LlmTestService:
    def __init__(self):
        self.llm_client = OllamaLangChainClient()


    async def get_llm_answer(self, request_data: ChatRequest) -> dict:
        """LangChain 인프라 레이어를 호출하여 결과 스펙을 바인딩합니다."""

        # 1. 비동기 체인 구동
        refined_reply = await self.llm_client.chat_async(request_data.prompt)

        # 2. 도메인 표준 아웃풋 스펙 멀티플렉싱
        return {
            # "model": "exaone3.5",
            "model": settings.OLLAMA_MODEL_NAME,
            "reply": refined_reply
        }