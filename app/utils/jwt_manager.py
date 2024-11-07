"""
Utility functions for JWT token creation and verification.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config.settings import api_settings


ACCESS_TOKEN_EXPIRE_MINUTES = api_settings.JWT_EXPIRATION_TIME / 60
ALGORITHM = "HS256"
SECRET_KEY = api_settings.JWT_SECRET.get_secret_value()

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_jwt_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])