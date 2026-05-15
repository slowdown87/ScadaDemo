from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class CleanState(str, Enum):
    IDLE = "IDLE"
    READY = "READY"
    STEP_EXEC = "STEP_EXEC"
    STEP_TRANSITION = "STEP_TRANSITION"
    COMPLETE = "COMPLETE"
    PAUSE = "PAUSE"
    FAULT = "FAULT"


class MediaType(str, Enum):
    NONE = "NONE"
    ALKALI = "ALKALI"
    ACID = "ACID"
    HOT_WATER = "HOT_WATER"
    PURE_WATER = "PURE_WATER"
    DISINFECT = "DISINFECT"


class ZoneStatus(BaseModel):
    zone_id: int
    zone_name: str
    state: CleanState
    current_step: int
    current_media: MediaType
    temp_sp: float
    temp_pv: float
    temp_reached: bool
    flow_pv: float
    conductivity: float
    pump_running: bool
    step_timer: int
    step_time_remaining: int


class AlarmInfo(BaseModel):
    alarm_id: int
    alarm_code: int
    alarm_text: str
    level: str
    zone_id: int
    trigger_time: datetime
    ack_time: Optional[datetime] = None
    status: str


class RecipeInfo(BaseModel):
    recipe_id: int
    recipe_name: str
    description: str
    step_count: int
    total_time: int


class RecipeStep(BaseModel):
    step_index: int
    media_id: MediaType
    media_name: str
    target_temp: float
    target_time: int
    target_flow: float


class BatchRecord(BaseModel):
    record_id: str
    zone_id: int
    zone_name: str
    recipe_id: int
    recipe_name: str
    start_time: datetime
    end_time: datetime
    total_time: int
    result: bool
    final_conductivity: float
    fail_reason: Optional[str] = None


class ZoneControlCommand(BaseModel):
    zone_id: int = Field(..., ge=1, le=5)
    command: str = Field(..., description="START, STOP, PAUSE, RESUME, RESET")


class RecipeExecuteRequest(BaseModel):
    zone_id: int = Field(..., ge=1, le=5)
    recipe_id: int = Field(..., ge=1, le=10)


class SystemStatus(BaseModel):
    system_ready: bool
    running: bool
    all_idle: bool
    active_zones: int
    alarm_count: int
    queue_count: int
    timestamp: datetime
