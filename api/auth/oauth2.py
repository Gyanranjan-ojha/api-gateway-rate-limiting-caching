"""
Module for OAuth2 configuration and user retrieval.
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from api.auth.jwt_manager import decode_jwt_token
from api.auth.users import get_user


# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user based on the JWT token.
    """
    payload = decode_jwt_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return get_user(username)

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """
    Verifies if the current user is active.
    """
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
