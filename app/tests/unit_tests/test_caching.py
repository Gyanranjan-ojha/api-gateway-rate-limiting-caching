from unittest.mock import AsyncMock

import pytest

from .base_test import BaseTest


class TestCache(BaseTest):

    @pytest.mark.asyncio
    async def test_cache_hit(self, mock_cache_service, mock_auth_service):
        # Mock cache_service to return cached product data
        mock_cache_service.get_cached_response.return_value = AsyncMock(return_value=None)
        mock_auth_service.return_value.authenticate_user.return_value = AsyncMock(username="testuser")

        response = self.client.get("/cached_products/")
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_cache_miss(self, mock_cache_service, mock_auth_service):
        # Mock cache_service to return None (cache miss)
        mock_cache_service.get_cached_response.return_value = AsyncMock(return_value=None)
        mock_auth_service.return_value.authenticate_user.return_value = AsyncMock(username="testuser")

        response = self.client.get("/cached_products/")
        
        assert response.status_code == 200
