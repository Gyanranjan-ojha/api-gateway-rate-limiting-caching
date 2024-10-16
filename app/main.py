"""
Main entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.settings import env_settings
from app.services.product_service import ProductService
from app.adapters.redis_adapter import RedisAdapter
from app.routes import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Redis adapter and product service
    redis_adapter = RedisAdapter(env_settings.REDIS_URL)
    product_service = ProductService(redis_adapter)

    # Check if the seed data exists in Redis
    existing_data = redis_adapter.hgetall("product:1")
    if not existing_data:
        # Seed fake products into Redis if they don't already exist
        await product_service.seed_fake_products(num_products=1000)

    yield  # Yield control to the app for its runtime


# Initialize FastAPI app with lifespan event handler
app = FastAPI(lifespan=lifespan)

app.include_router(api_router)



