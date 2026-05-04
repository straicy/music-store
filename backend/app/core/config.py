from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "music_store"

    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # App
    APP_NAME: str = "MusicStore API"
    DEBUG: bool = True
    CORS_ORIGINS: str = '["http://localhost:5173","http://localhost:3000"]'

    # Uploads
    UPLOAD_DIR: str = "uploads"
    MAX_IMAGE_SIZE_MB: int = 5

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
