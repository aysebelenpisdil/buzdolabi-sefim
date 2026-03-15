from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PORT: int = 3001
    FRONTEND_URL: str = "https://ease-publishing-cleared-productions.trycloudflare.com/"
    GEMINI_API_KEY: Optional[str] = None
    NODE_ENV: str = "development"
    
    # Embedding Model Configuration
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # FAISS Index Configuration
    FAISS_INDEX_TYPE: str = "IndexFlatL2"  # Options: IndexFlatL2, IndexIVFFlat, IndexHNSW
    FAISS_METRIC: str = "L2"  # Options: L2 (Euclidean), IP (Inner Product)
    FAISS_INDEX_PATH: str = "data/recipe_index.faiss"
    
    # Reranker Configuration
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # Cross-encoder for re-ranking
    RERANKER_BATCH_SIZE: int = 32  # Batch size for reranking
    RERANKER_ENABLED: bool = True  # Enable/disable reranker
    
    # LLM Configuration (Gemini)
    GEMINI_MODEL: str = "models/gemini-2.5-flash"  # Options: models/gemini-2.5-flash (fast), models/gemini-2.5-pro (quality)
    GEMINI_FALLBACK_MODEL: Optional[str] = "models/gemini-2.0-flash"  # 429 sonrası denenir (farklı kota havuzu)
    GEMINI_MAX_TOKENS: int = 2000  # Maximum tokens for LLM response
    GEMINI_TEMPERATURE: float = 0.7  # Temperature for creativity (0.0-1.0)
    GEMINI_ENABLED: bool = True  # Enable/disable LLM explanations

    # Database
    DATABASE_PATH: str = "data/smart_fridge.db"

    # Auth & Session
    SESSION_SECRET: str = "change-me-in-production"
    MAGIC_LINK_EXPIRY: int = 600  # seconds
    SESSION_EXPIRY_DAYS: int = 30
    SMTP_ENABLED: bool = False

    # SMTP (Magic Link e-posta)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None  # Gönderen adres (SMTP_USER ile aynı olabilir)
    SMTP_FROM_NAME: str = "Buzdolabı Şefi"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

