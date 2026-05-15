// CIP SCADA 系统类型定义

// 清洗状态枚举
export enum CleanState {
  IDLE = 'IDLE',
  READY = 'READY',
  STEP_EXEC = 'STEP_EXEC',
  PAUSE = 'PAUSE',
  FAULT = 'FAULT',
}

// 介质类型枚举
export enum MediaType {
  PURE_WATER = 'PURE_WATER',
  CAUSTIC = 'CAUSTIC',
  ACID = 'ACID',
  HOT_WATER = 'HOT_WATER',
  DISINFECTANT = 'DISINFECTANT',
}

// Zone状态
export interface ZoneStatus {
  zone_id: number;
  zone_name: string;
  state: CleanState;
  current_step: number;
  current_media: MediaType;
  temp_sp: number;
  temp_pv: number;
  temp_reached: boolean;
  flow_pv: number;
  conductivity: number;
  pump_running: boolean;
  step_timer: number;
  step_time_remaining: number;
}

// 系统状态
export interface SystemStatus {
  system_ready: boolean;
  running: boolean;
  all_idle: boolean;
  active_zones: number;
  alarm_count: number;
  queue_count: number;
  timestamp: string;
}

// 报警信息
export interface AlarmInfo {
  alarm_id: number;
  alarm_code: number;
  alarm_text: string;
  level: string;
  zone_id: number;
  zone_name: string;
  trigger_time: string;
  status: 'ACTIVE' | 'ACKED' | 'CLEARED';
}

// 配方信息
export interface RecipeInfo {
  recipe_id: number;
  recipe_name: string;
  description: string;
  step_count: number;
  total_time: number;
  enable: boolean;
}

// 配方步骤
export interface RecipeStep {
  step_no: number;
  media: MediaType;
  duration: number;
  temp_sp: number;
  flow_sp: number;
  conductivity_max: number | null;
}

// 配方详情
export interface RecipeDetail extends RecipeInfo {
  steps: RecipeStep[];
}

// 批次记录
export interface BatchRecord {
  id: number;
  record_id: string;
  zone_id: number;
  zone_name: string;
  recipe_id: number;
  recipe_name: string;
  start_time: string;
  end_time: string;
  total_time: number;
  result: boolean;
  final_conductivity: number;
  fail_reason: string | null;
}

// 控制命令
export interface ControlCommand {
  zone_id: number;
  command: 'START' | 'STOP' | 'PAUSE' | 'RESET' | 'STEP';
}

// WebSocket消息类型
export interface WSMessage {
  type: 'data' | 'alarm' | 'system';
  topic: string;
  timestamp: number;
  values: Record<string, unknown>;
}

// 罐区数据
export interface TankData {
  tank_id: string;
  tank_name: string;
  level: number;
  temp: number;
  conductivity: number;
}

// 设备状态
export interface EquipmentStatus {
  equipment_id: string;
  equipment_name: string;
  running: boolean;
  frequency: number;
  current: number;
}
