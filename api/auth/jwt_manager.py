"""
Module for managing JWT creation and verification.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from fastapi import HTTPException, status

from api.config.settings import env_settings


# JWT constants
SECRET_KEY = env_settings.JWT_SECRET.get_secret_value()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # minutes

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT token with an expiration date.
    """
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta if expires_delta else timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
                )
            )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str) -> dict:
    """
    Decodes and verifies a JWT token.
    """
    try:
        # Decode the JWT token and handle expiration automatically using jose
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

