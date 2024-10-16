"""
Module for fake users retrieval.
"""

from app.utils.hashing import get_password_hash


# Fake database for demonstration
fake_users_db: dict = {
    "gyanranjan@gameopedia.com": {
        "username": "gyanranjan@gameopedia.com",
        "full_name": "Gyan Ranjan Ojha",
        "hashed_password": get_password_hash("Gyan@123"),
        "disabled": False,
    }
}
