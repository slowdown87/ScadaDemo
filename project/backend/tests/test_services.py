import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys


class TestPLCServiceValidation:

    @pytest.fixture
    def plc_service(self):
        settings = MagicMock()
        settings.scada_zone_count = 5
        settings.scada_refresh_interval_ms = 100
        settings.plc_ip = "192.168.2.100"
        settings.plc_rack = 0
        settings.plc_slot = 1
        settings.plc_tcp_port = 102

        with patch.dict('sys.modules', {'snap7': MagicMock()}):
            with patch('app.services.plc_service.get_settings', return_value=settings):
                from app.services.plc_service import PLCService
                service = PLCService()
                service.client = MagicMock()
                service.connected = True
                return service

    @pytest.mark.asyncio
    async def test_send_command_valid(self, plc_service):
        plc_service.client.db_read = MagicMock(return_value=bytearray(500))
        plc_service.client.db_write = MagicMock()

        result = await plc_service.send_command(1, "START")
        assert result is True
        plc_service.client.db_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_command_invalid_zone_id_low(self, plc_service):
        result = await plc_service.send_command(0, "START")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_command_invalid_zone_id_high(self, plc_service):
        result = await plc_service.send_command(99, "START")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_command_disconnected(self, plc_service):
        plc_service.connected = False
        result = await plc_service.send_command(1, "START")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_command_unknown_command(self, plc_service):
        plc_service.client.db_read = MagicMock(return_value=bytearray(500))
        result = await plc_service.send_command(1, "UNKNOWN_CMD")
        assert result is False

    @pytest.mark.asyncio
    async def test_start_recipe_valid(self, plc_service):
        plc_service.client.db_read = MagicMock(return_value=bytearray(500))
        plc_service.client.db_write = MagicMock()

        result = await plc_service.start_recipe(1, 5)
        assert result is True
        plc_service.client.db_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_recipe_invalid_recipe_id_low(self, plc_service):
        result = await plc_service.start_recipe(1, 0)
        assert result is False

    @pytest.mark.asyncio
    async def test_start_recipe_invalid_recipe_id_high(self, plc_service):
        result = await plc_service.start_recipe(1, 99)
        assert result is False

    @pytest.mark.asyncio
    async def test_start_recipe_invalid_zone_id(self, plc_service):
        result = await plc_service.start_recipe(99, 1)
        assert result is False

    @pytest.mark.asyncio
    async def test_start_recipe_disconnected(self, plc_service):
        plc_service.connected = False
        result = await plc_service.start_recipe(1, 1)
        assert result is False
