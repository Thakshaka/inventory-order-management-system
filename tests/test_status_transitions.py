from typing import Any

import pytest
from httpx import AsyncClient


async def _create_order(client: AsyncClient, product: dict[str, Any]) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/orders",
        json={"items": [{"product_id": product["id"], "quantity": 1}]},
    )
    assert response.status_code == 201
    return response.json()


async def _update_status(client: AsyncClient, order_id: int, new_status: str):
    return await client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": new_status},
    )


@pytest.mark.asyncio
async def test_pending_to_shipped(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    order = await _create_order(client, sample_product)
    response = await _update_status(client, order["id"], "Shipped")
    assert response.status_code == 200
    assert response.json()["status"] == "Shipped"


@pytest.mark.asyncio
async def test_terminal_state_rejects_further_transitions(
    client: AsyncClient, sample_product: dict[str, Any]
) -> None:
    order = await _create_order(client, sample_product)
    await _update_status(client, order["id"], "Shipped")

    response = await _update_status(client, order["id"], "Cancelled")
    assert response.status_code == 400
    assert "cannot transition" in response.json()["detail"].lower()
