"""
Concrete implementation of the AbstractGateway for handling API requests.
"""

from fastapi import Request, Response

from app.core.abstract_gateway import AbstractGateway
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.rate_limit_service import RateLimiter
from app.services.cache_service import CacheService

class RequestHandler(AbstractGateway):
    def __init__(self, auth_service: AuthService, rate_limit_service: RateLimiter, 
                    cache_service: CacheService, product_service: ProductService):
        self.auth_service = auth_service
        self.rate_limit_service = rate_limit_service
        self.cache_service = cache_service
        self.product_service = product_service

    async def handle_request(self, request: Request) -> Response:
        if not await self.authenticate(request):
            return Response(content="Unauthorized", status_code=401)
        if not await self.rate_limit(request):
            return Response(content="Rate limit exceeded", status_code=429)

        # Process the request and generate response
        response = await self.process_request(request)

        await self.cache_response(request, response)
        return response

    async def authenticate(self, request: Request) -> bool:
        token = request.headers.get("Authorization")
        if not token:
            return False
        try:
            await self.auth_service.get_current_user(token.split()[1])
            return True
        except Exception:
            return False

    async def rate_limit(self, client_id: str) -> bool:
        """
        Checks the rate limit for a given client_id (username).
        Returns True if the request is within the allowed limit, False otherwise.
        """
        return await self.rate_limit_service.check_rate_limit(client_id)

    async def cache_response(self, request: Request, response: Response) -> None:
        await self.cache_service.cache_response(request.url.path, response.body)

    async def process_request(self, request: Request) -> Response:
        cached_response = await self.cache_service.get_cached_response(request.url.path)
        if cached_response:
            return Response(content=cached_response, media_type="application/json")

        # Route based on the request path and method
        if request.method == "GET" and request.url.path.startswith("/products"):
            products = await self.product_service.get_products()
            return Response(content=products.json(), media_type="application/json")

        return Response(content="Not Found", status_code=404)