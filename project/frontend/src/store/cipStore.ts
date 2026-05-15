import { create } from 'zustand';
import type { ZoneStatus, AlarmInfo, RecipeInfo, SystemStatus, CleanState } from '@/types';
import { zoneApi, alarmApi, recipeApi, systemApi, wsService } from '@/services';
import type { WSMessage } from '@/types';

interface CIPState {
  // 数据
  zones: ZoneStatus[];
  alarms: AlarmInfo[];
  recipes: RecipeInfo[];
  systemStatus: SystemStatus | null;
  
  // UI状态
  selectedZones: number[];
  wsConnected: boolean;
  loading: boolean;
  
  // 操作
  fetchZones: () => Promise<void>;
  fetchAlarms: () => Promise<void>;
  fetchRecipes: () => Promise<void>;
  fetchSystemStatus: () => Promise<void>;
  sendCommand: (zoneId: number, command: string) => Promise<boolean>;
  selectZone: (zoneId: number) => void;
  toggleZone: (zoneId: number) => void;
  clearSelection: () => void;
  handleWSMessage: (message: WSMessage) => void;
  setWSConnected: (connected: boolean) => void;
  initialize: () => void;
  cleanup: () => void;
}

export const useCIPStore = create<CIPState>((set, get) => ({
  // 初始状态
  zones: [],
  alarms: [],
  recipes: [],
  systemStatus: null,
  selectedZones: [],
  wsConnected: false,
  loading: false,

  // 获取所有Zone状态
  fetchZones: async () => {
    try {
      const zones = await zoneApi.getAllZones();
      set({ zones });
    } catch (error) {
      console.error('Failed to fetch zones:', error);
    }
  },

  // 获取报警列表
  fetchAlarms: async () => {
    try {
      const alarms = await alarmApi.getActiveAlarms();
      set({ alarms });
    } catch (error) {
      console.error('Failed to fetch alarms:', error);
    }
  },

  // 获取配方列表
  fetchRecipes: async () => {
    try {
      const recipes = await recipeApi.getAllRecipes();
      set({ recipes });
    } catch (error) {
      console.error('Failed to fetch recipes:', error);
    }
  },

  // 获取系统状态
  fetchSystemStatus: async () => {
    try {
      const systemStatus = await systemApi.getStatus();
      set({ systemStatus });
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  },

  // 发送控制命令
  sendCommand: async (zoneId: number, command: string) => {
    try {
      const result = await zoneApi.sendCommand({ zone_id: zoneId, command: command as 'START' | 'STOP' | 'PAUSE' | 'RESET' });
      if (result.status === 'ok') {
        await get().fetchZones();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to send command:', error);
      return false;
    }
  },

  // 选中Zone
  selectZone: (zoneId: number) => {
    set({ selectedZones: [zoneId] });
  },

  // 切换Zone选中状态
  toggleZone: (zoneId: number) => {
    const { selectedZones } = get();
    if (selectedZones.includes(zoneId)) {
      set({ selectedZones: selectedZones.filter((id) => id !== zoneId) });
    } else {
      set({ selectedZones: [...selectedZones, zoneId] });
    }
  },

  // 清除选中
  clearSelection: () => {
    set({ selectedZones: [] });
  },

  // 处理WebSocket消息
  handleWSMessage: (message: WSMessage) => {
    if (message.type === 'data' && message.topic === 'zone_status') {
      const zones = get().zones;
      const updatedZones = zones.map((zone) => {
        const updates = message.values as Partial<ZoneStatus>;
        if (updates.zone_id === zone.zone_id) {
          return { ...zone, ...updates };
        }
        return zone;
      });
      set({ zones: updatedZones });
    } else if (message.type === 'alarm') {
      get().fetchAlarms();
    } else if (message.type === 'system') {
      get().fetchSystemStatus();
    }
  },

  // 设置WebSocket连接状态
  setWSConnected: (connected: boolean) => {
    set({ wsConnected: connected });
  },

  // 初始化
  initialize: () => {
    // 获取初始数据
    get().fetchZones();
    get().fetchAlarms();
    get().fetchRecipes();
    get().fetchSystemStatus();

    // 连接WebSocket
    wsService.connect();
    wsService.subscribe((message) => {
      get().handleWSMessage(message);
    });
  },

  // 清理
  cleanup: () => {
    wsService.disconnect();
  },
}));

export default useCIPStore;
