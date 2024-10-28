"""
Module for fake users retrieval.
"""

from app.utils.hashing import get_password_hash
from app.utils.exceptions import UserNotFoundException, UserAlreadyExistsException


class FakeUsersDatabase:
    def __init__(self):
        self.fake_user_db = {
            "gyanranjan@gameopedia.com": {
                "username": "gyanranjan@gameopedia.com",
                "full_name": "Gyan Ranjan Ojha",
                "hashed_password": get_password_hash("Gyan@123"),
                "disabled": False,
            },
            "testuser": {
                "username": "testuser",
                "full_name": "Test User",
                "hashed_password": get_password_hash("password"),
                "disabled": False,
            }
        }

    def get_user(self, username: str):
        """Retrieve a user by username."""
        user = self.fake_user_db.get(username)
        if user is None:
            raise UserNotFoundException(username)
        return user

    def get_all_users(self):
        """Retrieve all users."""
        return self.fake_user_db

    def add_user(self, username: str, full_name: str, password: str):
        """Add a new user to the fake database."""
        if username in self.fake_user_db:
            raise UserAlreadyExistsException(username)
        
        self.fake_user_db[username] = {
            "username": username,
            "full_name": full_name,
            "hashed_password": get_password_hash(password),
            "disabled": False,
        }

fake_users_db = FakeUsersDatabase()