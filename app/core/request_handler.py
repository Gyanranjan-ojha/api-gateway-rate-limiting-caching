"""
Concrete implementation of the AbstractGateway for handling API requests.
"""

from fastapi import HTTPException, Request, Response, status

from app.core.abstract_gateway import AbstractGateway
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.services.product_service import ProductService
from app.services.rate_limit_service import RateLimiter
from app.utils.exceptions import (
    InvalidTokenException, 
    RateLimitExceededException, 
    InvalidAPIRequestException,
    ProductNotFoundException,
)
from app.utils.log_manager import logger


class RequestHandler(AbstractGateway):
    def __init__(self, auth_service: AuthService, rate_limit_service: RateLimiter, 
                    cache_service: CacheService, product_service: ProductService):
        self.auth_service = auth_service
        self.rate_limit_service = rate_limit_service
        self.cache_service = cache_service
        self.product_service = product_service

    async def handle_request(self, request: Request) -> Response:
        try:
            if not await self.authenticate(request):
                raise InvalidTokenException("Authentication failed.")

            client_id = request.headers.get("X-Client-ID")
            if not await self.rate_limit(client_id):
                logger.add_log_to_buffer('warning', f"Rate-limit violation for client: {client_id}")
                raise RateLimitExceededException()

            response = await self.process_request(request)

            await self.cache_response(request, response)
            return response

        except (InvalidTokenException, RateLimitExceededException) as e:
            logger.add_log_to_buffer('error', f"Error handling request: {str(e)}")
            return Response(
                content=str(e), 
                status_code=status.HTTP_401_UNAUTHORIZED 
                    if isinstance(e, InvalidTokenException) 
                    else status.HTTP_429_TOO_MANY_REQUESTS,
            )

        except Exception as e:
            logger.add_log_to_buffer('critical', f"Unexpected server error: {str(e)}")
            print(e)
            return Response(content=f"Internal Server Error: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def authenticate(self, request: Request) -> bool:
        token = request.headers.get("Authorization")
        if not token:
            raise InvalidTokenException("Missing authorization header.")
        try:
            await self.auth_service.get_current_user(token.split()[1])
            return True
        except InvalidTokenException as e:
            return Response(content=e.detail, status_code=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response(content=f"Internal server error: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def rate_limit(self, client_id: str) -> bool:
        """
        Checks the rate limit for a given client_id (username).
        Returns True if the request is within the allowed limit, False otherwise.
        """
        return await self.rate_limit_service.check_rate_limit(client_id)

    async def get_product_by_id(self, product_id: int) -> Response:
        try:
            cached_product = await self.cache_service.get_cached_response(f"product:{product_id}")
            if cached_product:
                return Response(content=cached_product, media_type="application/json")

            product = await self.product_service.get_product_by_id(product_id)
            if not product:
                raise ProductNotFoundException(f"Product with ID {product_id} not found.")

            response_content = product.json()
            await self.cache_service.cache_response(f"product:{product_id}", response_content)
            return Response(content=response_content, media_type="application/json")

        except ProductNotFoundException as e:
            logger.add_log_to_buffer("error", str(e))
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        except Exception as e:
            logger.add_log_to_buffer("critical", f"Error in get_product_by_id: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    async def search_products(self, search_query: dict) -> Response:
        try:
            products = await self.product_service.search_products(search_query)
            if not products:
                raise ProductNotFoundException("No matching products found.")

            return Response(content=products.json(), media_type="application/json")

        except ProductNotFoundException as e:
            logger.add_log_to_buffer("error", str(e))
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        except Exception as e:
            logger.add_log_to_buffer("critical", f"Error in search_products: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

    async def cache_response(self, request: Request, response: Response) -> None:
        await self.cache_service.cache_response(request.url.path, response.body)

    async def process_request(self, request: Request) -> Response:
        try:
            cached_response = await self.cache_service.get_cached_response(request.url.path)
            if cached_response:
                return Response(content=cached_response, media_type="application/json")

            if request.method == "GET" and request.url.path.startswith("/products"):
                products = await self.product_service.get_products()
                if not products:
                    raise ProductNotFoundException()
                return Response(content=products.json(), media_type="application/json")

            raise InvalidAPIRequestException()
        
        except ProductNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) 
        
        except InvalidAPIRequestException:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid API request")
        
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{str(e)}")