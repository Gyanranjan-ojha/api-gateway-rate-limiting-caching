from unittest.mock import AsyncMock

import pytest

from app.tests.base_test import BaseTest


class TestRateLimit(BaseTest):

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, mock_rate_limiter, mock_auth_service):
        # Set up the mock to return True for the first three calls, then False to trigger rate limiting.
        mock_rate_limiter.return_value.check_rate_limit.side_effect = [True, True, True, False]
        mock_auth_service.return_value.get_current_user = AsyncMock(return_value={"username": "testuser"})

        # Step 1: Obtain token for authorization
        response = self.client.post("/token", data={"username": "testuser", "password": "password"})
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        token = response.json()["access_token"]

        # Step 2: Make three successful requests
        headers = {"Authorization": f"Bearer {token}"}
        for _ in range(3):
            response = self.client.get("/products/", headers=headers)
            assert response.status_code == 200, "Expected status code 200 for the first three requests"

        # Step 3: Make fourth request, expecting a 429 response due to rate limiting
        response = self.client.get("/products/", headers=headers)
        assert response.status_code == 429, f"Expected status code 429, got {response.status_code}"
