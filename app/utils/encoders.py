"""
Module defines custom JSON encoders for handling special data types 
that are not natively serializable by the standard JSON encoder in Python
"""
import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """
    Custom JSON encoder for handling Decimal types.
    Converts Decimal objects to float when encoding to JSON.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        return super(DecimalEncoder, self).default(obj)
