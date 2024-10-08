"""
Module for fake users retrieval.
"""

from api.auth.hashing import get_password_hash


# Fake database for demonstration
fake_users_db = {
    "gyanranjan@gameopedia.com": {
        "username": "gyanranjan@gameopedia.com",
        "full_name": "Gyan Ranjan Ojha",
        "hashed_password": get_password_hash("Gyan@123"),
        "disabled": False,
    }
}
