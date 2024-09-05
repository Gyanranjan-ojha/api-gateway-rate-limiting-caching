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
    CURRENT_ENVIRONMENT: str  # Current environment (development, production, etc.)
    DEBUG: int = Field(..., gt=-1, lt=2, description="Debug value should be 1 or 0")  # Debug mode (1 or 0)
    SECRET_KEY: SecretStr  # Secret key for JWT token security
    JWT_SECRET: SecretStr  # Secret key for encoding JWT tokens
    REDIS_HOST: str  # Redis host for caching and rate limiting
    REDIS_PORT: int  # Redis port
    LOG_FILE_PATH: str  # Path to log file for error logging
    
    class Config:
        env_file = '.env'  # Load environment variables from .env file
        env_file_encoding = 'utf-8'  # UTF-8 encoding for the environment file

# ____Performance: Load Environment Variables at Runtime____
# This approach allows dynamic configuration based on different environments (development, testing, production).
env_settings = APIEnvSettings()
