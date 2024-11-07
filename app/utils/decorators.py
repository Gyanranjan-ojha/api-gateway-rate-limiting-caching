"""
Collection of decorators for use in FastAPI applications
"""

import asyncio
from functools import wraps

from fastapi import Request, HTTPException, status

from app.adapters.redis_adapter import RedisAdapter
from app.config.settings import api_settings
from app.core.request_handler import RequestHandler
from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.exceptions import InvalidTokenException, RateLimitExceededException
from app.utils.log_manager import logger
from app.services.rate_limit_service import RedisRateLimiter


def apply_rate_limit(limit: int = 10, window: int = 60):
    """
    Decorator to enforce rate limiting on routes using `current_user.username` as the client_id.
    """
    def decorator(func):
        @wraps(func)
        async def inner(request: Request, current_user: User, request_handler: RequestHandler, *args, **kwargs):
            client_id = current_user.username
            

            redis_adapter = RedisAdapter(api_settings.REDIS_URL)
            rate_limiter = RedisRateLimiter(redis_adapter, limit, window)

            try:
                if not await rate_limiter.check_rate_limit(client_id):
                    logger.add_log_to_buffer("warning", f"Rate limit hit for user: {client_id}.")
                    raise RateLimitExceededException("Rate limit exceeded.")

                logger.add_log_to_buffer("info", f"Rate limit passed for user: {client_id}.")
                
                return await func(request=request, current_user=current_user, request_handler=request_handler, *args, **kwargs)

            except RateLimitExceededException as e:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=f"{e.detail}")
            except Exception as e:
                logger.add_log_to_buffer("critical", f"Unexpected error in rate limiting: {str(e)}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")

        return inner
    return decorator


def jwt_required(auth_service: AuthService):
    """
    Decorator to enforce JWT authentication on routes.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                raise InvalidTokenException("Authorization token is missing.")
            try:
                current_user = await auth_service.get_current_user(token.split()[1])
                kwargs['current_user'] = current_user
                return await func(request, *args, **kwargs)

            except InvalidTokenException as e:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e.detail}")
            except Exception as e:
                print(e)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")
        return wrapper
    return decorator


def timeout(seconds: int):
    """
    Timeout decorator for asynchronous functions.

    Raises a 504 Gateway Timeout error if the function execution exceeds the 
    specified time limit.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request timed out")
        return wrapper
    return decorator
