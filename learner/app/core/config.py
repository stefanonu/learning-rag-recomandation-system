from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "RAG FastAPI POC"
    DB_PATH: str = "sqlite:///./rag.db"
    FAISS_INDEX_PATH: str = "storage/faiss_index/index.faiss"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
