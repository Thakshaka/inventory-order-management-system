"""Product service."""
import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.product import Product
from app.schemas.product import ProductCreate

logger = logging.getLogger(__name__)


class ProductService:
    """Encapsulates all product-related database operations."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_product(self, payload: ProductCreate) -> Product:
        product = Product(
            name=payload.name,
            price=payload.price,
            stock_quantity=payload.stock_quantity,
        )
        self._db.add(product)
        await self._db.commit()
        await self._db.refresh(product)
        logger.info("Created product id=%d name=%r", product.id, product.name)
        return product

    async def get_product_by_id(self, product_id: int) -> Product:
        result = await self._db.execute(
            select(Product).where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        if product is None:
            raise NotFoundError("Product", product_id)
        return product

    async def list_products(
        self, limit: int = 20, offset: int = 0
    ) -> dict[str, Any]:
        count_result = await self._db.execute(select(func.count(Product.id)))
        total: int = count_result.scalar_one()

        data_result = await self._db.execute(
            select(Product)
            .order_by(Product.id)
            .limit(limit)
            .offset(offset)
        )
        products = list(data_result.scalars().all())

        return {"items": products, "total": total, "limit": limit, "offset": offset}
