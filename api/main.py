"""
Main entry point for the FastAPI application.

This file initializes the FastAPI app, integrates API routes, and configures the environment.
It also serves as the entry point for starting the application using Uvicorn, a high-performance ASGI server.
"""

import sys
import os

# Add the root of the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import redis
import uvicorn
from fastapi import FastAPI
from faker import Faker

from api.routers import api_router  # Router containing API routes
from api.config import env_settings  # Environment settings
from api.logger import logger


# FastAPI app initialization with debug mode based on the environment
app = FastAPI(debug=env_settings.DEBUG)

# Router integration
app.include_router(api_router)

# Initialize Redis client for seeding
redis_client = redis.Redis(host=env_settings.REDIS_HOST, port=env_settings.REDIS_PORT, db=0)
fake = Faker()

def generate_fake_product():
    """
    Generate a fake product with random attributes such as name, brand, category, price, etc.
    Utilizes the Faker library for random data generation.
    
    Performance: Optimized for fast random generation, uses Faker's efficient methods to simulate realistic product data.
    """
    categories = ["Smartphone", "Laptop", "Tablet", "Smartwatch", "Camera", "Speaker", "Headphones", "Monitor", "Printer"]
    colors = ["Black", "White", "Silver", "Gold", "Blue", "Red"]
    materials = ["Plastic", "Metal", "Glass", "Aluminum", "Carbon Fiber"]

    return {
        "product_name": f"{fake.company()} {fake.word()}",
        "brand": fake.company(),
        "category": fake.random_element(categories),
        "price": round(fake.random_number(digits=3, fix_len=False) + fake.random_number(digits=2) / 100, 2),
        "stock": fake.random_int(min=0, max=500),
        "sku": fake.uuid4(),
        "release_date": str(fake.date_this_decade()),
        "description": fake.sentence(nb_words=10),
        "features": ', '.join(fake.sentences(nb=3)),  # Convert list to string
        "warranty": f"{fake.random_int(min=1, max=3)} years",
        "rating": round(fake.random_number(digits=1, fix_len=False) / 2 + 2.5, 1),
        "dimensions": f"{fake.random_int(min=5, max=50)}x{fake.random_int(min=5, max=50)}x{fake.random_int(min=1, max=10)} cm",
        "weight": f"{fake.random_int(min=100, max=5000)} grams",
        "color": fake.random_element(colors),
        "material": fake.random_element(materials),
    }


def seed_fake_products():
    """
    Function to seed 1000 fake products into Redis.
    """
    for i in range(1000):
        product_data = generate_fake_product()

        # Ensure product_data is flat, with no nested dictionaries or lists.
        redis_client.hset(f"product:{i}", mapping=product_data)

    logger.info("1000 fake products seeded into Redis")

# FastAPI app entry point
if __name__ == "__main__":

    # If 'seed' argument is provided, seed fake products into Redis
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed_fake_products()
    else:
        # Performance: Use Uvicorn ASGI server for high-performance serving
        uvicorn.run(app, host="0.0.0.0", port=8000)
