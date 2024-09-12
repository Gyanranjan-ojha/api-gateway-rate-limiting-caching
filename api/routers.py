"""
Router definitions for the FastAPI application with rate limiting, caching, and product data.

This file contains endpoints for handling product data, including rate-limited access, caching with Redis,
and a health check for Redis connectivity.
"""

from datetime import timedelta

import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from api.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    # get_password_hash,
    fake_users_db,
    User,
)
from api.config import env_settings
from api.logger import logger
# from api.models import CreateUserModel


# Initialize Redis client for caching and rate-limiting
redis_client = redis.Redis(host=env_settings.REDIS_HOST, port=env_settings.REDIS_PORT, db=0)
api_router = APIRouter()

RATE_LIMIT_TIME = 60  # 1 minutes
CACHE_EXPIRE_TIME = 300  # 5 minutes

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


# Redis health check route
@api_router.get("/redis_health_check")
async def redis_health_check():
    """
    Health check route to verify Redis connectivity by setting and retrieving a test key.
    
    Performance: Simple Redis operations to validate connection status and response times.
    """
    try:
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        if value == b"test_value":
            return {"status": "Redis is working correctly"}
        else:
            raise HTTPException(status_code=500, detail="Redis test failed")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(status_code=500, detail="Redis is not functioning properly")

# Token endpoint for login
@api_router.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate the user and return a JWT token.
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Products route that requires JWT authorization
@api_router.get("/products/")
async def get_products(current_user: User = Depends(get_current_active_user)):
    """
    Rate-limited endpoint to retrieve a list of products.
    Logs when rate limits are hit and when requests are successful.
    """
    try:
        # Apply rate-limiting using the authenticated user's username as client_id
        logger.info(f"User {current_user.username} is attempting to access products.")
        rate_limiter(current_user.username)

        product_list = []
        for i in range(10):  # Fetch 10 products
            product = redis_client.hgetall(f"product:{i}")
            product_list.append({k.decode(): v.decode() for k, v in product.items()})

        logger.info(f"Products successfully fetched for user {current_user.username}")
        return {"products": product_list}

    except HTTPException as e:
        if e.status_code == 429:
            logger.warning(f"Rate limit hit for user {current_user.username}.")
        raise e

# Cached route to get products (cached for 30 minutes)
@api_router.get("/cached_products/")
async def get_cached_products():
    """
    Endpoint to retrieve cached products from Redis.
    Cache duration: 5 minutes.
    """
    # Check if the data is already in cache
    cached_products = redis_client.get("cached_products")
    
    if cached_products:
        logger.info("Cache hit: Returning cached products")
        return {"cached_products": cached_products.decode()}  # Cache found, return it
    
    # If cache is not found (Cache miss)
    logger.info("Cache miss: Fetching fresh products from Redis and caching them for 5 minutes")
    
    products = []
    for i in range(10):
        product = redis_client.hgetall(f"product:{i}")
        products.append({k.decode(): v.decode() for k, v in product.items()})

    # Store the fetched data in the cache for 5 minutes
    redis_client.set("cached_products", str(products), ex=CACHE_EXPIRE_TIME)  # Cache for 5 minutes
    logger.info("Products cached for 5 minutes")
    
    return {"products": products}

# # Admin route to create users
# @api_router.post("/admin/create_user")
# async def create_user(user: CreateUserModel, current_user: User = Depends(get_current_active_user)):
#     """
#     Admin route to create a new user and store it in Redis.
#     """
#     # Only allow admin to create users
#     if current_user.username != "admin@example.com":
#         raise HTTPException(status_code=403, detail="Not enough permissions")

#     # Check if user already exists
#     existing_user = redis_client.hgetall(f"user:{user.username}")
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     # Create new user with hashed password and store it in Redis
#     hashed_password = get_password_hash(user.password)
#     redis_client.hmset(f"user:{user.username}", {
#         "username": user.username,
#         "full_name": user.full_name or "",
#         "hashed_password": hashed_password,
#         "disabled": str(user.disabled)
#     })
#     return {"message": "User created successfully"}
