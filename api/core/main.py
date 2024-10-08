"""
Main entry point for the FastAPI application.

This file initializes the FastAPI app, integrates API routes, and configures the environment.
It also serves as the entry point for starting the application using Uvicorn, a high-performance ASGI server.
"""

import sys

import uvicorn
from fastapi import FastAPI

from api.core.routers import api_router
from api.config.settings import env_settings
from api.seed.product_seeder import seed_fake_products


# FastAPI app initialization with debug mode based on the environment
app = FastAPI(debug=env_settings.DEBUG)

# Router integration
app.include_router(api_router)


if __name__ == "__main__":

    # If 'seed' argument is provided, seed fake products into Redis
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed_fake_products()
    else:
        uvicorn.run(app, host="0.0.0.0", port=8000)
