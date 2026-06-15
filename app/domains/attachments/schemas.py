# app/domains/attachments/schemas.yp
from datetime import datetime

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    attachment_id: int
    original_file_name: str
    file_path: str
    created_at: datetime
    author: str
    class Config:
        from_attributes = True