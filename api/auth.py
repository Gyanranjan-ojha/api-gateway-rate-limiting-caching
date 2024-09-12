"""
Authentication module for FastAPI using JWT with python-jose.

This file handles user authentication, password hashing, and JWT token creation and verification.
It provides helper functions to verify passwords and manage the authentication lifecycle.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.config import env_settings
from api.models import (
    User,
    UserInDB,
    TokenData,
)

# JWT constants
SECRET_KEY = env_settings.JWT_SECRET.get_secret_value()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Fake database for demonstration
fake_users_db = {
    "test@example.com": {
        "username": "test@example.com",
        "full_name": "Test User",
        "hashed_password": pwd_context.hash("password"),
        "disabled": False,
    }
}


# Helper functions
def verify_password(plain_password, hashed_password):
    """
    Verifies a plain-text password against its hashed version.
    
    Performance: Uses bcrypt hashing, which is secure but computationally expensive by design.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Hashes a plain-text password using bcrypt.
    
    Performance: bcrypt ensures security at the cost of CPU cycles, but is still performant for typical use cases.
    """
    return pwd_context.hash(password)

def get_user(db, username: str):
    """
    Retrieves a user from the mock database.
    
    Performance: Efficient lookup in the mock in-memory database.
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    """
    Authenticates a user by verifying username and password.
    
    Performance: Combines database lookup and password verification.
    """
    user = get_user(fake_db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Creates a JWT token with an expiration date.
    
    Performance: Efficient token generation with python-jose's encode method.
    """
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user based on the JWT token.
    
    Performance: Decodes and validates JWT tokens using python-jose. Token verification is a lightweight operation.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Verifies that the current user is active (not disabled).
    
    Performance: Simple check against user attributes.
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
