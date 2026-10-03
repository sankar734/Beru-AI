from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    APP_NAME: str = "NOVA X"
    APP_ENV: str = "development"
    APP_SECRET: str = "nova-x-secret-key-development"
    JWT_SECRET: str = "nova-x-jwt-secret-key-development-32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    PORT: int = 8000
    HOST: str = "127.0.0.1"
    FRONTEND_URL: str = "http://localhost:5173"

    MONGODB_URL: str = "mongodb://localhost:27017/nova_x"
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_IN_MEMORY_FALLBACK: bool = True

    DEFAULT_AI_PROVIDER: str = "mock"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_AI_API_KEY: Optional[str] = None

    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_DIR: str = "./data/storage"

    DESKTOP_COMPANION_PORT: int = 9000
    DESKTOP_SECRET_TOKEN: str = "nova-desktop-local-token"
    ALLOW_DESKTOP_CONTROL: bool = False

settings = Settings()
