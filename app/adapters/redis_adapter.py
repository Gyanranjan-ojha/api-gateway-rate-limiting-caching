"""
Adapter for Redis operations.
"""

import redis.asyncio as aioredis

from app.utils.log_manager import logger


class RedisAdapter:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True) 

    async def get(self, key: str) -> str:
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = None) -> None:
        await self.redis.set(key, value, ex=expire)

    async def incr(self, key: str) -> int:
        return await self.redis.incr(key)

    async def expire(self, key: str, time: int) -> None:
        await self.redis.expire(key, time)

    async def hgetall(self, key: str) -> dict:
        return await self.redis.hgetall(key)

    async def hmset(self, key: str, mapping: dict) -> None:
        await self.redis.hset(key, mapping=mapping)

    async def ping(self) -> bool:
        try:
            return await self.redis.ping()
        except Exception as e:
            print(e)
            logger.add_log_to_buffer("error", f"Error while checking redis ping: {str(e)}")
            return False