"""
Adapter for Redis operations.
"""

import redis

from app.utils.logger import logger

class RedisAdapter:
    def __init__(self, redis_url: str):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)

    def get(self, key: str) -> str:
        return self.redis.get(key)

    def set(self, key: str, value: str, expire: int = None) -> None:
        self.redis.set(key, value, ex=expire)

    def incr(self, key: str) -> int:
        return self.redis.incr(key)

    def expire(self, key: str, time: int) -> None:
        self.redis.expire(key, time)

    def hgetall(self, key: str) -> dict:
        return self.redis.hgetall(key)

    def hmset(self, key: str, mapping: dict) -> None:
        self.redis.hset(key, mapping=mapping)

    def ping(self) -> bool:
        try:
            return self.redis.ping()
        except Exception as e:
            logger.error(f"Error while checking redis ping: {e}")
            return False

