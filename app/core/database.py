from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# 커넥션 풀 설정이 포함된 엔진 생성
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,           # 대규모 트래픽을 고려한 기본 풀 크기
    max_overflow=10,        # 트래픽 폭증 시 추가 생성 가능한 연결 수
    pool_pre_ping=True      # 연결 유효성 자동 체크
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()