from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Document Vault API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost"]
    
    # Integrations
    MAYAN_API_URL: str
    MAYAN_API_TOKEN: str
    OLLAMA_API_URL: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
