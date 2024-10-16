"""
Router definitions for the FastAPI application with rate limiting, caching, and product data.

This file contains various endpoints, including Redis connectivity check, token authentication,
rate-limited access to product data, and cached product retrieval.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.adapters.redis_adapter import RedisAdapter
from app.config.settings import env_settings
from app.core.request_handler import RequestHandler
from app.core.gateway_factory import GatewayFactory
from app.db.fake_db import fake_users_db
from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.logger import logger


api_router = APIRouter()

def get_redis_adapter() -> RedisAdapter:
    return RedisAdapter(env_settings.REDIS_URL)

def get_gateway(redis_adapter: RedisAdapter = Depends(get_redis_adapter)):
    user_db = fake_users_db
    return GatewayFactory.create_gateway(user_db=user_db, redis_url=env_settings.REDIS_URL)

# Redis health check route
@api_router.get("/redis_health_check")
def redis_health_check(redis_adapter: RedisAdapter = Depends(get_redis_adapter)):
    """
    Health check for Redis connection by attempting to ping the server.
    """
    try:
        is_redis_alive = redis_adapter.ping()
        return {"status": "Redis is working correctly"} if is_redis_alive else HTTPException(status_code=500, detail="Redis ping failed")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(status_code=500, detail="Redis is not functioning properly")

# Token endpoint for login
@api_router.post("/token", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), request_handler: RequestHandler = Depends(get_gateway)
):
    """
    Authenticate the user and return a JWT token.
    """
    user = await request_handler.auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=60)
    access_token = request_handler.auth_service.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/protected-route/")
async def protected_route(current_user: User = Depends(AuthService(fake_users_db).get_current_user)):
    """
    Protected route that requires a valid JWT token for access.
    """
    return {"message": f"Hello, {current_user.username}!"}

# Products route that requires JWT authorization
@api_router.get("/products/")
async def get_products(
    request_handler: RequestHandler = Depends(get_gateway),
    current_user: User = Depends(AuthService(fake_users_db).get_current_user)
):
    """
    Rate-limited endpoint to retrieve a list of products.
    Logs when rate limits are hit and when requests are successful.
    """
    try:
        logger.info(f"User {current_user.username} is attempting to access products.")

        # Apply rate-limiting using the authenticated user's username as client_id
        if not await request_handler.rate_limit(current_user.username):
            logger.warning(f"Rate limit hit for user {current_user.username}.")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        products = await request_handler.product_service.get_products()
        logger.info(f"Products successfully fetched for user {current_user.username}")
        return {"products": products}

    except HTTPException as err:
        if err.status_code == 429:
            logger.warning(f"Rate limit hit for user {current_user.username}.")
            raise err

# Cached route to get products (cached for 5 minutes)
# @api_router.get("/cached_products/")
# async def get_cached_products(
#     request_handler: RequestHandler = Depends(get_gateway)
# ):
#     """
#     Endpoint to retrieve cached products from Redis.
#     Cache duration: 5 minutes.
#     """
#     cached_products = await request_handler.cache_service.get_cached_response("cached_products")

#     if cached_products:
#         logger.info("Cache hit: Returning cached products")
#         return {"cached_products": cached_products}

#     logger.info("Cache miss: Fetching fresh products from Redis and caching them for 5 minutes")
#     products = await request_handler.product_service.get_products()

#     # Store the fetched data in the cache for 5 minutes
#     await request_handler.cache_service.cache_response("cached_products", products, expire_time=300)
#     logger.info("Products cached for 5 minutes")

#     return {"products": products}
