"""
Authentication service responsible for user authentication and token management.
"""
# import pdb
from typing import Optional
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app.models.user import User, UserInDB
from app.utils.exceptions import AuthException, InvalidTokenException, MissingCredentialsException
from app.utils.hashing import verify_password
from app.utils.jwt_manager import create_access_token, decode_jwt_token
from app.utils.log_manager import logger


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
class AuthService:
    def __init__(self, user_db):
        self.user_db = user_db

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        try:
            user = self.get_user(username)
            if not user or not verify_password(password, user.hashed_password):
                logger.add_log_to_buffer('warning', f"Failed authentication attempt for user: {username}")
                raise AuthException("Invalid username or password.")
            return user
        except AuthException as err:
            logger.add_log_to_buffer('error', f"Authentication error: {str(err)}")
            raise err
        except KeyError:
            logger.add_log_to_buffer('error', f"User not found in the database: {username}")
            raise AuthException("User not found.")

    def get_user(self, username: str) -> Optional[UserInDB]:
        try:
            if not username:
                raise MissingCredentialsException(field_name="username")
            if username in self.user_db:
                user_dict = self.user_db[username]
                return UserInDB(**user_dict)
            return None
        except KeyError as err:
            logger.add_log_to_buffer('error', f"Error retrieving user {username}: {str(err)}")
            return None
        except MissingCredentialsException as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        try:
            payload = decode_jwt_token(token)
            username: str = payload.get("sub")
            if username is None:
                raise InvalidTokenException("Token does not contain a subject.")
        except jwt.ExpiredSignatureError:
            logger.add_log_to_buffer('warning', "Token expired")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except jwt.JWTError:
            logger.add_log_to_buffer('error', "JWT decode error")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except InvalidTokenException as err:
            logger.add_log_to_buffer('error', f"Token validation error: {str(err)}")
            raise err

        try:
            user = self.get_user(username)
            if user is None:
                raise AuthException("User not found.")
            return User(**user.model_dump())
        except AuthException as err:
            logger.add_log_to_buffer('error', f"User not found: {str(err)}")
            raise err

    @staticmethod
    async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
        try:
            if current_user.disabled:
                raise AuthException("Inactive user.")
            return current_user
        except AuthException as err:
            logger.add_log_to_buffer('warning', f"Inactive user access attempt: {str(err)}")
            raise err

    def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
        try:
            return create_access_token(data, expires_delta)
        except Exception as err:
            logger.add_log_to_buffer('error', f"Token creation error: {str(err)}")
            print(err)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token creation failed.")
