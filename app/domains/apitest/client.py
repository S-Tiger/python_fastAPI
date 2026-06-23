# app/domains/apitest/client.py
from urllib import response

import httpx
from fastapi import HTTPException


class ExternalApiClient:

    # 외부 API와 직접 통신하는 인프라 계층
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def fetch_data(self, endpoint: str):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/{endpoint}", timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise HTTPException(status_code=502, detail=f"외부 API 통신 오류: {str(e)}")

    # POST 방식으로 JSON BODY 전송
    async def post_data(self, endpoint: str, payload: dict):

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/{endpoint}",
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()

                # return response.json()

                raw_text = response.text

                # 'data:'로 시작하는지 확인하고 제거
                if raw_text.startswith("data:"):
                    clean_text = raw_text.replace("data:", "").strip()
                    return {"result": clean_text}  # 가공된 텍스트 반환

                return {"result": raw_text}
            except httpx.HTTPError as e:
                raise HTTPException(status_code=502, detail=f"외부 API 통신 오류: {str(e)}")
