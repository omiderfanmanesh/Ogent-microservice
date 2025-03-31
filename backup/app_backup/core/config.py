"""
Application configuration.

This module provides configuration settings for the application.
"""

import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.
    
    This class defines the configuration for the application,
    with default values that can be overridden by environment variables.
    """
    # App settings
    APP_NAME: str = "langchain-agent"
    APP_VERSION: str = "0.1.0"
    API_KEY: str = "test-api-key"
    
    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "langchain_agent"
    DATABASE_URL: str = ""
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # LangChain settings
    OPENAI_API_KEY: str = ""
    COMMAND_SERVICE_URL: str = "http://localhost:8001/api/v1"
    
    # Model defaults
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 1000
    
    # Command execution settings
    DEFAULT_TIMEOUT_SECONDS: int = 30
    MAX_MEMORY_MB: int = 512
    ALLOWED_PATHS: List[str] = ["/tmp"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Construct DATABASE_URL if not provided
        if not self.DATABASE_URL and all([self.DB_HOST, self.DB_PORT, self.DB_USER, self.DB_PASSWORD, self.DB_NAME]):
            self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


# Create settings instance
settings = Settings() 