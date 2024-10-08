"""
Seed module to generate and insert fake product data into Redis for testing.

This file uses Faker to generate random product details and stores them in Redis.
"""

from faker import Faker

from ..logger import logger
from ..rate_limiter import redis_client


fake = Faker()

def generate_fake_product():
    """
    Generate a fake product with random attributes such as name, brand, category, price, etc.
    Utilizes the Faker library for random data generation.
    
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
        "features": ', '.join(fake.sentences(nb=3)),
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

        redis_client.hset(f"product:{i}", mapping=product_data)

    logger.info("1000 fake products seeded into Redis")