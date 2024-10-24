"""
Caching service for storing and retrieving responses.
"""

from abc import ABC, abstractmethod

from app.adapters.redis_adapter import RedisAdapter
from app.utils.exceptions import RedisConnectionException
from app.utils.log_manager import logger


class CacheService(ABC):
    @abstractmethod
    async def cache_response(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    async def get_cached_response(self, key: str) -> str:
        pass

class RedisCacheService(CacheService):
    def __init__(self, redis_adapter: RedisAdapter):
        self.redis_adapter = redis_adapter

    async def cache_response(self, key: str, value: str, expire_time: int = 300) -> None:
        """Cache a response with a specified expiration time."""
        try:
            self.redis_adapter.set(key, value, expire=expire_time)
            logger.add_log_to_buffer('info', f"Cached response for key: {key}")
        except Exception as e:
            logger.add_log_to_buffer('error', f"Failed to cache response for key {key}: {str(e)}")
            raise RedisConnectionException("Failed to connect to Redis while caching response.")

    async def get_cached_response(self, key: str) -> str | None:
        """Retrieve a cached response or log a miss."""
        try:
            cached_data = self.redis_adapter.get(key)
            if cached_data:
                logger.add_log_to_buffer('info', f"Cache hit for key: {key}")
                return cached_data
            logger.add_log_to_buffer('info', f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.add_log_to_buffer('error', f"Failed to retrieve cache for key {key}: {str(e)}")
            raise RedisConnectionException("Failed to connect to Redis while retrieving cache.")
