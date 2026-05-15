import axios from 'axios';
import type {
  ZoneStatus,
  SystemStatus,
  AlarmInfo,
  RecipeInfo,
  RecipeDetail,
  BatchRecord,
  ControlCommand,
} from '@/types';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 系统相关API
export const systemApi = {
  // 获取系统状态
  getStatus: async (): Promise<SystemStatus> => {
    const response = await api.get('/api/v1/system/status');
    return response.data;
  },
};

// Zone相关API
export const zoneApi = {
  // 获取所有Zone状态
  getAllZones: async (): Promise<ZoneStatus[]> => {
    const response = await api.get('/api/v1/zones');
    return response.data;
  },

  // 获取单个Zone状态
  getZone: async (zoneId: number): Promise<ZoneStatus> => {
    const response = await api.get(`/api/v1/zones/${zoneId}`);
    return response.data;
  },

  // 发送控制命令
  sendCommand: async (command: ControlCommand): Promise<{ status: string; message: string }> => {
    const response = await api.post('/api/v1/zones/command', command);
    return response.data;
  },
};

// 报警相关API
export const alarmApi = {
  // 获取活跃报警
  getActiveAlarms: async (): Promise<AlarmInfo[]> => {
    const response = await api.get('/api/v1/alarms');
    return response.data;
  },

  // 确认报警
  ackAlarm: async (alarmId: number, user: string): Promise<boolean> => {
    const response = await api.post(`/api/v1/alarms/${alarmId}/ack`, { user });
    return response.data.status === 'ok';
  },
};

// 配方相关API
export const recipeApi = {
  // 获取所有配方
  getAllRecipes: async (): Promise<RecipeInfo[]> => {
    const response = await api.get('/api/v1/recipes');
    return response.data;
  },

  // 获取配方详情
  getRecipe: async (recipeId: number): Promise<RecipeDetail> => {
    const response = await api.get(`/api/v1/recipes/${recipeId}`);
    return response.data;
  },

  // 执行配方
  executeRecipe: async (zoneId: number, recipeId: number): Promise<{ status: string }> => {
    const response = await api.post('/api/v1/recipes/execute', { zone_id: zoneId, recipe_id: recipeId });
    return response.data;
  },
};

// 批次记录API
export const batchApi = {
  // 获取批次记录
  getBatchRecords: async (params?: {
    zone_id?: number;
    start_time?: string;
    end_time?: string;
    limit?: number;
  }): Promise<BatchRecord[]> => {
    const response = await api.get('/api/v1/batch', { params });
    return response.data;
  },
};

export default api;
