"""
Router definitions for the FastAPI application with rate limiting, caching, and authentication.
"""

import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm  # Import OAuth2PasswordRequestForm
from datetime import timedelta

from api.auth import (
    authenticate_user, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    create_access_token, 
    fake_users_db,
    get_current_active_user, 
    User, 
)
from api.config import env_settings  # Settings for environment variables
from api.main import generate_fake_users  # Fake user generation

# ____Redis Initialization (Caching & Rate Limiting)____
# Initialize Redis connection using environment settings
redis_client = redis.Redis(
    host=env_settings.REDIS_HOST,  # Redis host from environment
    port=env_settings.REDIS_PORT,  # Redis port from environment
    db=0  # Redis database index
)

# Create an API router
api_router = APIRouter()

# ____Rate Limiting Logic with Redis Cache____
def rate_limiter(client_id: str):
    """
    Rate limiter function using Redis. Allows a maximum of 10 requests per minute for each client_id.
    Raises an HTTP 429 error if the limit is exceeded.
    """
    request_count = redis_client.get(client_id)  # Fetch request count from Redis cache
    
    if request_count and int(request_count) >= 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")  # Too many requests (Rate Limiting)
    else:
        redis_client.incr(client_id)  # Increment the request count
        redis_client.expire(client_id, 60)  # Set expiration for 1 minute (Rate limiting timeframe)

# ____Authentication Endpoint: JWT Token Generation____
@api_router.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate the user and return a JWT token.
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)  # Authenticate the user
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Set token expiration duration
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires  # Generate JWT token
    )
    return {"access_token": access_token, "token_type": "bearer"}  # Return JWT token

# ____Secure Route with Rate Limiting and Authentication____
@api_router.get("/users/", dependencies=[Depends(rate_limiter), Depends(get_current_active_user)])
async def get_users(current_user: User = Depends(get_current_active_user)):
    """
    Endpoint to get a list of fake users. Rate-limited to 10 requests per minute.
    Requires JWT authentication.
    """
    users = generate_fake_users()  # Generate fake users (no caching here)
    return users

# ____Cached Route using Redis Cache____
@api_router.get("/cached_users/", dependencies=[Depends(get_current_active_user)])
async def get_cached_users():
    """
    Endpoint to get a cached list of fake users. Caches data in Redis for 60 seconds.
    Requires JWT authentication.
    """
    cached_users = redis_client.get("cached_users")  # Check Redis cache for stored user data
    
    if cached_users:
        return cached_users  # Return cached users if available
    
    users = generate_fake_users()  # Generate new fake users if not cached
    redis_client.set("cached_users", users, ex=60)  # Cache the generated users for 60 seconds
    return users
