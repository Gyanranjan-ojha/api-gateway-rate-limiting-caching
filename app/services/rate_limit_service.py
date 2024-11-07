"""
Rate limiting service for controlling request frequency.
"""

from abc import ABC, abstractmethod

from app.adapters.redis_adapter import RedisAdapter
from app.config.settings import api_settings
from app.utils.log_manager import logger

class RateLimiter(ABC):
    @abstractmethod
    async def check_rate_limit(self, client_id: str) -> bool:
        pass

class RedisRateLimiter(RateLimiter):
    def __init__(self, redis_adapter: RedisAdapter):
        self.redis_adapter = redis_adapter
        self.limit = api_settings.RATE_LIMIT
        self.window = api_settings.RATE_LIMIT_WINDOW

    async def check_rate_limit(self, client_id: str) -> bool:
        key = f"rate_limit:{client_id}"
        try:
            count = await self.redis_adapter.get(key)
            
            if count is None: 
                count = 0
                await self.redis_adapter.set(key, str(count), expire=self.window)
            else:
                count = int(count)
            
            count = await self.redis_adapter.incr(key)

            if count == 1:
                await self.redis_adapter.expire(key, self.window)
                
            logger.add_log_to_buffer("info", f"Rate limit check for {client_id}: {count}/{self.limit}")
            
            return count <= self.limit
        except Exception as e:
            print(e)
            logger.add_log_to_buffer("error", f"Error while checking rate limit for {client_id}: {str(e)}")
            return False
