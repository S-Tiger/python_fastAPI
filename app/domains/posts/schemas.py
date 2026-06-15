# app\domains\posts\schemas.py

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# 게시글 생성 요청 DTO
class PostCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description='게시글 제목')
    content: str = Field(..., escription='게시글 본문')
    author: str = Field(..., min_length=2, max_length=50, description='작성자 명')

# 게시글 수정 요청 DTO
class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    content: Optional[str] = None

# API 응답용 DTO (엔티티를 감싸서 보안 및 포맷팅 처리)
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str

    attachmentFiles: List[AttachmentFileResponse] = []

    created_at: datetime
    updated_at: Optional[datetime] = None
    #updated_at: datetime | None = None 으로 최신버전에서는 표현가능하다 typing import가 필요 없어짐

    class Config:
        from_attributes = True # SQLAlchemy 객체를 Pydantic으로 자동 변환


class AttachmentFileResponse(BaseModel):
    id: int
    original_filename: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True 
