# app\domains\posts\router.py

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.posts.repository import PostRepository
from app.domains.posts.schemas import PostCreate, PostResponse, PostUpdate
from app.domains.posts.service import PostService


router = APIRouter(prefix="/posts", tags=["Posts"])

def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(db)


# 생성 ("/posts/ 가 되지만 /posts로 호출해도 FastAPI가 /posts/로 연결해준다.")
@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post_in: PostCreate, file: Optional[UploadFile] = File(None),  db: Session = Depends(get_db)):

    return PostRepository.create(db, post_in, file)

@router.post("/addFile", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post_file(
    # 파일과 텍스트를 동시에 받을 때는 아래와 같이 Form과 File 문법으로 낱개로 명시하는 것이 FastAPI 전 세계 표준입니다.
    title: str = Form(..., min_length=2, max_length=200, description="게시글 제목"),
    content: str = Form(..., description="게시글 본문 내용"),
    author: str = Form(..., min_length=2, max_length=50, description="작성자 이름"),
    file: Optional[UploadFile] = File(None, description="첨부 파일 (선택 사항)"),
    # 의존성 주입구들 (Service와 DB 세션)
    post_service: PostService = Depends(get_post_service)
    ):
    return post_service.create_post(
        title=title, 
        content=content, 
        author=author, 
        upload_file=file
    )

# 목록
@router.get("/", response_model=List[PostResponse])
def read_posts(skip: int = 0, limit: int = 10, post_service: PostService = Depends(get_post_service)):
    return post_service.read_posts(skip=skip, limit=limit)

# 상세
@router.get("/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):

    post = PostRepository.get_by_id(db, post_id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return post

# 수정
@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_in: PostUpdate, db: Session = Depends(get_db)):

    post = PostRepository.get_by_id(db, post_id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return PostRepository.update(db, db_post=post, post_in=post_in)

# 삭제
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    
    post = PostRepository.get_by_id(db, post_id=post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    return None