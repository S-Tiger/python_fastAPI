# app\core\config.py


from pydantic_settings import BaseSettings, SettingsConfigDict


class settings(BaseSettings):
    PROJECT_NAME: str = 'RAG 시스템 API'

    # PostgreSQL 연결 정보
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = '1234'
    DB_NAME: str = 'test'

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = settings()