"""
Authentication service responsible for user authentication and token management.
"""

from typing import Optional
from datetime import timedelta

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from app.utils.jwt_manager import create_access_token, decode_jwt_token
from app.models.user import User, UserInDB
from app.utils.hashing import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    def __init__(self, user_db):
        self.user_db = user_db
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def get_user(self, username: str) -> Optional[UserInDB]:
        if username in self.user_db:
            user_dict = self.user_db[username]
            return UserInDB(**user_dict)
        return None

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = self.get_user(username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return User(**user.model_dump())

    @staticmethod
    async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        if current_user.disabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        return current_user

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        return create_access_token(data, expires_delta)
