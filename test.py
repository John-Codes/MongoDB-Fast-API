# tests/test_store_api.py

import pytest
from httpx import AsyncClient
from bson import ObjectId

# ──────────────────────────────────────
#   CONFIG – point to your running app
# ──────────────────────────────────────

BASE_URL = "http://localhost:8000"
DB_NAME = "mystore"
COLLECTION = "items"


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_create_and_get_item():
    payload = {
        "name": "Blue T-shirt",
        "price": 19.99,
        "size": "M",
        "color": "navy",
        "inStock": True
    }

    async with AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Create
        resp_create = await client.post("/items", json=payload)
        assert resp_create.status_code == 201
        created = resp_create.json()
        assert "id" in created
        assert created["name"] == "Blue T-shirt"
        assert created["price"] == 19.99
        item_id = created["id"]

        # Get by id
        resp_get = await client.get(f"/items/{item_id}")
        assert resp_get.status_code == 200
        gotten = resp_get.json()
        assert gotten["id"] == item_id
        assert gotten["name"] == "Blue T-shirt"


@pytest.mark.asyncio
async def test_list_items():
    # We assume at least one item exists from previous tests (or seed manually)
    async with AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
        resp = await client.get("/items?limit=5")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        # At minimum we expect something (even empty is ok, but happy path prefers ≥1)
        # If you want stricter: assert len(items) >= 1


@pytest.mark.asyncio
async def test_update_item():
    # First create fresh item
    payload = {"product": "Coffee Mug", "price": 12.50, "material": "ceramic"}

    async with AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        create_resp = await client.post("/items", json=payload)
        assert create_resp.status_code == 201
        item_id = create_resp.json()["id"]

        # Update
        update_payload = {
            "price": 14.99,
            "inStock": False,
            "discount": 0.1
        }
        update_resp = await client.put(f"/items/{item_id}", json=update_payload)
        assert update_resp.status_code == 200
        updated = update_resp.json()

        assert updated["price"] == 14.99
        assert updated["inStock"] is False
        assert updated["discount"] == 0.1
        assert updated["material"] == "ceramic"  # unchanged field preserved


@pytest.mark.asyncio
async def test_delete_item():
    # Create item to delete
    payload = {"name": "To be deleted", "type": "test"}

    async with AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        create_resp = await client.post("/items", json=payload)
        assert create_resp.status_code == 201
        item_id = create_resp.json()["id"]

        # Delete
        delete_resp = await client.delete(f"/items/{item_id}")
        assert delete_resp.status_code == 204

        # Verify gone
        get_resp = await client.get(f"/items/{item_id}")
        assert get_resp.status_code == 404