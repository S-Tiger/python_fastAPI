# app/domains/apitest/router.py
from fastapi import APIRouter
from fastapi.params import Depends

from app.domains.apitest.schemas import ApiRequest
from app.domains.apitest.service import ApiTestService

router = APIRouter(prefix="/apitest", tags=["Apitest"])


def get_apitest_service() -> ApiTestService:
    return ApiTestService()


@router.get("/{query}")
async def fetch_and_process(query: str, service: ApiTestService = Depends(get_apitest_service)):
    return await service.get_processed_data(query)


@router.post("/process")
async def process_data(
        request: ApiRequest,  # JSON Body를 자동으로 파싱합니다.
        service: ApiTestService = Depends(get_apitest_service)
):
    return await service.send_and_process(request)


@router.get("/search")
async def search_data(query: str, service: ApiTestService = Depends()):
    return await service.get_search_result(query)