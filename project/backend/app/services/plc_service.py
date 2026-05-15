import snap7
from snap7.util import get_bool, set_bool, get_int, set_int, get_real, set_real
from app.core.config import get_settings
from app.core.redis import get_redis
import asyncio
from datetime import datetime
from typing import Optional

settings = get_settings()


class PLCService:
    def __init__(self):
        self.client: Optional[snap7.client.Client] = None
        self.connected = False
        self.poll_task: Optional[asyncio.Task] = None

        self.db_zone_offset = 100
        self.db_zone_size = 500

        self.zone_state_offsets = {
            'zone_id': 0,
            'state': 2,
            'current_step': 4,
            'current_media': 6,
            'temp_sp': 8,
            'temp_pv': 12,
            'temp_reached': 16,
            'flow_pv': 18,
            'conductivity': 22,
            'pump_running': 26,
            'step_timer': 28,
            'step_time_remaining': 32
        }

    async def connect(self) -> bool:
        try:
            self.client = snap7.client.Client()
            self.client.connect(
                settings.plc_ip,
                settings.plc_rack,
                settings.plc_slot,
                settings.plc_tcp_port
            )
            if self.client.get_connected():
                self.connected = True
                print(f"PLC connected: {settings.plc_ip}")
                return True
        except Exception as e:
            print(f"PLC connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        if self.poll_task:
            self.poll_task.cancel()
            try:
                await self.poll_task
            except asyncio.CancelledError:
                pass
        if self.client:
            self.client.disconnect()
            self.client = None
        self.connected = False

    async def poll_plc(self):
        reconnect_delay = 1.0
        max_reconnect_delay = 60.0
        while self.connected:
            try:
                await self.read_all_zones()
                reconnect_delay = 1.0
                await asyncio.sleep(settings.scada_refresh_interval_ms / 1000.0)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"PLC poll error: {e}")
                reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay)
                await asyncio.sleep(reconnect_delay)

    async def read_all_zones(self):
        redis = await get_redis()
        for zone_id in range(1, settings.scada_zone_count + 1):
            zone_data = await self.read_zone_data(zone_id)
            if zone_data:
                pipe = redis.pipeline()
                key = f"scada:zone:{zone_id}"
                pipe.delete(key)
                pipe.hset(key, mapping=zone_data)
                pipe.expire(key, 10)
                pipe.execute()

    async def read_zone_data(self, zone_id: int) -> dict:
        if not self.connected or not self.client:
            return {}

        try:
            db_number = self.db_zone_offset + zone_id
            data = self.client.db_read(db_number, 0, self.db_zone_size)

            zone_name = f"Zone-{zone_id}"
            state = self._read_int(data, self.zone_state_offsets['state'])
            state_map = {0: "IDLE", 1: "READY", 2: "STEP_EXEC", 3: "STEP_TRANSITION",
                        4: "COMPLETE", 5: "PAUSE", 6: "FAULT"}
            state_str = state_map.get(state, "UNKNOWN")

            media = self._read_int(data, self.zone_state_offsets['current_media'])
            media_map = {0: "PURE_WATER", 1: "ALKALI", 2: "ACID",
                        3: "HOT_WATER", 4: "DISINFECT", 5: "NONE"}
            media_str = media_map.get(media, "NONE")

            return {
                "zone_name": zone_name,
                "state": state_str,
                "current_step": str(self._read_int(data, self.zone_state_offsets['current_step'])),
                "current_media": media_str,
                "temp_sp": str(self._read_real(data, self.zone_state_offsets['temp_sp'])),
                "temp_pv": str(self._read_real(data, self.zone_state_offsets['temp_pv'])),
                "temp_reached": "true" if self._read_bool(data, self.zone_state_offsets['temp_reached'], 0) else "false",
                "flow_pv": str(self._read_real(data, self.zone_state_offsets['flow_pv'])),
                "conductivity": str(self._read_real(data, self.zone_state_offsets['conductivity'])),
                "pump_running": "true" if self._read_bool(data, self.zone_state_offsets['pump_running'], 0) else "false",
                "step_timer": str(self._read_int(data, self.zone_state_offsets['step_timer'])),
                "step_time_remaining": str(self._read_int(data, self.zone_state_offsets['step_time_remaining']))
            }
        except Exception as e:
            print(f"Read zone {zone_id} error: {e}")
            return {}

    def _read_bool(self, data: bytearray, start: int, bit: int) -> bool:
        return get_bool(data, start, bit)

    def _write_bool(self, data: bytearray, start: int, bit: int, value: bool):
        set_bool(data, start, bit, value)

    def _read_int(self, data: bytearray, start: int) -> int:
        return get_int(data, start)

    def _write_int(self, data: bytearray, start: int, value: int):
        set_int(data, start, value)

    def _read_real(self, data: bytearray, start: int) -> float:
        return get_real(data, start)

    def _write_real(self, data: bytearray, start: int, value: float):
        set_real(data, start, value)

    async def send_command(self, zone_id: int, command: str) -> bool:
        if not self.connected or not self.client:
            return False

        if zone_id < 1 or zone_id > settings.scada_zone_count:
            print(f"Invalid zone_id: {zone_id}, must be between 1 and {settings.scada_zone_count}")
            return False

        try:
            db_number = self.db_zone_offset + zone_id
            data = self.client.db_read(db_number, 0, self.db_zone_size)

            cmd_map = {"START": 1, "STOP": 2, "PAUSE": 3, "RESUME": 4, "RESET": 5}
            if command.upper() in cmd_map:
                cmd_value = cmd_map[command.upper()]
                self._write_int(data, 50, cmd_value)
                self.client.db_write(db_number, 0, data)
                return True
            return False
        except Exception as e:
            print(f"Send command error: {e}")
            return False

    async def start_recipe(self, zone_id: int, recipe_id: int) -> bool:
        if not self.connected or not self.client:
            return False

        if recipe_id < 1 or recipe_id > 10:
            print(f"Invalid recipe_id: {recipe_id}, must be between 1 and 10")
            return False

        if zone_id < 1 or zone_id > settings.scada_zone_count:
            print(f"Invalid zone_id: {zone_id}, must be between 1 and {settings.scada_zone_count}")
            return False

        try:
            db_number = self.db_zone_offset + zone_id
            data = self.client.db_read(db_number, 0, self.db_zone_size)

            self._write_int(data, 50, 1)
            self._write_int(data, 52, recipe_id)

            self.client.db_write(db_number, 0, data)
            return True
        except Exception as e:
            print(f"Start recipe error: {e}")
            return False
