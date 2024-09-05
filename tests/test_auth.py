"""
Unit tests for the authentication mechanisms.
Tests include JWT token creation and user authentication logic.
"""

from datetime import timedelta
from api.auth import authenticate_user, create_access_token, fake_users_db

# ____Test JWT Token Creation____
def test_create_access_token():
    """
    Test that a valid JWT token is created upon user authentication.
    """
    user = authenticate_user(fake_users_db, "test@example.com", "password")
    assert user is not None  # Ensure the user is authenticated
    
    token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=30))
    assert token is not None  # Ensure the token is created

# ____Test User Authentication____
def test_authenticate_user():
    """
    Test that a user can be authenticated with valid credentials.
    """
    user = authenticate_user(fake_users_db, "test@example.com", "password")
    assert user.username == "test@example.com"  # Ensure valid authentication

def test_authenticate_invalid_user():
    """
    Test that an invalid user cannot be authenticated.
    """
    user = authenticate_user(fake_users_db, "invalid@example.com", "wrongpassword")
    assert user is False  # Ensure invalid authentication fails
