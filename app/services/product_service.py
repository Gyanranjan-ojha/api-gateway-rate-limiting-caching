"""
Service for managing product-related operations, including seeding fake data.
"""

from faker import Faker

from app.adapters.redis_adapter import RedisAdapter
from app.models.product import Product
from app.utils.exceptions import ProductNotFoundException


fake = Faker()

class ProductService:
    def __init__(self, redis_adapter: RedisAdapter):
        self.redis_adapter = redis_adapter

    async def get_products(self, limit: int = 10) -> list[Product]:
        products = []
        for pid in range(limit):
            product_data = self.redis_adapter.hgetall(f"product:{pid}")
            if product_data:
                product_data["id"] = pid                 
                if 'product_name' in product_data:
                    product_data['name'] = product_data.pop('product_name')

                products.append(Product(**product_data))
        if not products:
            raise ProductNotFoundException()
        return products

    async def create_product(self, product: Product) -> None:
        product_id = self.redis_adapter.incr("product_id_counter")
        product.id = product_id
        self.redis_adapter.hmset(f"product:{product_id}", product.model_dump())

    def generate_fake_product(self) -> dict:
        """
        Generate a fake product with random attributes.
        """
        categories = ["Smartphone", "Laptop", "Tablet", "Smartwatch", "Camera", "Speaker", "Headphones", "Monitor", "Printer"]
        colors = ["Black", "White", "Silver", "Gold", "Blue", "Red"]
        materials = ["Plastic", "Metal", "Glass", "Aluminum", "Carbon Fiber"]

        return {
            "name": f"{fake.company()} {fake.word()}",  # Correct key
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

    async def seed_fake_products(self, num_products: int = 1000) -> None:
        """
        Seed the database with fake products.
        This function resets the product_id_counter and overwrites existing data.
        """
        self.redis_adapter.set("product_id_counter", 0)

        for i in range(num_products):
            product_data = self.generate_fake_product()
            self.redis_adapter.hmset(f"product:{i}", product_data)
        
        print(f"{num_products} fake products seeded into Redis")