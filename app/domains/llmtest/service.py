# app/domains/llmtest/service.py
import io

from fastapi import UploadFile
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

from app.core.config import settings
from app.domains.llmtest.client import ElasticsearchRagClient
# from app.domains.llmtest.client import OllamaLangChainClient
from app.domains.llmtest.schemas import ChatRequest


class LlmTestService:
    def __init__(self):
        # self.llm_client = OllamaLangChainClient()
        self.rag_client = ElasticsearchRagClient()

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,  # bge-m3 모델의 임베딩 해상도를 고려한 청크 크기
            chunk_overlap=60,  # 청크 간 문맥 단절을 막기 위한 중첩 구간
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # 페이지/문단/문장 단위 순차 안전 분할
        )


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
    async def process_and_ingest_pdf(self, file: UploadFile) -> dict:
        """
        FastAPI UploadFile 스트림 수신 ➡️ 인메모리 PDF 텍스트 추출 ➡️
        문서 청킹(Split) ➡️ 메타데이터 매핑 ➡️ 벡터 스토어 적재 파이프라인
        """
        # 1. 파일 비동기 스트림 읽기 (메모리 적재)
        file_bytes = await file.read()

        # 2. 인메모리 바이너리 스트림 변환 및 pypdf 파싱 (Windows 디스크 I/O Lock 원천 차단)
        pdf_reader = PdfReader(io.BytesIO(file_bytes))

        raw_documents = []
        for page_idx, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if not page_text or not page_text.strip():
                continue

            # 3. 페이지별 로우 데이터 Document 객체화 및 추적용 메타데이터 주입
            raw_documents.append(Document(
                page_content=page_text,
                metadata={
                    "source": file.filename,
                    "page": page_idx + 1  # 1부터 시작하는 페이지 번호
                }
            ))

        # 4. 텍스트 분할기(Text Splitter) 구동하여 청킹 수행
        # 이 과정을 거쳐야 검색 시 엉뚱한 페이지 전체가 아닌 '정확한 단락'만 스코어링되어 LLM에 인입됩니다.
        split_documents = self.text_splitter.split_documents(raw_documents)

        # 5. 인프라 레이어를 통해 엘라스틱서치에 최종 적재
        await self.rag_client.add_langchain_documents_async(split_documents)

        return {
            "status": "success",
            "filename": file.filename,
            "total_pages": len(pdf_reader.pages),
            "chunked_count": len(split_documents)
        }