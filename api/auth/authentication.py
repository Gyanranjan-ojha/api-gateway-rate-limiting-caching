"""
Module for handling user authentication using JWT tokens.
"""

from fastapi import HTTPException

from api.auth.jwt_manager import decode_jwt_token


class Authenticator:
    """
    Authenticator class to validate JWT tokens and ensure user authentication.
    """

    def __init__(self, token: str):
        self.token = token

    def authenticate(self) -> bool:
        """
        Authenticates the user based on the JWT token.
        
        :return: Boolean indicating whether authentication is successful
        :raises: HTTPException if authentication fails
        """
        if not self.token:
            raise HTTPException(status_code=400, detail="Authentication token is missing")
        
        try:
            payload = decode_jwt_token(self.token)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Token decoding failed: {str(e)}")
        
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return True
