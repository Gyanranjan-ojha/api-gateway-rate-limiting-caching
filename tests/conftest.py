"""
Shared pytest fixtures for the FastAPI application.
Provides reusable configurations like the TestClient and mock Redis instance.
"""

import pytest

from fastapi.testclient import TestClient
from redis import Redis

from api.main import app


# ____Test Client for FastAPI Application (Shared Across Tests)____
@pytest.fixture(scope="module")
def test_client():
    """
    Provides a shared TestClient instance for testing FastAPI routes.
    """
    with TestClient(app) as client:
        yield client

# ____Mock Redis Client for Testing Redis-Related Functionality____
@pytest.fixture(scope="module")
def mock_redis():
    """
    Provides a Redis client for testing caching and rate limiting.
    """
    redis = Redis(host="localhost", port=6379, db=0)
    yield redis
    redis.flushall()  # Cleanup Redis after tests
