import pytest

from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.usefixtures("mock_auth_service", "mock_rate_limiter", "mock_cache_service")
class BaseTest:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = TestClient(app)

    @pytest.fixture
    def mock_auth_service(self, mocker):
        return mocker.patch('app.services.auth_service.AuthService', autospec=True)

    @pytest.fixture
    def mock_rate_limiter(self, mocker):
        return mocker.patch('app.services.rate_limit_service.RateLimiter', autospec=True)

    @pytest.fixture
    def mock_cache_service(self, mocker):
        return mocker.patch('app.services.cache_service.RedisCacheService', autospec=True)
