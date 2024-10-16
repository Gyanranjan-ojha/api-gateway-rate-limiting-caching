"""
Caching service for storing and retrieving responses.
"""


from abc import ABC, abstractmethod

from app.adapters.redis_adapter import RedisAdapter


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
        self.redis_adapter.set(key, value, expire=expire_time)

    async def get_cached_response(self, key: str) -> str:
        return self.redis_adapter.get(key)
