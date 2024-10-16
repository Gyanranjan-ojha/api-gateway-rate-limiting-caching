"""
Factory for creating API gateway instances with injected dependencies.
"""

from app.core.request_handler import RequestHandler
from app.services.auth_service import AuthService
from app.services.rate_limit_service import RedisRateLimiter
from app.services.cache_service import RedisCacheService
from app.adapters.redis_adapter import RedisAdapter
from app.services.product_service import ProductService


class GatewayFactory:
    @staticmethod
    def create_gateway(user_db, redis_url):
        redis_adapter = RedisAdapter(redis_url)
        auth_service = AuthService(user_db)
        rate_limit_service = RedisRateLimiter(redis_adapter)
        cache_service = RedisCacheService(redis_adapter)
        product_service = ProductService(redis_adapter)
        
        return RequestHandler(auth_service, rate_limit_service, cache_service, product_service)
