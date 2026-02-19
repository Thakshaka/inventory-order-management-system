from typing import Any

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_order_success(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    product_id = sample_product["id"]
    initial_stock = sample_product["stock_quantity"]
    order_qty = 3

    response = await client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product_id, "quantity": order_qty}]},
    )

    assert response.status_code == 201
    order = response.json()
    assert order["status"] == "Pending"
    assert len(order["items"]) == 1
    assert order["items"][0]["product_id"] == product_id
    assert order["items"][0]["quantity"] == order_qty
    assert order["items"][0]["price_at_time"] == sample_product["price"]

    products = (await client.get("/api/v1/products")).json()["items"]
    updated = next(p for p in products if p["id"] == product_id)
    assert updated["stock_quantity"] == initial_stock - order_qty


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    product_id = sample_product["id"]
    initial_stock = sample_product["stock_quantity"]

    response = await client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product_id, "quantity": initial_stock + 1}]},
    )

    assert response.status_code == 400
    error = response.json()
    assert "detail" in error
    assert error["product_id"] == product_id
    assert error["available"] == initial_stock

    products = (await client.get("/api/v1/products")).json()["items"]
    unchanged = next(p for p in products if p["id"] == product_id)
    assert unchanged["stock_quantity"] == initial_stock


@pytest.mark.asyncio
async def test_create_order_partial_failure_full_rollback(client: AsyncClient) -> None:
    """One item over stock — the entire order must roll back, no stock is deducted."""
    r1 = await client.post(
        "/api/v1/products",
        json={"name": "Sufficient", "price": "5.00", "stock_quantity": 100},
    )
    r2 = await client.post(
        "/api/v1/products",
        json={"name": "Scarce", "price": "50.00", "stock_quantity": 1},
    )
    p1, p2 = r1.json(), r2.json()

    response = await client.post(
        "/api/v1/orders",
        json={
            "items": [
                {"product_id": p1["id"], "quantity": 5},
                {"product_id": p2["id"], "quantity": 10},
            ]
        },
    )
    assert response.status_code == 400

    products = {p["id"]: p for p in (await client.get("/api/v1/products")).json()["items"]}
    assert products[p1["id"]]["stock_quantity"] == 100
    assert products[p2["id"]]["stock_quantity"] == 1


@pytest.mark.asyncio
async def test_create_order_product_not_found(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": 99999, "quantity": 1}]},
    )
    assert response.status_code == 404
