# app/domains/attachments
from sqlalchemy import Column, Integer, String, DateTime, func, CheckConstraint
from sqlalchemy.orm import relationship

from core.database import Base


class Attachment(Base):
    __tablename__ = 'attachments'

    attachment_id = Column(Integer, primary_key=True, index=True)
    original_file_name = Column(String(255), nullable=False)
    stored_file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author = Column(String(50), nullable=False)

    # 역방향 연동 (어떤 부모들이 나를 쳐다보고 있는지 정의, 1:1이므로 uselist=False)
    # post = relationships("Post", back_populates="attachment", uselist=False)
    document = relationship("Document", back_populates="attachment", uselist=False)