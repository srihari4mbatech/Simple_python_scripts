"""
Application Configuration Module
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings configuration"""
    
    # Database Configuration
    database_url: str = Field(default="postgresql://username:password@localhost:5432/mcp_database")
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="mcp_database")
    postgres_user: str = Field(default="username")
    postgres_password: str = Field(default="password")
    
    # LLM API Configuration
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    
    # MCP Server Configuration
    mcp_server_host: str = Field(default="localhost")
    mcp_server_port: int = Field(default=8001)
    mcp_log_level: str = Field(default="INFO")
    
    # FastAPI Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    secret_key: str = Field(default="your_secret_key_here")
    debug: bool = Field(default=True)
    
    # Frontend Configuration
    frontend_url: str = Field(default="http://localhost:3000")
    
    # Authentication
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get the complete database URL"""
    return settings.database_url


def validate_llm_apis() -> dict:
    """Validate which LLM APIs are configured"""
    apis = {}
    
    if settings.openai_api_key:
        apis['openai'] = True
    else:
        apis['openai'] = False
        
    if settings.anthropic_api_key:
        apis['anthropic'] = True
    else:
        apis['anthropic'] = False
        
    return apis