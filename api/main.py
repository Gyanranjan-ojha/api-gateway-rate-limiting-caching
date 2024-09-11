"""
Main entry point for the FastAPI application.
"""
import uvicorn

from fastapi import FastAPI

from api.routers import api_router  # Router containing API routes
from api.config import env_settings  # Environment settings


app = FastAPI(debug=env_settings.DEBUG)  # FastAPI app with debug mode based on environment

# ____Router Integration____
# Include your router that handles various endpoints, including rate-limited and cached routes.
app.include_router(api_router)

# ____FastAPI App Entry Point____
if __name__ == "__main__":

    # ____Performance: Use Uvicorn ASGI Server for Serving FastAPI____
    # Run the application with settings from environment variables.
    # Uvicorn is a lightweight ASGI server designed for high-performance apps.
    uvicorn.run(
        app,
        host="0.0.0.0",  # Expose app on all available network interfaces
        port=8000,  # Serve on port 8000
        debug=env_settings.DEBUG  # Debug mode for development
    )
