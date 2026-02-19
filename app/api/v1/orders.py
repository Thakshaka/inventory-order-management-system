"""Order API routes."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.dependencies import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.order import OrderCreate, OrderRead, OrderStatusUpdate
from app.services.order_service import OrderService

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
    description=(
        "Creates an order transactionally using SELECT FOR UPDATE. "
        "Returns 400 on insufficient stock, 404 if any product is not found."
    ),
)
async def create_order(
    payload: OrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrderRead:
    service = OrderService(db)
    order = await service.create_order(payload)
    return OrderRead.model_validate(order)


@router.get(
    "",
    response_model=PaginatedResponse[OrderRead],
    status_code=status.HTTP_200_OK,
    summary="List orders with pagination",
)
async def list_orders(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[
        int,
        Query(ge=1, le=settings.max_page_limit, description="Max items to return"),
    ] = settings.default_page_limit,
    offset: Annotated[
        int,
        Query(ge=0, description="Number of items to skip"),
    ] = 0,
) -> PaginatedResponse[OrderRead]:
    service = OrderService(db)
    result = await service.list_orders(limit=limit, offset=offset)
    return PaginatedResponse[OrderRead](
        items=[OrderRead.model_validate(o) for o in result["items"]],
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
    )


@router.get(
    "/{order_id}",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
    summary="Get order by ID",
)
async def get_order(
    order_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrderRead:
    service = OrderService(db)
    order = await service.get_order(order_id)
    return OrderRead.model_validate(order)


@router.patch(
    "/{order_id}/status",
    response_model=OrderRead,
    status_code=status.HTTP_200_OK,
    summary="Update order status",
    description="Allowed transitions: Pending → Shipped, Pending → Cancelled. All others return 400.",
)
async def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrderRead:
    service = OrderService(db)
    order = await service.update_order_status(order_id, payload.status)
    return OrderRead.model_validate(order)
