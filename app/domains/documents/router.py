# app/domains/documents/roter.py
from fastapi import APIRouter, Depends, Form, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.documents.schemas import DocumentResponse
from app.domains.documents.service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

def get_document_service(db: Session = Depends(get_db)) -> DocumentService:
    return DocumentService(db)

@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
        document_title: str = Form(..., description="문서 제목"),
        key_word:str = Form(..., description="키워드"),
        author:str = Form(..., description="등록자"),
        file: UploadFile = File(None, description="1:1 증빙 첨부파일"),
        document_service: DocumentService = Depends(get_document_service),
):
    return document_service.register_document(document_title=document_title, key_word=key_word, author=author, upload_file=file)