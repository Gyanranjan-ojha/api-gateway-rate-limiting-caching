"""
Authentication module for FastAPI using JWT with python-jose.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt  # JWT mechanism using python-jose
from passlib.context import CryptContext
from pydantic import BaseModel

from api.config import env_settings


# ____Security Mechanism: JWT____
# Constants for JWT
SECRET_KEY = env_settings.JWT_SECRET.get_secret_value()  # Secure secret key for JWT encryption
ALGORITHM = "HS256"  # Hashing algorithm for token security
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time (performance-related to avoid long-lived tokens)

# Password hashing context (Security-related to avoid plain text passwords)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer token URL (Security: token-based authentication)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock database of users for demonstration purposes (can be replaced with actual DB)
fake_users_db = {
    "test@example.com": {
        "username": "test@example.com",
        "full_name": "Test User",
        "hashed_password": pwd_context.hash("password"),
        "disabled": False,
    }
}

# Pydantic models for structured data
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# ____Security: Password Hashing and Verification____
# Verifies hashed password during authentication (security)
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Hash the password (security-related to prevent plain-text passwords)
def get_password_hash(password):
    return pwd_context.hash(password)

# ____Authentication Logic____
# Function to retrieve user from a mock database (you can switch to a real DB)
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

# Authenticate user with password and database lookup
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# ____Security: JWT Token Creation____
# Create JWT token for user session, ensuring secure and time-limited access
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # Performance: Time-limited session
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default expiration
    to_encode.update({"exp": expire})  # Add expiration to token payload
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Secure token encoding
    return encoded_jwt

# ____Authentication & Security: Token Verification____
# Dependency to get the current user from the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",  # Security: Invalid JWT handling
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode token securely
        username: str = payload.get("sub")  # Extract user info from token
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception  # Handle token validation error
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception  # Security: Reject invalid users
    return user

# ____Security: Active User Check____
# Dependency to ensure the current user is active (not disabled)
async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")  # Security: Prevent disabled users
    return current_user
