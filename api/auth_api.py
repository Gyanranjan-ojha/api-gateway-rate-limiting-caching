"""
Module for handling authenticated API requests.
"""

from api.base_api import BaseAPIRequest
from api.auth.authentication import Authenticator


class AuthenticatedAPIRequest(BaseAPIRequest):
    """
    Class for handling authenticated API requests.
    """

    def __init__(self, token: str):
        """
        Initialize the request with an authentication token.

        :param token: JWT token for authentication
        """
        self.authenticator = Authenticator(token)

    def send(self, request):
        """
        Send an authenticated API request.

        :param request: The API request to be sent
        :raises: Exception if authentication fails
        """
        if self.authenticator.authenticate():
            super().send(request)
        else:
            raise Exception("Authentication failed")
