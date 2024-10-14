"""
Module for handling rate-limited API requests.
"""

from api.base_api import BaseAPIRequest
from api.rate_limiter import RateLimiter


class RateLimitedAPIRequest(BaseAPIRequest):
    """
    Class for handling rate-limited API requests using the RateLimiter.
    """

    def __init__(self, rate_limiter: RateLimiter):
        
        self.rate_limiter = rate_limiter

    def send(self, request, user_id: str):
        """
        Send a rate-limited API request.

        :param request: The API request to be sent
        :param user_id: The user ID for rate-limiting purposes
        :raises: Exception if the rate limit is exceeded
        """
        if self.rate_limiter.limit(user_id):
            super().send(request)
        else:
            raise Exception("Rate limit exceeded")
