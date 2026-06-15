# app/domins/documents/repository.py
from sqlalchemy.orm import Session

from domains.attachments.models import Attachment
from domains.documents.models import Document


class DocumentRepository:
    @staticmethod
    def create(
            db: Session,
            document_title: str,
            key_word: str,
            author: str,
            attachment: Attachment | None = None
    ) -> Document:
        db_document = Document(
            document_title=document_title,
            key_word=key_word,
            attachment=attachment
        )

        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document