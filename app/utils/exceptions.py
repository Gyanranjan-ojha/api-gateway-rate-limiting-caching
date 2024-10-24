"""
Custom Exception Handling Module for API Gateway.
"""

from fastapi import HTTPException


class AuthException(HTTPException):
    """Raised when authentication fails."""
    def __init__(self, detail: str = "Authentication failed."):
        super().__init__(status_code=401, detail=detail) # 401 Unauthorized

class InvalidTokenException(HTTPException):
    """Raised when the provided JWT token is invalid."""
    def __init__(self, detail: str = "Invalid token."):
        super().__init__(status_code=401, detail=detail) # 401 Unauthorized

class InvalidAPIRequestException(HTTPException):
    """Raised for invalid API requests."""
    def __init__(self, detail: str = "Invalid API request."):
        super().__init__(status_code=400, detail=detail) # 400 Bad Request

class ProductNotFoundException(HTTPException):
    """Raised when the products data not found."""
    def __init__(self, detail: str = "Product not found."):
        super().__init__(status_code=404, detail=detail) # 400 Bad Request

class RateLimitExceededException(HTTPException):
    """Raised when the rate limit is exceeded."""
    def __init__(self, detail: str = "Rate limit exceeded."):
        super().__init__(status_code=429, detail=detail) # 429 Too Many Requests

class RedisConnectionException(HTTPException):
    """Raised when there is a connection issue with Redis."""
    def __init__(self, detail: str = "Failed to connect to Redis."):
        super().__init__(status_code=503, detail=detail) # 503 Service Unavailable