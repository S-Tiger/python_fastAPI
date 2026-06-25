# app/domains/llmtest/router.py
from fastapi import APIRouter, status, UploadFile
from fastapi.params import Depends, File
from pydantic import BaseModel

from app.domains.llmtest.schemas import ChatRequest, ChatResponse
from app.domains.llmtest.service import LlmTestService

router = APIRouter(prefix="/chat", tags=["chat"])

def get_llmtest_service() -> LlmTestService:
    return LlmTestService()

class IngestRequest(BaseModel):
    documents: list[str]  # ["FastAPI의 창시자는 Sebastián Ramírez이다.", "우리 회사 퇴직금 정산일은 매월 25일이다."]

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_with_lagchain(
        request: ChatRequest,
        service: LlmTestService = Depends(get_llmtest_service)
):
    """
    [LangChain 추상화 적용] LCEL 기반 로컬 EXAONE 3.5 연동 API
    """
    return await service.get_llm_answer(request)

@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_documents(
    request: IngestRequest,
    service: LlmTestService = Depends(get_llmtest_service)
):
    """RAG 지식 베이스 아카이빙 API (Elasticsearch 벡터화 적재)"""
    return await service.ingest_knowledge_base(request.documents)

@router.post("/query", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def query_rag(
    request: ChatRequest,
    service: LlmTestService = Depends(get_llmtest_service)
):
    """Elasticsearch k-NN 검색 연동 EXAONE 3.5 RAG 질의 API"""
    return await service.get_rag_answer(request)


@router.post("/upload-pdf", status_code=status.HTTP_201_CREATED)
async def upload_pdf_knowledge(
        file: UploadFile = File(..., description="적재할 사내 가이드라인 및 지식 PDF 파일"),
        service: LlmTestService = Depends(get_llmtest_service)
):
    """
    [Multipart File Upload] PDF 지식 도큐먼트 파싱 및 벡터 DB 적재 API
    """
    # 확장자 검증 보안 가드 벨트
    if not file.filename.lower().endswith('.pdf'):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    return await service.process_and_ingest_pdf(file)