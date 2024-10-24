"""
Authentication service responsible for user authentication and token management.
"""

from typing import Optional
from datetime import timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.models.user import User, UserInDB
from app.utils.exceptions import InvalidTokenException, AuthException
from app.utils.hashing import verify_password
from app.utils.jwt_manager import create_access_token, decode_jwt_token
from app.utils.log_manager import logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    def __init__(self, user_db):
        self.user_db = user_db

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user(username)
        if not user or not verify_password(password, user.hashed_password):
            logger.add_log_to_buffer('warning', f"Failed authentication attempt for user: {username}")
            raise AuthException("Invalid username or password.")
        return user

    def get_user(self, username: str) -> Optional[UserInDB]:
        if username in self.user_db:
            user_dict = self.user_db[username]
            return UserInDB(**user_dict)
        return None

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        try:
            payload = decode_jwt_token(token)
        except Exception:
            raise InvalidTokenException("Invalid token.")

        username: str = payload.get("sub")
        if username is None:
            raise InvalidTokenException("Token does not contain a subject.")

        user = self.get_user(username)
        if user is None:
            raise AuthException("User not found.")
        
        return User(**user.model_dump())

    @staticmethod
    async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        if current_user.disabled:
            raise AuthException("Inactive user.")
        return current_user

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        return create_access_token(data, expires_delta)
