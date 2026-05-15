from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import random
import os

from app.core.config import get_settings
from app.core.redis import init_redis, close_redis, get_redis
from app.schemas.cip import (
    ZoneStatus, AlarmInfo, RecipeInfo, BatchRecord,
    ZoneControlCommand, RecipeExecuteRequest, SystemStatus
)
from app.services.plc_service import PLCService
from app.services.data_service import DataService

settings = get_settings()

MOCK_MODE = os.environ.get("MOCK_MODE", "true").lower() == "true"

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
]


def get_mock_zones() -> List[ZoneStatus]:
    states = ["IDLE", "READY", "STEP_EXEC", "PAUSE"]
    medias = ["PURE_WATER", "ALKALI", "ACID", "HOT_WATER"]
    zones = []
    for i in range(1, 6):
        state = random.choice(states)
        zones.append(ZoneStatus(
            zone_id=i,
            zone_name=f"Zone-{i}",
            state=state,
            current_step=random.randint(0, 5),
            current_media=random.choice(medias),
            temp_sp=60.0,
            temp_pv=25.0 + random.uniform(0, 40),
            temp_reached=random.choice([True, False]),
            flow_pv=10.0 + random.uniform(0, 20),
            conductivity=5.0 + random.uniform(0, 30),
            pump_running=random.choice([True, False]),
            step_timer=random.randint(0, 300),
            step_time_remaining=random.randint(0, 600)
        ))
    return zones


def build_zone_status(zone_id: int, zone_data: dict) -> ZoneStatus:
    return ZoneStatus(
        zone_id=zone_id,
        zone_name=zone_data.get("zone_name", f"Zone-{zone_id}"),
        state=zone_data.get("state", "IDLE"),
        current_step=int(zone_data.get("current_step", "0")),
        current_media=zone_data.get("current_media", "NONE"),
        temp_sp=float(zone_data.get("temp_sp", "0")),
        temp_pv=float(zone_data.get("temp_pv", "0")),
        temp_reached=zone_data.get("temp_reached", "false").lower() == "true",
        flow_pv=float(zone_data.get("flow_pv", "0")),
        conductivity=float(zone_data.get("conductivity", "0")),
        pump_running=zone_data.get("pump_running", "false").lower() == "true",
        step_timer=int(zone_data.get("step_timer", "0")),
        step_time_remaining=int(zone_data.get("step_time_remaining", "0"))
    )


plc_service_global = None
data_service_global = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global plc_service_global, data_service_global, MOCK_MODE
    
    if MOCK_MODE:
        print("[MOCK] Mode started: using simulated data")
    else:
        try:
            await init_redis()
            plc_service_global = PLCService()
            data_service_global = DataService()
            await plc_service_global.connect()
            app.state.plc_service = plc_service_global
            app.state.data_service = data_service_global
            asyncio.create_task(plc_service_global.poll_plc())
            print("[OK] Real mode started: connected to Redis and PLC")
        except Exception as e:
            print(f"[WARN] Connection failed, switching to Mock mode: {e}")
            MOCK_MODE = True
    yield
    if not MOCK_MODE and plc_service_global:
        await plc_service_global.disconnect()
        await close_redis()
    print("[DISCONNECT] Service stopped")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "status": "running",
        "version": settings.app_version,
        "mock_mode": MOCK_MODE
    }


@app.get("/api/v1/system/status")
async def get_system_status():
    if MOCK_MODE:
        return {
            "system_ready": True,
            "running": True,
            "all_idle": False,
            "active_zones": 2,
            "alarm_count": 0,
            "queue_count": 0,
            "timestamp": datetime.now().isoformat()
        }
    redis = await get_redis()
    all_keys = []
    for zone_id in range(1, settings.scada_zone_count + 1):
        key = f"scada:zone:{zone_id}"
        data = await redis.hgetall(key)
        if data and data.get("state") not in ["IDLE"]:
            all_keys.append(key)
    alarm_keys = await redis.smembers("scada:alarms:active")
    return {
        "system_ready": True,
        "running": len(all_keys) > 0,
        "all_idle": len(all_keys) == 0,
        "active_zones": len(all_keys),
        "alarm_count": len(alarm_keys),
        "queue_count": 0,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/zones", response_model=List[ZoneStatus])
async def get_all_zones():
    if MOCK_MODE:
        return get_mock_zones()
    redis = await get_redis()
    zones = []
    for zone_id in range(1, settings.scada_zone_count + 1):
        zone_data = await redis.hgetall(f"scada:zone:{zone_id}")
        if zone_data:
            zones.append(build_zone_status(zone_id, zone_data))
    return zones


@app.get("/api/v1/zones/{zone_id}", response_model=ZoneStatus)
async def get_zone(zone_id: int):
    if MOCK_MODE:
        zones = get_mock_zones()
        return zones[zone_id - 1] if zone_id <= len(zones) else zones[0]
    if zone_id < 1 or zone_id > settings.scada_zone_count:
        raise HTTPException(status_code=404, detail="Zone not found")
    redis = await get_redis()
    zone_data = await redis.hgetall(f"scada:zone:{zone_id}")
    if not zone_data:
        raise HTTPException(status_code=404, detail="Zone data not found")
    return build_zone_status(zone_id, zone_data)


@app.post("/api/v1/zones/command")
async def send_zone_command(command: ZoneControlCommand):
    if MOCK_MODE:
        return {"status": "ok", "message": f"[Mock] Command {command.command} sent to zone {command.zone_id}"}
    plc_service: PLCService = app.state.plc_service
    success = await plc_service.send_command(command.zone_id, command.command)
    if success:
        return {"status": "ok", "message": f"Command {command.command} sent to zone {command.zone_id}"}
    else:
        raise HTTPException(status_code=500, detail="Failed to send command")


@app.get("/api/v1/alarms", response_model=List[AlarmInfo])
async def get_active_alarms():
    if MOCK_MODE:
        return []
    redis = await get_redis()
    alarm_keys = await redis.smembers("scada:alarms:active")
    alarms = []
    for alarm_key in alarm_keys:
        alarm_data = await redis.hgetall(f"scada:alarm:{alarm_key}")
        if alarm_data:
            alarms.append(AlarmInfo(
                alarm_id=int(alarm_key),
                alarm_code=int(alarm_data.get("alarm_code", "0")),
                alarm_text=alarm_data.get("alarm_text", ""),
                level=alarm_data.get("level", "L3"),
                zone_id=int(alarm_data.get("zone_id", "0")),
                zone_name=f"Zone-{alarm_data.get('zone_id', '0')}",
                trigger_time=alarm_data.get("trigger_time", ""),
                status="ACTIVE"
            ))
    return alarms


@app.get("/api/v1/recipes", response_model=List[RecipeInfo])
async def get_recipes():
    if MOCK_MODE:
        return [
            RecipeInfo(recipe_id=1, recipe_name="快速清洗", description="5分钟快速清洗", step_count=3, total_time=300, enable=True),
            RecipeInfo(recipe_id=2, recipe_name="标准清洗", description="标准CIP清洗", step_count=5, total_time=1800, enable=True),
            RecipeInfo(recipe_id=3, recipe_name="深度清洗", description="深度清洗", step_count=7, total_time=3600, enable=True),
        ]
    redis = await get_redis()
    recipes = []
    for recipe_id in range(1, 11):
        recipe_data = await redis.hgetall(f"scada:recipe:{recipe_id}")
        if recipe_data:
            recipes.append(RecipeInfo(
                recipe_id=int(recipe_data.get("recipe_id", recipe_id)),
                recipe_name=recipe_data.get("recipe_name", f"Recipe {recipe_id}"),
                description=recipe_data.get("description", ""),
                step_count=int(recipe_data.get("step_count", "0")),
                total_time=int(recipe_data.get("total_time", "0")),
                enable=recipe_data.get("enable", "true").lower() == "true"
            ))
    return recipes


@app.post("/api/v1/recipes/execute")
async def execute_recipe(request: RecipeExecuteRequest):
    if MOCK_MODE:
        return {"status": "ok", "message": f"[Mock] Recipe {request.recipe_id} started on zone {request.zone_id}"}
    plc_service: PLCService = app.state.plc_service
    success = await plc_service.start_recipe(request.zone_id, request.recipe_id)
    if success:
        return {"status": "ok", "message": f"Recipe {request.recipe_id} started on zone {request.zone_id}"}
    raise HTTPException(status_code=500, detail="Failed to start recipe")


@app.websocket("/ws/zones")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if MOCK_MODE:
                zones = get_mock_zones()
                await websocket.send_json({
                    "type": "data",
                    "topic": "zone_status",
                    "timestamp": int(datetime.now().timestamp()),
                    "values": {"zones": [z.model_dump() for z in zones]}
                })
            else:
                redis = await get_redis()
                zones_data = []
                for zone_id in range(1, settings.scada_zone_count + 1):
                    zone_data = await redis.hgetall(f"scada:zone:{zone_id}")
                    if zone_data:
                        zones_data.append(build_zone_status(zone_id, zone_data).model_dump())
                await websocket.send_json({
                    "type": "data",
                    "topic": "zone_status",
                    "timestamp": int(datetime.now().timestamp()),
                    "values": {"zones": zones_data}
                })
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
