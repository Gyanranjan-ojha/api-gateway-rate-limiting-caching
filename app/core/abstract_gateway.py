"""
Abstract base class for API gateway implementations.
"""

from abc import ABC, abstractmethod

from fastapi import Request, Response


class AbstractGateway(ABC):
    @abstractmethod
    async def handle_request(self, request: Request) -> Response:
        pass

    @abstractmethod
    async def authenticate(self, request: Request) -> bool:
        pass

    @abstractmethod
    async def rate_limit(self, request: Request) -> bool:
        pass

    @abstractmethod
    async def cache_response(self, request: Request, response: Response) -> None:
        pass