"""
Main entry point for the FastAPI application.
"""
import uvicorn

from fastapi import FastAPI
from faker import Faker

from api.models import User  # Data model for users
from api.routers import api_router  # Router containing API routes
from api.config import env_settings  # Environment settings


app = FastAPI(debug=env_settings.DEBUG)  # FastAPI app with debug mode based on environment

# ____Router Integration____
# Include your router that handles various endpoints, including rate-limited and cached routes.
app.include_router(api_router)

fake = Faker()  # Faker instance for generating fake data

# ____Performance: Fake Data Generation for Testing/Mocking____
def generate_fake_users(n=10):
    """
    Generate a list of fake users.

    Args:
        n (int): The number of users to generate. Default is 10.

    Returns:
        list[User]: A list of User objects populated with fake data.
    """
    users = []
    for i in range(n):
        user = User(
            id=i,  # Assign incremental IDs
            name=fake.name(),  # Generate a fake name
            email=fake.email()  # Generate a fake email
        )
        users.append(user)
    return users

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
