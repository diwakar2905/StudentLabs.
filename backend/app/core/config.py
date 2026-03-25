"""
Application configuration and settings.
Centralized place for all configuration constants.
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # App metadata
    APP_NAME: str = "StudentLabs"
    APP_VERSION: str = "2.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./studentlabs.db")
    
    # JWT/Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis/Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # AI Models
    SUMMARIZER_MODEL: str = "facebook/bart-large-cnn"
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    GENERATOR_MODEL: str = "mistralai/Mistral-7B-Instruct"
    
    # RAG Configuration
    TOP_K_PAPERS: int = 3  # Number of papers to retrieve
    EMBEDDING_DIM: int = 384  # all-MiniLM-L6-v2 dimension
    
    # Generation parameters
    MAX_TOKENS_ABSTRACT: int = 300
    MAX_TOKENS_INTRO: int = 400
    MAX_TOKENS_DISCUSSION: int = 500
    MAX_TOKENS_CONCLUSION: int = 400
    
    # File export
    EXPORT_DIR: str = "generated"
    PDF_MARGIN: int = 40
    PDF_FONT_SIZE: int = 10
    PPT_SLIDE_WIDTH: float = 10.0
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL with any necessary modifications"""
        if cls.DATABASE_URL.startswith("sqlite"):
            return cls.DATABASE_URL
        return cls.DATABASE_URL


# Global settings instance
settings = Settings()
