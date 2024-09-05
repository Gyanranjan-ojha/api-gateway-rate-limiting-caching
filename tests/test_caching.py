"""
Tests for caching functionality using Redis.
Ensures that data is cached and retrieved correctly from Redis.
"""

def test_caching(test_client, mock_redis):
    """
    Test that user data is cached in Redis and can be retrieved from the cache.
    """
    # ____Make Request and Cache the Response____
    response = test_client.get("/cached_users/", headers={"Authorization": "Bearer your_valid_token_here"})
    assert response.status_code == 200
    cached_users = mock_redis.get("cached_users")
    assert cached_users is not None  # Ensure that users are cached

    # ____Make Another Request, Should Return Cached Data____
    cached_response = test_client.get("/cached_users/", headers={"Authorization": "Bearer your_valid_token_here"})
    assert cached_response.status_code == 200
