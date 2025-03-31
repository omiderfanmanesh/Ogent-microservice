"""
Application configuration.

This module provides configuration settings for the LangChain Agent Service.
"""

import os
from typing import Dict, List, Optional, Any

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    Application settings.
    
    This class provides configuration settings for the LangChain Agent Service.
    """
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    # Application
    app_name: str = "LangChain Agent Service"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = False
    api_key: str = "default_api_key"  # Default API key for development
    
    # Database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "langchain_agent"
    database_url: Optional[str] = None
    db_echo_log: bool = False
    db_create_tables: bool = True
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # LangChain
    openai_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langchain_project: Optional[str] = None
    
    # Model defaults
    default_model: str = "gpt-4o-mini"
    default_temperature: float = 0.7
    
    # Command execution
    command_service_url: str = "http://localhost:8001"
    default_command_timeout: int = 30
    default_allowed_commands: List[str] = [
        "ls", "cat", "grep", "find", "echo", "pwd", "curl", "wget",
        "head", "tail", "wc", "sort", "uniq", "cut"
    ]
    max_memory_limit: int = 512  # MB
    
    @validator("database_url", pre=True)
    def assemble_db_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        """
        Assemble database URL if not provided.
        
        Args:
            v: Current value
            values: Other values
            
        Returns:
            Database URL
        """
        if v:
            return v
        
        user = values.get("db_user", "postgres")
        password = values.get("db_password", "postgres")
        host = values.get("db_host", "localhost")
        port = values.get("db_port", 5432)
        name = values.get("db_name", "langchain_agent")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"


# Create settings instance
settings = Settings() 