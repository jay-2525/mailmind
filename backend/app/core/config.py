from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # Project Identifiers
    PROJECT_NAME: str = "MailMind: Agentic AI for Smart Email and Career Intelligence"
    APP_NAME: str = "InboxGuard"
    APP_ENV: str = "demo"
    DEBUG: bool = True
    PORT: int = 8000
    SECRET_KEY: str = "inboxguard_super_secret_production_key_must_be_32_characters_minimum"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # LLM Provider Configuration
    LLM_PROVIDER: str = "heuristic"  # Options: 'gemini', 'openai', 'ollama', 'heuristic'
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gemini-1.5-flash"

    # Embedding Model Configuration
    EMBEDDING_PROVIDER: str = "sentence-transformers"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Database
    DATABASE_URL: str = "sqlite:///./inboxguard.db"

    # Google Workspace OAuth Integration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    GOOGLE_SCOPES: list[str] = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/calendar.events"
    ]

    # Demo Mode
    DEMO_MODE: bool = True
    DEMO_USER_EMAIL: str = "alex.morgan@university.edu"
    DEMO_USER_NAME: str = "Alex Morgan"

    # Storage Waste Scoring Formula Weights (Must sum to ~1.0)
    WEIGHT_STORAGE_SIZE: float = 0.25
    WEIGHT_PROMOTIONAL: float = 0.25
    WEIGHT_REDUNDANCY: float = 0.20
    WEIGHT_AGE: float = 0.15
    WEIGHT_LOW_ACTIONABILITY: float = 0.15

    # Job Match Scoring Formula Weights (Must sum to ~1.0)
    WEIGHT_REQUIRED_SKILLS: float = 0.35
    WEIGHT_PREFERRED_SKILLS: float = 0.15
    WEIGHT_SEMANTIC_SIMILARITY: float = 0.20
    WEIGHT_EXPERIENCE: float = 0.15
    WEIGHT_EDUCATION: float = 0.15

    # Thresholds
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.65
    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.88
    WASTE_SCORE_AUTO_RECOMMEND_THRESHOLD: int = 75


settings = Settings()
