from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "resume_updater"

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    GOOGLE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    RESUME_LLM_PROVIDER: str = "gemini"
    RESUME_LLM_MODEL: str = "gemini-2.0-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def effective_google_api_key(self) -> str:
        return self.GOOGLE_API_KEY or self.GEMINI_API_KEY


settings = Settings()