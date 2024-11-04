from unittest.mock import AsyncMock

import pytest

from app.tests.base_test import BaseTest


class TestAuth(BaseTest):
    
    @pytest.mark.asyncio
    async def test_login_for_access_token(self, mock_auth_service):
        # Mock authenticate_user to return a mock user
        mock_auth_service.return_value.authenticate_user.return_value = AsyncMock(username="testuser")

        response = self.client.post("/token", data={"username": "testuser", "password": "password"})
        
        assert response.status_code == 200
        assert "access_token" in response.json()
