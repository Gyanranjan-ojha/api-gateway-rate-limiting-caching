"""
Pydantic models for request data validation and JWT token handling in the FastAPI application.
"""

from datetime import datetime, timezone

from jose import jwt, JWTError
from pydantic import BaseModel, Field, field_validator, ValidationError

from app.config.settings import env_settings
from app.utils.exceptions import InvalidTokenException


class RequestHeaders(BaseModel):
    """
    Model for validating headers in incoming API requests.
    """

    authorization: str = Field(..., description="Authorization header with Bearer token")

    @field_validator("authorization")
    def check_authorization_format(cls, value):
        """
        Validates that the authorization header contains a Bearer token.
        """
        if not value.startswith("Bearer "):
            raise ValueError("Authorization header must contain a Bearer token.")
        return value


class TokenData(BaseModel):
    """
    Model for JWT token data, with validation for claims.
    """

    sub: str
    exp: datetime
    roles: list[str] = []

    @classmethod
    def from_jwt_token(cls, token: str) -> "TokenData":
        """
        Decodes and validates a JWT token, then initializes a TokenData instance.
        """
        try:
            payload = jwt.decode(token, env_settings.JWT_SECRET.get_secret_value(), algorithms=["HS256"])
            return cls(**payload)
        except JWTError as e:
            raise InvalidTokenException("Invalid JWT token.") from e
        except ValidationError as e:
            # Custom handling for validation errors, if needed
            raise InvalidTokenException(f"Token data validation error: {str(e)}") from e

    @field_validator("exp")
    def check_expiration(cls, value):
        """
        Validates that the token has not expired.
        """
        if datetime.now(timezone.utc) > value:
            raise ValueError("Token has expired.")
        return value
