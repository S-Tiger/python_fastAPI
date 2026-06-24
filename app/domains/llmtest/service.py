# app/domains/llmtest/service.py
from app.core.config import settings
from app.domains.llmtest.client import ElasticsearchRagClient
# from app.domains.llmtest.client import OllamaLangChainClient
from app.domains.llmtest.schemas import ChatRequest


class LlmTestService:
    def __init__(self):
        # self.llm_client = OllamaLangChainClient()
        self.rag_client = ElasticsearchRagClient()


    # async def get_llm_answer(self, request_data: ChatRequest) -> dict:
    #     """LangChain 인프라 레이어를 호출하여 결과 스펙을 바인딩합니다."""
    #
    #     # 1. 비동기 체인 구동
    #     refined_reply = await self.llm_client.chat_async(request_data.prompt)
    #
    #     # 2. 도메인 표준 아웃풋 스펙 멀티플렉싱
    #     return {
    #         # "model": "exaone3.5",
    #         "model": settings.OLLAMA_MODEL_NAME,
    #         "reply": refined_reply
    #     }
    async def ingest_knowledge_base(self, texts: list[str]) -> dict:
        """사내 매뉴얼이나 참조 문서를 엘라스틱서치 벡터에 적재하는 비즈니스 로직"""
        await self.rag_client.add_documents_async(texts=texts)
        return {"status": "success", "inserted_count": len(texts)}

    async def get_rag_answer(self, request_data: ChatRequest) -> dict:
        """컨텍스트 기반 검색 증강 생성(RAG) 실행"""
        rag_reply = await self.rag_client.ask_rag_async(request_data.prompt)
        return {
            "model": "exaone3.5 + elasticsearch_rag",
            "reply": rag_reply
        }