"""
Main entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.adapters.redis_adapter import RedisAdapter
from app.config.settings import api_settings
from app.routes import api_router
from app.services.product_service import ProductService


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_adapter = RedisAdapter(api_settings.REDIS_URL)
    product_service = ProductService(redis_adapter)

    existing_data = await redis_adapter.hgetall("product:1")
    if not existing_data:
        await product_service.seed_fake_products(num_products=1000)

    try:
        yield  # Yield control to the app for its runtime
    finally:
        # Clear rate limit keys when the server stops
        async for key in redis_adapter.redis.scan_iter("rate_limit:*"):
            await redis_adapter.redis.delete(key)

app = FastAPI(lifespan=lifespan)

app.include_router(api_router)
