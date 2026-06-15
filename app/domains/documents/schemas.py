# app/domains/documents/schemas.py
from datetime import datetime

from pydantic import BaseModel

from domains.attachments.schemas import AttachmentResponse


class DocumentResponse(BaseModel):
   document_id: int
   document_title: str
   key_word: str
   author: str
   # 문서가 파일 객체(AttachmentResponse)를 단건으로 품고 나갑니다.
   # 파일이 없을 수도 있으므로 당연히 | None 처리해 줍니다
   attachment: AttachmentResponse | None = None

   created_at: datetime

   class Config:
      from_attributes = True
