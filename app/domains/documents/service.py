# app/domains/documents/service.py
import os
import uuid

from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.domains.attachments.models import Attachment
from app.domains.documents.models import Document
from app.domains.documents.repository import DocumentRepository


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

        self.UPLOAD_DIR = "C:/chat/upload"
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def register_document(
            self, document_title: str, key_word: str, author: str, upload_file: UploadFile
    ) -> Document:

        db_attachment = None

        if upload_file and upload_file.filename:
            original_file_name = upload_file.filename
            stored_file_name = f"{uuid.uuid4()}_{original_file_name}"
            saved_file_path = os.path.join(self.UPLOAD_DIR, stored_file_name)

            try:
                with open(saved_file_path, "wb") as buffer:
                    while chunk := upload_file.file.read(1024 * 1024):
                        buffer.write(chunk)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"문서 파일 디스크 저장 실패: {str(e)}")
            finally:
                upload_file.file.close()


            db_attachment = Attachment(
                original_file_name=original_file_name,
                stored_file_name=stored_file_name,
                file_path=saved_file_path,
                author=author,
            )

            # db.add(db_attachment)를 생략해도,
            # 아래 레포지토리에서 db_document를 세션에 넣을 때 '종속성 전이(Cascade Save)'가 일어나서
            # 트랜잭션이 커밋될 때 파일이 먼저 선행 INSERT 되고 문서가 후행 INSERT 됩니다.

        return DocumentRepository.create(
            db=self.db,
            document_title=document_title,
            key_word=key_word,
            author=author,
            attachment=db_attachment,
        )


