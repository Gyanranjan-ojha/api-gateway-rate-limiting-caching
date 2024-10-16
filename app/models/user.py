"""
Data models for users related.
"""

from typing import Optional

from pydantic import BaseModel


# Pydantic models for structured data
class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str