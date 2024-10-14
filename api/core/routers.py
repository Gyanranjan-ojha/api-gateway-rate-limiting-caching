"""
Router definitions for the FastAPI application with rate limiting, caching, and product data.

This file contains various endpoints, including Redis connectivity check and rate-limited 
of fake generated product data access.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from ..auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from ..caching import CACHE_EXPIRE_TIME
from ..db.fake_db import fake_users_db
from ..models.users import User
from ..logger import logger
from ..rate_limiter_old import redis_client, rate_limiter

api_router = APIRouter(prefix="/api")

# Redis health check route
@api_router.get("/redis_health_check")
async def redis_health_check():
    """
    Health check for Redis connection by attempting to ping the server.
    """
    try:
        redis_client.ping()  # Proper health check by pinging the Redis server
        return {"status": "Redis is working correctly"}
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

    except HTTPException as err:
        if err.status_code == 429:
            logger.warning(f"Rate limit hit for user {current_user.username}.")
            raise err

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