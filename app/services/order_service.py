"""Order service — transactional order management with pessimistic locking."""
import logging
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import (
    InsufficientStockError,
    InvalidStatusTransitionError,
    NotFoundError,
)
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.product import Product
from app.schemas.order import OrderCreate

logger = logging.getLogger(__name__)

# Valid status transitions; Shipped and Cancelled are terminal states.
ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: set(),
    OrderStatus.CANCELLED: set(),
}


class OrderService:
    """Encapsulates all order-related database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_order(self, payload: OrderCreate) -> Order:
        """
        Create a new order atomically.

        Products are fetched with SELECT FOR UPDATE (sorted by id to prevent
        deadlocks). All stock is validated before any mutation. On failure the
        transaction rolls back automatically.
        """
        # Aggregate quantities in case the payload contains duplicate product_ids.
        quantity_map: dict[int, int] = defaultdict(int)
        for item in payload.items:
            quantity_map[item.product_id] += item.quantity

        # Sort IDs for consistent lock ordering — prevents deadlocks under concurrency.
        product_ids = sorted(quantity_map.keys())

        result = await self._db.execute(
            select(Product)
            .where(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
        )
        locked_products = result.scalars().all()

        found_ids = {p.id for p in locked_products}
        missing_ids = set(product_ids) - found_ids
        if missing_ids:
            raise NotFoundError("Product", next(iter(missing_ids)))

        # Validate all items before mutating anything to ensure atomicity.
        product_map = {p.id: p for p in locked_products}
        for product_id, requested_qty in quantity_map.items():
            product = product_map[product_id]
            if product.stock_quantity < requested_qty:
                raise InsufficientStockError(
                    product_id=product.id,
                    product_name=product.name,
                    requested=requested_qty,
                    available=product.stock_quantity,
                )

        order = Order(status=OrderStatus.PENDING)
        self._db.add(order)
        await self._db.flush()

        order_items: list[OrderItem] = []
        for product_id, requested_qty in quantity_map.items():
            product = product_map[product_id]
            product.stock_quantity -= requested_qty
            order_items.append(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=requested_qty,
                    price_at_time=product.price,
                )
            )

        self._db.add_all(order_items)
        await self._db.commit()
        await self._db.refresh(order)

        logger.info("Created order id=%d with %d item(s)", order.id, len(order_items))
        return order

    async def get_order(self, order_id: int) -> Order:
        result = await self._db.execute(
            select(Order).where(Order.id == order_id)
        )
        order = result.scalar_one_or_none()
        if order is None:
            raise NotFoundError("Order", order_id)
        return order

    async def list_orders(
        self, limit: int = 10, offset: int = 0
    ) -> dict[str, list[Order] | int]:
        total = await self._db.scalar(select(func.count()).select_from(Order))
        result = await self._db.execute(
            select(Order)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return {
            "items": result.scalars().all(),
            "total": total or 0,
            "limit": limit,
            "offset": offset,
        }

    async def update_order_status(
        self, order_id: int, new_status: OrderStatus
    ) -> Order:
        order = await self.get_order(order_id)

        allowed = ALLOWED_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            raise InvalidStatusTransitionError(
                current=order.status.value,
                requested=new_status.value,
            )

        order.status = new_status
        await self._db.commit()
        await self._db.refresh(order)

        logger.info(
            "Order id=%d status updated: %s → %s",
            order.id,
            order.status.value,
            new_status.value,
        )
        return order
