import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.hgetall = AsyncMock(return_value={
        "zone_name": "Zone-1",
        "state": "IDLE",
        "current_step": "0",
        "current_media": "PURE_WATER",
        "temp_sp": "60.0",
        "temp_pv": "25.0",
        "temp_reached": "false",
        "flow_pv": "0.0",
        "conductivity": "0.0",
        "pump_running": "false",
        "step_timer": "0",
        "step_time_remaining": "0"
    })
    redis_mock.smembers = AsyncMock(return_value={"1", "2"})
    redis_mock.pipeline = MagicMock(return_value=redis_mock)
    redis_mock.delete = AsyncMock()
    redis_mock.hset = AsyncMock()
    redis_mock.expire = AsyncMock()
    redis_mock.execute = AsyncMock()
    return redis_mock


@pytest.fixture
def mock_plc_service():
    plc_mock = AsyncMock()
    plc_mock.connect = AsyncMock(return_value=True)
    plc_mock.disconnect = AsyncMock()
    plc_mock.poll_plc = AsyncMock()
    plc_mock.send_command = AsyncMock(return_value=True)
    plc_mock.start_recipe = AsyncMock(return_value=True)
    plc_mock.connected = True
    return plc_mock


@pytest.fixture
async def client(mock_redis, mock_plc_service):
    with patch('app.core.redis.init_redis', AsyncMock(return_value=mock_redis)), \
         patch('app.core.redis.close_redis', AsyncMock()), \
         patch('app.core.redis.get_redis', AsyncMock(return_value=mock_redis)), \
         patch('app.core.redis.redis_client', mock_redis):

        from app.main import app

        app.state.plc_service = mock_plc_service
        app.state.data_service = AsyncMock()

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
