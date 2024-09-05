"""
Data models for the FastAPI application.
"""

from pydantic import BaseModel


# ____User Data Model for FastAPI____
class User(BaseModel):
    """
    User model representing a user with an id, name, and email.
    """
    id: int  # User ID
    name: str  # User's name
    email: str  # User's email address

# ____Performance: Using Pydantic for Data Validation & Serialization____
# Pydantic models are efficient for both validation and serialization, improving app performance
