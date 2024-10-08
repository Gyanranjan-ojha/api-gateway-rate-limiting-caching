"""
Data models for tokens related.
"""

from typing import Optional

from pydantic import BaseModel


# Pydantic models for structured data
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None