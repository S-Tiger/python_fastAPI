# app\domains\posts\models.py

from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# [부모 엔티티] 게시글 테이블
# 하나의 게시글은 여러 개의 첨부파일을 가질 수 있습니다. (1 : N 관계)
class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # [관계 연동] 자바 JPA의 @OneToMany(mappedBy = "post", cascade = CascadeType.ALL)와 같습니다.
    # - back_populates: 자식 엔티티(attachmentFiles)의 어떤 변수와 매치되는지 연결합니다.
    # - cascade="all, delete-orphan": 게시글이 삭제되면 그 글에 달린 첨부파일 데이터도 함께 자동 삭제(종속)시킵니다.
    attachmentFiles = relationship(
        "AttachmentFile", 
        back_populates="post", 
        cascade="all, delete-orphan"
    )

class AttachmentFile(Base):
    __tablename__ = 'attachmentFiles'
    
    id = Column(Integer, primary_key=True, index=True)

    # [외래키 설정] 자바 JPA의 @JoinColumn(name = "post_id") 역할입니다.
    # posts 테이블의 id 컬럼이 삭제(CASCADE)되면 이 파일 행도 같이 지워지도록 물리적 제약조건을 겁니다.
    post_id = Column(
        Integer, 
        ForeignKey("posts.id", ondelete="CASCADE"), 
        nullable=False
    )

    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # [관계 연동] 자바 JPA의 @ManyToOne 역할입니다.
    # 이 파일이 속한 부모 게시글 객체를 역으로 바로 조회할 수 있게 해줍니다.
    post = relationship("Post", back_populates="attachmentFiles")