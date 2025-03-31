"""
Settings configuration for the LangChain Agent Service.

This module loads configuration from environment variables with sensible defaults.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Application settings
    PROJECT_NAME: str = "LangChain Agent Service"
    PROJECT_DESCRIPTION: str = "A service that provides LangChain-based agent functionality"
    API_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Security
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    # Database settings
    DATABASE_URL: str
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "langchain_agent"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_ECHO_LOG: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_CREATE_TABLES: bool = True
    
    # LangChain settings
    OPENAI_API_KEY: str
    DEFAULT_LLM_MODEL: str = "gpt-3.5-turbo"
    DEFAULT_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Command Service settings
    COMMAND_SERVICE_URL: str = "http://command-execution:5000"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    @validator("OPENAI_API_KEY")
    def validate_openai_api_key(cls, v: Optional[str], values: Dict[str, Any]) -> Optional[str]:
        """
        Validate the OpenAI API key if we're not in development mode.
        """
        if values.get("ENVIRONMENT") != "development" and not v:
            raise ValueError("OPENAI_API_KEY is required in non-development environments")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )
    
    # Properties for backward compatibility
    @property
    def app_name(self) -> str:
        return self.PROJECT_NAME
    
    @property
    def app_version(self) -> str:
        return "1.0.0"
    
    @property
    def cors_origins(self) -> List[str]:
        return self.CORS_ORIGINS


# Create a settings instance
settings = Settings()
