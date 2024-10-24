from unittest.mock import AsyncMock

import pytest

from app.tests.base_test import BaseTest


class TestRateLimit(BaseTest):

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, mock_rate_limiter, mock_auth_service):
        # Mock the rate limit check to return False (rate limit exceeded)
        mock_rate_limiter.return_value.check_rate_limit.return_value = AsyncMock(return_value=False)
        mock_auth_service.return_value.authenticate_user.return_value = AsyncMock(username="testuser")

        response = self.client.get("/products/", headers={"Authorization": "Bearer test_token"})
        
        assert response.status_code == 429
        assert response.json()["detail"] == "Rate limit exceeded"
