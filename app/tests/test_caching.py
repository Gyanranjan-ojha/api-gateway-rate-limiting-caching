from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.tests.base_test import BaseTest


# Sample product data for testing
sample_product_data = {
    "id": 1,
    "name": "Hubbard, Harris and Morrow field",
    "brand": "Smith, Higgins and Hudson",
    "category": "Printer",
    "price": Decimal('885.25'),
    "stock": 326,
    "sku": "51419d83-18db-4971-a235-3cddcf069811",
    "release_date": "2020-10-08",
    "description": "Magazine ball decade property southern agency.",
    "features": "Citizen black officer difficult push visit argue., See economic party avoid., Food reveal truth hot program sing two safe.",
    "warranty": "3 years",
    "rating": 3.0,
    "dimensions": "46x25x7 cm",
    "weight": "1843 grams",
    "color": "Gold",
    "material": "Plastic"
}

class TestCache(BaseTest):

    @pytest.mark.asyncio
    async def test_cache_hit(self, mock_cache_service, mock_auth_service):
        # Mock cache_service to return cached product data
        mock_cache_service.get_cached_response.return_value = AsyncMock(return_value=[sample_product_data])
        mock_auth_service.return_value.authenticate_user.return_value = AsyncMock(username="testuser")

        response = self.client.get("/cached_products/")
        
        assert response.status_code == 200
        assert response.json() == {"cached_products": [sample_product_data]}

    @pytest.mark.asyncio
    async def test_cache_miss(self, mock_cache_service, mock_auth_service):
        # Mock cache_service to return None (cache miss)
        mock_cache_service.get_cached_response.return_value = AsyncMock(return_value=None)
        mock_auth_service.return_value.authenticate_user.return_value = AsyncMock(username="testuser")

        response = self.client.get("/cached_products/")
        
        assert response.status_code == 200
        assert "products" in response.json()
