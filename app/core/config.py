from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, computed_field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Task Management API"
    SECRET_KEY: str = "supersecretkey123456"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "taskdb"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

    @computed_field
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
