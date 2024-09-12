"""
Data models for the FastAPI application.
"""

from typing import Optional

from pydantic import BaseModel


# ____User Data Model for FastAPI____
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

# Model for new user creation
class CreateUserModel(BaseModel):
    username: str
    full_name: Optional[str] = None
    password: str  # Plaintext password for creation
    disabled: Optional[bool] = False
    
# ____Performance: Using Pydantic for Data Validation & Serialization____
# Pydantic models are efficient for both validation and serialization, improving app performance
