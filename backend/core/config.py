from pathlib import Path

from pydantic_settings import BaseSettings
from typing import List, Optional

# .env lives in backend/; config is in backend/core/ so go up one more level
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "resume_updater"

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    RESUME_LLM_PROVIDER: str = "gemini"
    RESUME_LLM_MODEL: str = "gemini-2.5-flash"

    class Config:
        env_file = str(_ENV_PATH)
        case_sensitive = True

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


settings = Settings()
