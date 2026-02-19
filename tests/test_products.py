import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_product_success(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/products",
        json={"name": "Laptop Pro", "price": "1299.99", "stock_quantity": 25},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Laptop Pro"
    assert data["price"] == "1299.99"
    assert data["stock_quantity"] == 25
    assert "id" in data
