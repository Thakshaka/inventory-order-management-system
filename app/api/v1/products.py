"""Product API routes."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductCreate, ProductRead
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(
    payload: ProductCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProductRead:
    service = ProductService(db)
    product = await service.create_product(payload)
    return ProductRead.model_validate(product)


@router.get(
    "",
    response_model=PaginatedResponse[ProductRead],
    status_code=status.HTTP_200_OK,
    summary="List products with pagination",
)
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[
        int,
        Query(ge=1, le=settings.max_page_limit, description="Max items to return"),
    ] = settings.default_page_limit,
    offset: Annotated[
        int,
        Query(ge=0, description="Number of items to skip"),
    ] = 0,
) -> PaginatedResponse[ProductRead]:
    service = ProductService(db)
    result = await service.list_products(limit=limit, offset=offset)
    return PaginatedResponse[ProductRead](
        items=[ProductRead.model_validate(p) for p in result["items"]],
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
    )
