"""
Environment variables configuration for the FastAPI project.
"""

from pydantic import ConfigDict, Field, SecretStr
from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    # Rate Limiting Settings
    RATE_LIMIT: int = Field(100, description="Maximum number of requests allowed per window")
    RATE_LIMIT_WINDOW: int = Field(60, description="Time window in seconds for rate limiting")

    # JWT Settings
    JWT_EXPIRATION_TIME: int = Field(3600, description="JWT token expiration time in seconds (default: 1 hour)")

    # Timeout Settings
    TIMEOUT: int = Field(10, description="Timeout duration for requests in seconds")
    
    # Redis Settings
    REDIS_URL: str = Field(..., description="URL for connecting to Redis")
    
    # Secret Keys (for security reasons, these should not be hardcoded)
    SECRET_KEY: SecretStr = Field(..., description="Secret key for encrypting data")
    JWT_SECRET: SecretStr = Field(..., description="Secret key for signing JWT tokens")

    # Debugging and Logging Settings
    DEBUG: bool = Field(False, description="Set to True for debugging purposes")
    
    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )


api_settings = APISettings()
