"""
Module for password hashing and verification using bcrypt.
"""

from passlib.context import CryptContext


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against its hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt.
    """
    return pwd_context.hash(password)
