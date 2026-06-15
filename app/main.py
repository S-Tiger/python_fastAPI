# app\main.py


from fastapi import FastAPI

from app.core.config import settings
from app.core.database import engine, Base
from app.domains.posts import router as post_router


# 앱 구동 시 PostgreSQL에 테이블 자동 생성 (실무 대규모 앱은 주로 alembic 마이그레이션 도구를 병행함)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="PostgreSQL + Psycopg3 환경의 CRUD"
)

# 도메인 라우터 조립
app.include_router(post_router.router)

@app.get("/health-check", tags=["System"])
def health_check():
    return {"status": "healthy", "project_name": settings.PROJECT_NAME}