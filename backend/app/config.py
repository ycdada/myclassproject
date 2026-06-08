from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "DSA Learning Multi-Agent System"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://dsa_user:dsa_password@localhost:5432/dsa_learning"
    DATABASE_URL_SYNC: str = "postgresql://dsa_user:dsa_password@localhost:5432/dsa_learning"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "dsa-resources"
    MINIO_SECURE: bool = False

    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # iFlytek Spark API
    SPARK_APP_ID: str = ""
    SPARK_API_KEY: str = ""
    SPARK_API_SECRET: str = ""
    SPARK_API_DOMAIN_PRO: str = "generalv3.5"      # Spark Pro
    SPARK_API_DOMAIN_MAX: str = "generalv4.0"       # Spark Max
    SPARK_API_DOMAIN_128K: str = "pro-128k"         # Spark Pro 128K
    SPARK_TTS_APP_ID: str = ""
    SPARK_TTS_API_KEY: str = ""
    SPARK_ASR_APP_ID: str = ""

    # RAG
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    VECTOR_DIMENSION: int = 384
    RAG_SIMILARITY_THRESHOLD: float = 0.65
    RAG_CHUNK_SIZE: int = 800
    RAG_CHUNK_OVERLAP: int = 100
    RAG_TOP_K: int = 5

    # Content Safety
    ENABLE_SAFETY_FILTER: bool = True
    ENABLE_CODE_SANDBOX: bool = True

    # Generation
    MAX_GENERATION_TOKENS: int = 4096
    TEMPERATURE_FACTUAL: float = 0.3
    TEMPERATURE_CREATIVE: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
