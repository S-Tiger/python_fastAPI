# app/domains/llmtest/client.py

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.core.config import settings


class OllamaLangChainClient:

    # ollama Exaone 3.5 모델과의 Lcel 파이프라인을 관장하는 클라이언트
    # def __init__(self, model_name: str = "exaone3.5", base_url: str = "http://localhost:11434"):
        # 1. 하위 프로바이더 명시적 선언 (스트리밍 비활성화는 내부 프레임워크가 핸들링)
        # self.model = ChatOllama(
        #     model=model_name,
        #     base_url=base_url,
        #     temperature=0.3,    # 결정론적 답변 생성을 위한 온도 조절
        #     num_predict=1024    # 최대 토큰 규격 제한
        # )
    def __init__(self):
        self.model = ChatOllama(
            model=settings.OLLAMA_MODEL_NAME,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            num_predict=settings.LLM_MAX_TOKENS
        )

        # 2. 시스템/유저 프롬프트 컨텍스트 분리
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 엔터프라이즈 시스템의 유능한 AI 조력자입니다. 한국어로 전문적이고 간결하게 답변하십시오."),
            ("user", "{user_input}")
        ])

        # 3. 로우 AIMessage, 객체를 순수 문자열로 컨버팅하는 파서
        self.output_parser = StrOutputParser()

        # 4. LCEL(LangChain Expression Language) 컴포지션 조립
        # 내부적으로 컴파일되어 최적화된 Runnable 시퀀스를 생성합니다.
        self.chain = self.prompt | self.model | self.output_parser

    async def chat_async(self, prompt_input: str) -> str:
        """
        FastAPI의 이벤트 루프를 블로킹하지 않기 위해
        명시적으로 비동기 엔트리포인트인 `ainvoke`를 호출합니다.
        """
        # 비동기 컨텍스트로 체인 실행
        return await self.chain.ainvoke({"user_input": prompt_input})