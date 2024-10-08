"""
Module for user authentication and retrieval.
"""

from api.auth.hashing import verify_password
from api.models.users import UserInDB


def get_user(db, username: str):
    """
    Retrieves a user from the mock database.
    
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    """
    Authenticates a user by verifying username and password.
    
    """
    user = get_user(fake_db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user
