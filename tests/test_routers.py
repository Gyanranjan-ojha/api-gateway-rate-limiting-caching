"""
Tests for FastAPI routes, including user retrieval and caching.
Ensures the API endpoints function as expected.
"""

def test_get_users(test_client):
    """
    Test that authenticated requests to /users return a valid response with user data.
    """
    response = test_client.get("/users/", headers={"Authorization": "Bearer your_valid_token_here"})
    assert response.status_code == 200  # Ensure request succeeds
    assert len(response.json()) > 0  # Ensure the response contains users

def test_get_cached_users(test_client):
    """
    Test that authenticated requests to /cached_users return cached data if available.
    """
    response = test_client.get("/cached_users/", headers={"Authorization": "Bearer your_valid_token_here"})
    assert response.status_code == 200  # Ensure request succeeds
    assert len(response.json()) > 0  # Ensure users are returned
