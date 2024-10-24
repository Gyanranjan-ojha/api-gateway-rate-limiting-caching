from unittest.mock import AsyncMock

from app.tests.base_test import BaseTest


class TestAuth(BaseTest):
    def test_login_for_access_token(self, mock_auth_service):
        # Mock authenticate_user to return a mock user
        mock_auth_service.return_value.authenticate_user.return_value = AsyncMock(username="testuser")

        response = self.client.post("/token", data={"username": "testuser", "password": "password"})
        
        # Ensure the token is returned
        assert response.status_code == 200
        assert "access_token" in response.json()
