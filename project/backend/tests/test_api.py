import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "CIP SCADA Backend"
    assert data["status"] == "running"
    assert "version" in data


@pytest.mark.asyncio
async def test_get_system_status(client):
    response = await client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "system_ready" in data
    assert "running" in data
    assert "all_idle" in data
    assert "active_zones" in data
    assert "alarm_count" in data
    assert "queue_count" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_get_all_zones(client):
    response = await client.get("/api/v1/zones")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


@pytest.mark.asyncio
async def test_get_zone_by_id(client):
    response = await client.get("/api/v1/zones/1")
    assert response.status_code == 200
    data = response.json()
    assert data["zone_id"] == 1
    assert data["zone_name"] == "Zone-1"
    assert data["state"] == "IDLE"


@pytest.mark.asyncio
async def test_get_zone_not_found(client):
    response = await client.get("/api/v1/zones/99")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_zone_invalid_id(client):
    response = await client.get("/api/v1/zones/0")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_zone_command(client, mock_plc_service):
    mock_plc_service.send_command = AsyncMock(return_value=True)
    response = await client.post(
        "/api/v1/zones/command",
        json={"zone_id": 1, "command": "START"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "START" in data["message"]


@pytest.mark.asyncio
async def test_send_zone_command_failure(client, mock_plc_service):
    mock_plc_service.send_command = AsyncMock(return_value=False)
    response = await client.post(
        "/api/v1/zones/command",
        json={"zone_id": 1, "command": "START"}
    )
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_send_zone_command_invalid_zone(client):
    response = await client.post(
        "/api/v1/zones/command",
        json={"zone_id": 99, "command": "START"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_active_alarms(client, mock_redis):
    mock_redis.smembers = AsyncMock(return_value={"1", "2"})
    mock_redis.hgetall = AsyncMock(side_effect=[
        {
            "alarm_code": "1001",
            "alarm_text": "High temperature",
            "level": "L1",
            "zone_id": "1",
            "trigger_time": datetime.now().isoformat(),
            "status": "ACTIVE"
        },
        {
            "alarm_code": "1002",
            "alarm_text": "Low pressure",
            "level": "L2",
            "zone_id": "2",
            "trigger_time": datetime.now().isoformat(),
            "status": "ACTIVE"
        }
    ])

    response = await client.get("/api/v1/alarms")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_recipes(client, mock_redis):
    mock_redis.hgetall = AsyncMock(return_value={
        "recipe_id": "1",
        "recipe_name": "Standard Clean",
        "description": "Default cleaning recipe",
        "step_count": "5",
        "total_time": "1800",
        "enable": "true"
    })

    response = await client.get("/api/v1/recipes")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_execute_recipe(client, mock_plc_service):
    mock_plc_service.start_recipe = AsyncMock(return_value=True)
    response = await client.post(
        "/api/v1/recipes/execute",
        json={"zone_id": 1, "recipe_id": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_execute_recipe_failure(client, mock_plc_service):
    mock_plc_service.start_recipe = AsyncMock(return_value=False)
    response = await client.post(
        "/api/v1/recipes/execute",
        json={"zone_id": 1, "recipe_id": 1}
    )
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_execute_recipe_invalid_recipe_id(client):
    response = await client.post(
        "/api/v1/recipes/execute",
        json={"zone_id": 1, "recipe_id": 99}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_execute_recipe_invalid_zone_id(client):
    response = await client.post(
        "/api/v1/recipes/execute",
        json={"zone_id": 99, "recipe_id": 1}
    )
    assert response.status_code == 422
