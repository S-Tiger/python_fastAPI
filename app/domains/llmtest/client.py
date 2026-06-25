# app/domains/llmtest/client.py
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_elasticsearch import ElasticsearchStore
from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.core.config import settings


# class OllamaLangChainClient:
#
#     # ollama Exaone 3.5 모델과의 Lcel 파이프라인을 관장하는 클라이언트
#     # def __init__(self, model_name: str = "exaone3.5", base_url: str = "http://localhost:11434"):
#         # 1. 하위 프로바이더 명시적 선언 (스트리밍 비활성화는 내부 프레임워크가 핸들링)
#         # self.model = ChatOllama(
#         #     model=model_name,
#         #     base_url=base_url,
#         #     temperature=0.3,    # 결정론적 답변 생성을 위한 온도 조절
#         #     num_predict=1024    # 최대 토큰 규격 제한
#         # )
#     def __init__(self):
#         self.model = ChatOllama(
#             model=settings.OLLAMA_MODEL_NAME,
#             base_url=settings.OLLAMA_BASE_URL,
#             temperature=settings.LLM_TEMPERATURE,
#             num_predict=settings.LLM_MAX_TOKENS
#         )
#
#         # 2. 시스템/유저 프롬프트 컨텍스트 분리
#         self.prompt = ChatPromptTemplate.from_messages([
#             ("system", "당신은 엔터프라이즈 시스템의 유능한 AI 조력자입니다. 한국어로 전문적이고 간결하게 답변하십시오."),
#             ("user", "{user_input}")
#         ])
#
#         # 3. 로우 AIMessage, 객체를 순수 문자열로 컨버팅하는 파서
#         self.output_parser = StrOutputParser()
#
#         # 4. LCEL(LangChain Expression Language) 컴포지션 조립
#         # 내부적으로 컴파일되어 최적화된 Runnable 시퀀스를 생성합니다.
#         self.chain = self.prompt | self.model | self.output_parser
#
#     async def chat_async(self, prompt_input: str) -> str:
#         """
#         FastAPI의 이벤트 루프를 블로킹하지 않기 위해
#         명시적으로 비동기 엔트리포인트인 `ainvoke`를 호출합니다.
#         """
#         # 비동기 컨텍스트로 체인 실행
#         return await self.chain.ainvoke({"user_input": prompt_input})


class ElasticsearchRagClient:
    def __init__(self):
        # 1. 임베딩 모델 및 LLM 아키텍처 주입
        self.embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_EMBEDDING_MODEL
        )
        self.llm = ChatOllama(
            model=settings.OLLAMA_MODEL_NAME,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.2
        )

        # 2. 엘라스틱서치 벡터 스토어 바인딩
        self.vector_store = ElasticsearchStore(
            es_url=settings.ELASTICSEARCH_URL,
            index_name=settings.ELASTICSEARCH_INDEX,
            embedding=self.embeddings,
            # 💡 실무 치트키: Dense Vector 처리를 위한 대략적인 k-NN 전략 설정
            strategy=ElasticsearchStore.ExactRetrievalStrategy()
        )

        # 3. RAG 전용 프롬프트 엔지니어링 (컨텍스트 바인딩 구조)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 주어진 [Context]의 정보만을 바탕으로 답변하는 정직한 AI입니다. "
                       "Context에 없는 내용은 절대 추측해서 답변하지 말고 '관련 정보를 찾을 수 없습니다'라고 답하십시오.\n\n"
                       "[Context]\n{context}"),
            ("user", "{question}")
        ])

        # 4. 리트리버 선언 (유사도 기준 상위 3개 문서 추출 설정)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

        # 5. LCEL RAG 파이프라인 컴포지션 조립
        # question을 받아 -> retriever를 거쳐 context를 채우고 -> prompt -> llm -> parser 흐름
        self.rag_chain = (
                {"context": self.retriever, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
        )

    async def add_documents_async(self, texts: list[str], metadatas: list[dict] = None):
        """지식 베이스 생성을 위한 백엔드 데이터 인덱싱(적재) 메서드"""
        # 비동기 스레드 풀에서 엘라스틱에 벡터 적재
        await self.vector_store.aadd_texts(texts=texts, metadatas=metadatas)

    async def ask_rag_async(self, question: str) -> str:
        """컨텍스트 검색 후 EXAONE 3.5 모델 기반 생성(RAG) 구동"""
        return await self.rag_chain.ainvoke(question)

    async def add_langchain_documents_async(self, documents: list[Document]):
        """
        [확장] 텍스트와 메타데이터(출처, 페이지 번호 등)가 결합된
        LangChain Document 세트를 Elasticsearch 벡터 인덱스에 벌크 적재합니다.
        """
        if not documents:
            return
        # 엘라스틱서치 스토어의 비동기 문서 적재 API 호출
        await self.vector_store.aadd_documents(documents=documents)