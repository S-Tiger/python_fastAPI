# app/domains/apitest/schemas.py
from pydantic import BaseModel


class ApiRequest(BaseModel):
    userId: str
    message: str