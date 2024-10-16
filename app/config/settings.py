"""
Environment variables configuration for the FastAPI project.
"""

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings

# ____Environment Configuration____
class APIEnvSettings(BaseSettings):
    """
    Settings class for managing environment variables used in the FastAPI application.
    """
    CURRENT_ENVIRONMENT: str
    DEBUG: int = Field(..., gt=-1, lt=2, description="Debug value should be 1 or 0")
    SECRET_KEY: SecretStr 
    JWT_SECRET: SecretStr 
    REDIS_HOST: str 
    REDIS_PORT: int
    LOG_FILE_PATH: str
    REDIS_URL: str
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

env_settings = APIEnvSettings()
