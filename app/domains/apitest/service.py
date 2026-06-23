# app/domains/apitest/service.py
from app.domains.apitest.client import ExternalApiClient
from app.domains.apitest.schemas import ApiRequest


class ApiTestService:
    def __init__(self):
        self.client = ExternalApiClient()

    async def get_processed_data(self, query: str):
        # 1. 외부 데이터 가져오기
        raw_data = await self.client.fetch_data(f"search?q={query}")

        # 2. 데이터 가공 (비지니스 로직)
        processed = {
            "query": query,
            "result_count": len(raw_data.get("items", [])),
            "summary": "가공 완료된 데이터입니다."
        }
        return processed

    async def send_and_process(self, request_data: ApiRequest):
        raw_data = await self.client.post_data("api/agent/chat", request_data.model_dump())

        return {"status": "success", "data": raw_data}

    async def get_search_result(self, query: str):
        # 1. 쿼리 파라미터를 넘겨 외부 API 호출
        data = await self.client.fetch_data(query)

        # 2. 결과 가공 (간단한 예시)
        return {
            "origin": "External API",
            "search_term": query,
            "processed_content": f"Result for {query}: {data.get('text', 'No data')}"
        }