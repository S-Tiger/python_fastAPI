# app\domains\posts\repository.py

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.domains.posts.models import AttachmentFile, Post
from app.domains.posts.schemas import PostCreate, PostUpdate

class PostRepository:
    @staticmethod
    def create(
        db: Session, 
        title: str, 
        content: str, 
        author: str, 
        orig_name: Optional[str] = None, 
        stored_name: Optional[str] = None, 
        file_path: Optional[str] = None
    ) -> Post:
        
        # [게시글 및 첨부파일 일괄 동시 생성 함수]
        # 1. 부모 객체인 게시글 인스턴스를 먼저 생성합니다.
        db_post = Post(title=title, content=content, author=author)

        # 2. 만약 파일 정보가 파라미터로 넘어왔다면 자식 객체를 생성합니다.
        if file_path and orig_name and stored_name:
            db_attachmentFile = AttachmentFile(
                original_filename=orig_name,
                stored_filename=stored_name,
                file_path=file_path
            )
            # [SQLAlchemy 핵심 문법] 
            # 부모 객체의 관계형 리스트(.attachmentFiles)에 자식 객체를 .append()로 추가해 주기만 하면,
            # SQLAlchemy가 알아서 부모 ID(FK)를 자식에게 매핑해 줍니다! (JPA와 동일한 편의성)
            db_post.attachmentFiles.append(db_attachmentFile)

        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        return db_post
    
    @staticmethod
    def get_by_id(db: Session, post_id : int) -> Optional[Post]:
        return db.execute(select(Post).where(Post.id == post_id)).scalar_one_or_none()
    
    @staticmethod
    def get_multi(db: Session, skip: int = 0, limit: int = 10) -> List[Post]:
        # 대규모 조회 시 페이징
        statement = select(Post).offset(skip).limit(limit).order_by(Post.created_at.desc())
        return list(db.execute(statement).scalars().all())

    @staticmethod
    def update(db: Session, db_post: Post, post_in: PostUpdate) -> Post:
        update_data = post_in.model_dump(exclude_unset=True) # 전송된 필드만 추출
        for key, value in update_data.item():
            setattr(db_post, key, value)
        db.commit()
        db.refresh(db_post)
        return db_post
    
    @staticmethod
    def delete(db: Session, db_post: Post) -> None:
        db.delete(db_post)
        db.commit()