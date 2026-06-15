# app\main.py


from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.domains.posts import router as post_router
from app.domains.documents import router as document_router


# 앱 구동 시 PostgreSQL에 테이블 자동 생성 (실무 대규모 앱은 주로 alembic 마이그레이션 도구를 병행함)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="PostgreSQL + Psycopg3 환경의 CRUD"
)

# CORS 미들웨어 추가
# 프론트엔드(React, Vue 등) 소스코드와 통신할 때 발생하는 자바스크립트 보안 에러를 원천 차단합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실무 환경에서는 ["https://myfrontend.com"] 처럼 특정 도메인만 지정합니다.
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# 도메인 라우터 조립
app.include_router(post_router.router)
app.include_router(document_router.router)

@app.get("/health-check", tags=["System"])
def health_check():
    return {"status": "healthy", "project_name": settings.PROJECT_NAME}