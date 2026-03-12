# tests/test_docker_api.py

import pytest
from httpx import AsyncClient
from bson import ObjectId

# ──────────────────────────────────────
#   CONFIG – point to your Docker container
# ──────────────────────────────────────

BASE_URL = "http://localhost:8001"  # Docker container port
DB_NAME = "mystore"
COLLECTION = "items"


@pytest.mark.asyncio
async def test_docker_health_check():
    async with AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_docker_create_and_get_item():
    payload = {
        "name": "Docker Test T-shirt",
        "price": 24.99,
        "size": "L",
        "color": "black",
        "inStock": True,
        "test_source": "docker"
    }

    async with AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Create
        resp_create = await client.post("/items", json=payload)
        assert resp_create.status_code == 201
        created = resp_create.json()
        assert "id" in created
        assert created["name"] == "Docker Test T-shirt"
        assert created["price"] == 24.99
        assert created["test_source"] == "docker"
        item_id = created["id"]

        # Get by id
        resp_get = await client.get(f"/items/{item_id}")
        assert resp_get.status_code == 200
        gotten = resp_get.json()
        assert gotten["id"] == item_id
        assert gotten["name"] == "Docker Test T-shirt"
        assert gotten["test_source"] == "docker"


@pytest.mark.asyncio
async def test_docker_list_items():
    async with AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
        resp = await client.get("/items?limit=5")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)


@pytest.mark.asyncio
async def test_docker_update_item():
    # First create fresh item
    payload = {"product": "Docker Coffee Mug", "price": 15.50, "material": "porcelain", "test_source": "docker"}

    async with AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        create_resp = await client.post("/items", json=payload)
        assert create_resp.status_code == 201
        item_id = create_resp.json()["id"]

        # Update
        update_payload = {
            "price": 17.99,
            "inStock": False,
            "discount": 0.15,
            "test_source": "docker_updated"
        }
        update_resp = await client.put(f"/items/{item_id}", json=update_payload)
        assert update_resp.status_code == 200
        updated = update_resp.json()

        assert updated["price"] == 17.99
        assert updated["inStock"] is False
        assert updated["discount"] == 0.15
        assert updated["material"] == "porcelain"  # unchanged field preserved
        assert updated["test_source"] == "docker_updated"


@pytest.mark.asyncio
async def test_docker_delete_item():
    # Create item to delete
    payload = {"name": "Docker Delete Test", "type": "test", "test_source": "docker"}

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