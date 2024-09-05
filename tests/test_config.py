"""
Tests for loading environment variables and configurations.
Ensures that environment settings are loaded correctly from the .env file.
"""

from api.config import env_settings

def test_env_config():
    """
    Test that environment variables are loaded correctly from the .env file.
    """
    assert env_settings.JWT_SECRET is not None  # Ensure that JWT secret is loaded
    assert env_settings.REDIS_HOST == "localhost"  # Ensure Redis host is loaded correctly
    assert env_settings.DEBUG == 1  # Ensure debug mode is correctly set
