"""
Collection of decorators for use in FastAPI applications
"""

import asyncio
from functools import wraps

from fastapi import HTTPException


def timeout(seconds: int):
    """
    Timeout decorator for asynchronous functions.

    Raises a 504 Gateway Timeout error if the function execution exceeds the 
    specified time limit.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise HTTPException(status_code=504, detail="Request timed out")
        return wrapper
    return decorator
