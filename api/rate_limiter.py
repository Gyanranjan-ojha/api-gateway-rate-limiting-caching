"""
Module for rate-limiting API requests.
Provides a `RateLimiter` class to enforce limits on the number of requests within a time period.
"""

import time

from fastapi import HTTPException


class RateLimiter:
    """
    RateLimiter class to manage the number of API requests allowed per user within a specific time period.
    """

    def __init__(self, max_requests: int, period: int):
        self.max_requests = max_requests
        self.period = period
        self.request_count = {}

    def limit(self, user_id: str) -> bool:
        """
        Applies rate-limiting to the specified user.

        :param user_id: Unique identifier for the user
        :return: Boolean indicating whether the user is within the rate limit
        :raises: HTTPException if rate limit is exceeded
        """
        if not user_id:
            raise HTTPException(status_code=400, detail="User ID is missing")

        current_time = time.time()
        
        if user_id not in self.request_count:
            self.request_count[user_id] = {'count': 1, 'start_time': current_time}
        else:
            time_since_start = current_time - self.request_count[user_id]['start_time']
            if time_since_start < self.period:
                self.request_count[user_id]['count'] += 1
            else:
                # Reset count if period has passed
                self.request_count[user_id] = {'count': 1, 'start_time': current_time}

        if self.request_count[user_id]['count'] > self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again later.")

        return True
