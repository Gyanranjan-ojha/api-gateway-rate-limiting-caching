"""
Environment variables configuration for the FastAPI project.
"""


from pydantic import ConfigDict, Field, SecretStr
from pydantic_settings import BaseSettings


# ____Environment Configuration____
class APIEnvSettings(BaseSettings):
    CURRENT_ENVIRONMENT: str
    DEBUG: int = Field(..., gt=-1, lt=2, description="Debug value should be 1 or 0")
    SECRET_KEY: SecretStr 
    JWT_SECRET: SecretStr 
    REDIS_URL: str
    
    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

env_settings = APIEnvSettings()
