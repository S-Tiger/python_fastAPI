# app/domains/documents/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Document(Base):
    __tablename__ = 'documents'

    document_id = Column(Integer, primary_key=True, index=True)
    document_title = Column(String(200), nullable=False, index=True)
    key_word = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author = Column(String(50), nullable=False)
    # 다른 게시글이 이 파일을 공유할 수 없도록 unique=True를 반드시 걸어 1:1을 강제합니다.
    attachment_id = Column(
        Integer,
        ForeignKey('attachments.attachment_id', ondelete='CASCADE'), # 글이 지워져도 파일 이력은 남기거나, 비즈니스에 따라 CASCADE 설정
        unique=True
        , index=True
    )

    attachment = relationship("Attachment", back_populates="document")