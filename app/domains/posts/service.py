# app\domains\posts\service.py

from ast import List
import os
from typing import Optional
import uuid

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.domains.posts.models import Post
from app.domains.posts.repository import PostRepository
from app.domains.posts.schemas import PostResponse


class PostService:
    def __init__(self, db: Session):
        # 생성자를 통해 DB 세션을 관리합니다.
        self.db = db
        # 📂 실제 서버 컴퓨터에 파일이 저장될 절대 경로 설정
        self.UPLOAD_DIR = "D:/pythonstudy/uvfapi/uploads"
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    
    def create_post(
            self, title: str, content: str, author: str, upload_file: Optional[UploadFile]
    ) -> Post:
        
        orig_name = None
        stored_name = None
        saved_file_path = None

        # 1. 파일이 첨부되어 들어왔을 경우의 비즈니스 로직 처리
        if upload_file and upload_file.filename:
            orig_name = upload_file.filename

            # [보안 규칙] 사용자가 같은 이름의 파일을 올리면 덮어쓰기 에러가 나므로,
            # 파일명 앞에 무작위 문자열인 UUID를 붙여서 전 세계에서 유일한 파일명을 만듭니다.
            stored_name = f"{uuid.uuid4()}_{orig_name}"
            saved_file_path = os.path.join(self.UPLOAD_DIR, stored_name)

            try:
                # [대규모 메모리 방어] 대용량 파일이 들어와도 서버 RAM 메모리가 
                # 터지지 않도록 1MB씩 쪼개서(Chunk) 디스크에 스트리밍으로 저장합니다.
                with open(saved_file_path, "wb") as buffer:
                    while chunk := upload_file.file.read(1024 * 1024):
                        buffer.write(chunk)

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"서버 디스크에 파이을 저장하는 중 오류 발생: {str(e)}"
                )
            
            finally:
                # 사용이 끝난 파일 스트림은 반드시 닫아서 OS 자원을 반환합니다.
                upload_file.close()

        return PostRepository.create(
            db=self.db,
            title=title,
            content=content,
            author=author,
            orig_name=orig_name,
            stored_name=stored_name,
            file_path=saved_file_path
            )

    def read_posts (self, skip: int, limit: int) -> List[PostResponse]:
        if limit > 100:
            limit = 0
        return PostRepository.get_multi(self.db, skip=skip, limit=limit)