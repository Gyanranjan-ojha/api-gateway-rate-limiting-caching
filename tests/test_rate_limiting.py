"""
Tests for the rate-limiting mechanism using Redis.
Ensures that users are rate-limited after a certain number of requests.
"""

import time

def test_rate_limiting(test_client, mock_redis):
    """
    Test that rate limiting is enforced after 10 requests per minute.
    """
    client_id = "test-client"

    # ____Make 10 Valid Requests with client_id____
    for _ in range(10):
        response = test_client.get(f"/users/?client_id={client_id}", headers={"Authorization": "Bearer your_valid_token_here"})
        assert response.status_code == 200  # Ensure request succeeds

    # ____11th Request Should Fail Due to Rate Limiting____
    response = test_client.get(f"/users/?client_id={client_id}", headers={"Authorization": "Bearer your_valid_token_here"})
    assert response.status_code == 429  # Ensure rate limit exceeded

    # ____Wait for the Rate Limiting Period to Reset____
    time.sleep(60)
    
    # ____Request Should Be Allowed After Limit Reset____
    response = test_client.get(f"/users/?client_id={client_id}", headers={"Authorization": "Bearer your_valid_token_here"})
    assert response.status_code == 200  # Should be allowed after the rate limit reset
