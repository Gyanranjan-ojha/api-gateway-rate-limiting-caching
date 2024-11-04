"""
Router definitions for the FastAPI application 
"""

# import asyncio
import json
# import pdb
from datetime import timedelta
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from app.adapters.redis_adapter import RedisAdapter
from app.config.settings import env_settings
from app.core.request_handler import RequestHandler
from app.core.gateway_factory import GatewayFactory
from app.db.fake_db import fake_users_db
from app.models.user import User
# from app.models.validation import RequestHeaders, TokenData
from app.services.auth_service import AuthService
from app.utils.decorators import apply_rate_limit, jwt_required, timeout
from app.utils.encoders import DecimalEncoder
from app.utils.exceptions import (
    # InvalidTokenException,
    MissingCredentialsException,
    ProductNotFoundException,
    InvalidAPIRequestException,
)
from app.utils.log_manager import logger


api_router = APIRouter()

def get_redis_adapter() -> RedisAdapter:
    return RedisAdapter(env_settings.REDIS_URL)

def get_gateway(redis_adapter: RedisAdapter = Depends(get_redis_adapter)):
    return GatewayFactory.create_gateway(user_db=fake_users_db.get_all_users(), redis_url=env_settings.REDIS_URL)


@api_router.post("/token", response_model=dict)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request_handler: RequestHandler = Depends(get_gateway)
):
    """
    Authenticate the user and return a JWT token.
    """

    try:
        if 'string' in (form_data.username, form_data.password):
            raise MissingCredentialsException(field_name="username or password")
        
        user = await request_handler.auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

        access_token_expires = timedelta(minutes=60)
        access_token = request_handler.auth_service.create_access_token(
            data={"sub": user.username}, 
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except MissingCredentialsException as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err.detail))


@api_router.get("/products/")
@timeout(10)
@apply_rate_limit(limit=3, window=60)  
@jwt_required(AuthService(fake_users_db.get_all_users())) 
async def get_products(
    request: Request,
    # request_headers: RequestHeaders = Depends(),
    request_handler: RequestHandler = Depends(get_gateway),
    current_user: User = Depends(AuthService(fake_users_db.get_all_users()).get_current_user)
):
    """
    Rate-limited endpoint to retrieve a list of products.
    """
    logger.add_log_to_buffer("info", f"User {current_user.username} is attempting to access products.")
    
    # token = request_headers.authorization.split()[1]
    # try:
    #     TokenData.from_jwt_token(token)
    # except InvalidTokenException as e:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e.detail))

    # await asyncio.sleep(2) # Simulating the delay for timeout response

    try:
        products = await request_handler.product_service.get_products()
        if not products:
            raise ProductNotFoundException(detail="No products available.")
        logger.add_log_to_buffer("info", f"Products successfully fetched for user {current_user.username}")
        return {"products": products}
    except ProductNotFoundException as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.detail)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}.")

@api_router.get("/products/{product_id}/")
@timeout(10)
@apply_rate_limit(limit=3, window=60)
@jwt_required(AuthService(fake_users_db.get_all_users()))
async def get_product_by_product_id(
    request: Request,
    _product_id: int = Query(..., alias="product_id"),
    current_user: User = Depends(AuthService(fake_users_db.get_all_users()).get_current_user),
    request_handler: RequestHandler = Depends(get_gateway),
):
    """
    Rate-limited endpoint to retrieve a product by its ID.
    """
    logger.add_log_to_buffer("info", f"User {current_user.username} is fetching product with ID {_product_id}.")
    # pdb.set_trace()

    try:
        product = await request_handler.product_service.get_product_by_id(_product_id)
        return {"product": product}
    except ProductNotFoundException as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.detail)
    except Exception as e:
        logger.add_log_to_buffer("error", f"Internal server error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.get("/products/search")
@timeout(10)
@apply_rate_limit(limit=3, window=60)
@jwt_required(AuthService(fake_users_db.get_all_users()))
async def search_products(
    request: Request,
    product_name: Optional[str] = Query(None, alias="product_name"),
    category: Optional[str] = Query(None, alias="category"),
    min_price: Optional[float] = Query(None, alias="min_price"),
    max_price: Optional[float] = Query(None, alias="max_price"),
    limit: Optional[int] = Query(10, alias="limit"),  # Default limit of 10
    request_handler: RequestHandler = Depends(get_gateway),
    current_user: User = Depends(AuthService(fake_users_db.get_all_users()).get_current_user),
):
    """
    Rate-limited endpoint to search products based on query parameters.
    """
    search_query = {
        "product_name": product_name,
        "category": category,
        "min_price": min_price,
        "max_price": max_price,
        "limit": limit,
    }
    # Remove any None values
    search_query = {k: v for k, v in search_query.items() if v is not None}
    
    logger.add_log_to_buffer("info", f"User {current_user.username} is searching for products with {search_query}.")

    try:
        products = await request_handler.product_service.search_products(search_query)
        return {"products": products}
    except ProductNotFoundException as err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err.detail)
    except InvalidAPIRequestException as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err.detail)
    except Exception as e:
        logger.add_log_to_buffer("error", f"Internal server error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@api_router.get("/cached_products/")
async def get_cached_products(
    request: Request,
    request_handler: RequestHandler = Depends(get_gateway)
):
    """
    Endpoint to retrieve cached products from Redis.
    Cache duration: 5 minutes.
    """

    cached_products = await request_handler.cache_service.get_cached_response("cached_products")

    if cached_products:
        logger.add_log_to_buffer("info", "Cache hit: Returning cached products")
        return {"cached_products": json.loads(cached_products)}

    logger.add_log_to_buffer("info", "Cache miss: Fetching fresh products from Redis and caching them for 5 minutes")
    products = await request_handler.product_service.get_products()

    product_dicts = [product.model_dump() for product in products]

    await request_handler.cache_service.cache_response(
        "cached_products", 
        json.dumps(product_dicts, cls=DecimalEncoder), 
        expire_time=300
    )
    logger.add_log_to_buffer("info", "Products cached for 5 minutes")

    return {"products": product_dicts}


# @api_router.get("/redis_health_check")
# async def redis_health_check(redis_adapter: RedisAdapter = Depends(get_redis_adapter)):
#     """
#     Health check for Redis connection by attempting to ping the server.
#     """
#     try:
#         is_redis_alive = await redis_adapter.ping()
#         if is_redis_alive:
#             logger.add_log_to_buffer("info", "Redis successfully pinged.")  
#             return {"status": "Redis is working correctly"} 
#         raise HTTPException(status_code=500, detail="Redis ping failed.")
#     except Exception as e:
#         print(e)
#         logger.add_log_to_buffer("error", f"Redis health check failed: {e}") 
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Redis is not functioning properly")
# @api_router.get("/protected-route/")
# async def protected_route(current_user: User = Depends(AuthService(fake_users_db.get_all_users()).get_current_user)):
#     """
#     Protected route that requires a valid JWT token for access.
#     """
#     logger.add_log_to_buffer("info", f"{current_user.username} successfuly authenticated.")
#     return {"message": f"Hello, {current_user.username}!"}