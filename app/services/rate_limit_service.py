"""
Rate limiting service for controlling request frequency.
"""

from abc import ABC, abstractmethod

from app.adapters.redis_adapter import RedisAdapter
from app.utils.log_manager import logger

class RateLimiter(ABC):
    @abstractmethod
    async def check_rate_limit(self, client_id: str) -> bool:
        pass

class RedisRateLimiter(RateLimiter):
    def __init__(self, redis_adapter: RedisAdapter, limit: int = 3, window: int = 60):
        self.redis_adapter = redis_adapter
        self.limit = limit
        self.window = window

    async def check_rate_limit(self, client_id: str) -> bool:
        key = f"rate_limit:{client_id}"
        try:
            # Check if the rate limit key exists
            count = await self.redis_adapter.get(key)
            
            if count is None:  # Key does not exist; initialize it
                count = 0
                await self.redis_adapter.set(key, str(count), expire=self.window)
            else:
                count = int(count)
            
            # Increment the rate limit count
            count = await self.redis_adapter.incr(key)

            # Set expiration if this is the first request after reset
            if count == 1:
                await self.redis_adapter.expire(key, self.window)
                
            logger.add_log_to_buffer("info", f"Rate limit check for {client_id}: {count}/{self.limit}")
            
            return count <= self.limit
        except Exception as e:
            print(e)
            logger.add_log_to_buffer("error", f"Error while checking rate limit for {client_id}: {str(e)}")
            return False
