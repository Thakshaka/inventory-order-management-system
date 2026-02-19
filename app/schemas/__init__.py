"""Schemas package."""
from app.schemas.product import ProductCreate, ProductRead
from app.schemas.order import (
    OrderCreate,
    OrderItemInput,
    OrderItemRead,
    OrderRead,
    OrderStatusUpdate,
)
from app.schemas.common import PaginatedResponse, ErrorDetail

__all__ = [
    "ProductCreate",
    "ProductRead",
    "OrderCreate",
    "OrderItemInput",
    "OrderItemRead",
    "OrderRead",
    "OrderStatusUpdate",
    "PaginatedResponse",
    "ErrorDetail",
]
