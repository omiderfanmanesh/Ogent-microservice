"""
Application configuration.

This module defines the application configuration settings.
"""

import os
import secrets
from typing import Any, Dict, Optional, List

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.
    
    This class defines the application configuration settings.
    Environment variables can be used to override these settings.
    """
    
    # Application settings
    app_name: str = "LangChain Agent Service"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = Field(default=True)  # Set to True for development
    
    # Security settings
    secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    access_token_expire_minutes: int = Field(default=60 * 24 * 7)  # 7 days
    
    # Database settings
    database_url: str = Field(
        default="sqlite+aiosqlite:///./test.db"
    )
    
    # LangChain settings
    openai_api_key: Optional[str] = Field(default=None)
    command_service_url: str = Field(default="http://localhost:8001")
    
    # CORS settings
    cors_origins: List[str] = Field(default=["*"])
    
    # Default admin user settings
    admin_username: str = Field(default="admin")
    admin_password: str = Field(default="admin123")
    admin_email: str = Field(default="admin@example.com")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    def get_database_url_sync(self) -> str:
        """
        Get synchronous database URL.
        
        Returns:
            Synchronous database URL
        """
        # For sync SQLAlchemy operations (e.g., Alembic migrations)
        return str(self.database_url).replace("+asyncpg", "")


# Create settings instance
settings = Settings()


# Export settings
__all__ = ["settings"] 