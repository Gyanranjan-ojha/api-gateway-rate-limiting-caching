"""
Rate limiting service for controlling request frequency.
"""

from abc import ABC, abstractmethod

from app.adapters.redis_adapter import RedisAdapter


class RateLimiter(ABC):
    @abstractmethod
    async def check_rate_limit(self, client_id: str) -> bool:
        pass

class RedisRateLimiter(RateLimiter):
    def __init__(self, redis_adapter: RedisAdapter):
        self.redis_adapter = redis_adapter

    async def check_rate_limit(self, client_id: str) -> bool:
        key = f"rate_limit:{client_id}"
        count = self.redis_adapter.incr(key)
        if count == 1:
            self.redis_adapter.expire(key, 60)  # 1 minute window
        return count <= 3  # 3 requests per minute