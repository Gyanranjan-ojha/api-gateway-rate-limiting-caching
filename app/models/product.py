"""
Product-related data models.
"""

from pydantic import BaseModel
from decimal import Decimal
from typing import Optional

class Product(BaseModel):
    id: Optional[int]
    name: str
    brand: str
    category: str
    price: Decimal
    stock: int
    sku: str
    release_date: str
    description: str
    features: str
    warranty: str
    rating: float
    dimensions: str
    weight: str
    color: str
    material: str
