"""
Rate limiter module for FastAPI using Redis to limit the rate of client requests.
"""

import redis
from fastapi import HTTPException

from api.config.settings import env_settings
from api.logger import logger


# Initialize Redis client for rate-limiting
redis_client = redis.Redis(
    host=env_settings.REDIS_HOST, 
    port=env_settings.REDIS_PORT, 
    db=0
)

RATE_LIMIT_TIME = 60  # 1 minutes

# Rate limiter using Redis
def rate_limiter(client_id: str):
    """
    Rate limiter using Redis to limit a user to 3 requests per RATE_LIMIT_TIME seconds.
    Logs request counts and when rate limit is exceeded.
    """
    request_count = redis_client.get(client_id)
    
    if request_count:
        logger.info(f"Current request count for {client_id}: {request_count.decode()}")
    else:
        logger.info(f"First request for {client_id}")

    if request_count and int(request_count) >= 3:
        logger.error(f"Rate limit exceeded for {client_id}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    else:
        # Increment the request count for this client and set expiry
        redis_client.incr(client_id)
        redis_client.expire(client_id, RATE_LIMIT_TIME)  # Set expiration to RATE_LIMIT_TIME
        logger.info(f"Incremented request count for {client_id}. New count: {redis_client.get(client_id).decode()}")