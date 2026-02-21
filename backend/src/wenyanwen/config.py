"""Application configuration using pydantic-settings."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Get the backend directory (parent of src/)
BACKEND_DIR = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Database - use absolute path relative to backend directory
    database_url: str = f"sqlite:///{BACKEND_DIR}/data/wenyanwen.db"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Environment
    environment: str = "development"


settings = Settings()
