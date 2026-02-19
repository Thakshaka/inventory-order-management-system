"""Order Pydantic schemas."""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderItemInput(BaseModel):
    product_id: int = Field(..., gt=0, examples=[1])
    quantity: int = Field(..., ge=1, examples=[3])


class OrderCreate(BaseModel):
    items: list[OrderItemInput] = Field(..., min_length=1)


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    price_at_time: Decimal


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemRead]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus = Field(..., examples=["Shipped"])
