"""
Custom Exception Handling Module for API Gateway.
"""

from fastapi import HTTPException, status


class UserNotFoundException(HTTPException):
    """Raised when a user is not found in the database."""
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User '{username}' not found."
        )

class UserAlreadyExistsException(HTTPException):
    """Raised when trying to add a user that already exists."""
    def __init__(self, username: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"User '{username}' already exists."
        )

class AuthException(HTTPException):
    """Raised when authentication fails."""
    def __init__(self, detail: str = "Authentication failed."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail
        ) 

class InvalidTokenException(HTTPException):
    """Raised when the provided JWT token is invalid."""
    def __init__(self, detail: str = "Invalid token."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=detail
        ) 

class InvalidAPIRequestException(HTTPException):
    """Raised for invalid API requests."""
    def __init__(self, detail: str = "Invalid API request."):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=detail
        )  

class ProductNotFoundException(HTTPException):
    """Raised when the product data is not found."""
    def __init__(self, detail: str = "Product not found."):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=detail
        )  

class RateLimitExceededException(HTTPException):
    """Raised when the rate limit is exceeded."""
    def __init__(self, detail: str = "Rate limit exceeded."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, 
            detail=detail
        )  

class RedisConnectionException(HTTPException):
    """Raised when there is a connection issue with Redis."""
    def __init__(self, detail: str = "Failed to connect to Redis."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=detail
        ) 

class MissingCredentialsException(HTTPException):
    """Raised when a required data field is empty or missing."""
    def __init__(self, field_name: str):
        detail = f"The field '{field_name}' cannot be empty or missing."
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=detail
        )  