// CIP SCADA 数字孪生3D类型定义

import { CleanState, MediaType } from '@/types';

export { MediaType, CleanState };

// 3D设备基础接口
export interface Device3DProps {
  id: string;
  position: [number, number, number];
  rotation?: [number, number, number];
  scale?: number;
  onClick?: () => void;
  selected?: boolean;
}

// 储罐3D属性
export interface Tank3DProps extends Device3DProps {
  tankId: string;
  tankName: string;
  level: number; // 0-100 液位百分比
  temp: number; // 温度
  conductivity: number; // 电导率
  currentMedia: MediaType;
  state: CleanState;
}

// 泵3D属性
export interface Pump3DProps extends Device3DProps {
  pumpId: string;
  pumpName: string;
  running: boolean;
  frequency: number;
  current: number;
  state: CleanState;
}

// 管道3D属性
export interface Pipeline3DProps {
  id: string;
  startPoint: [number, number, number];
  endPoint: [number, number, number];
  radius?: number;
  mediaType: MediaType;
  flowRate: number;
  active?: boolean;
}

// 阀门3D属性
export interface Valve3DProps extends Device3DProps {
  valveId: string;
  valveName: string;
  open: boolean;
  openPercent: number; // 0-100
  mediaType: MediaType;
}

// 传感器3D属性
export interface SensorIndicator3DProps extends Device3DProps {
  sensorId: string;
  sensorName: string;
  sensorType: 'TT' | 'PT' | 'FT' | 'CD'; // 温度、压力、流量、电导率
  value: number;
  unit: string;
  alarm?: boolean;
  alarmLow?: number;
  alarmHigh?: number;
}

// 清洗介质颜色映射
export const mediaColors: Record<MediaType, string> = {
  [MediaType.PURE_WATER]: '#4FC3F7',     // 浅蓝色 - 纯水
  [MediaType.CAUSTIC]: '#FFB74D',        // 橙色 - 碱液
  [MediaType.ACID]: '#F06292',           // 粉红色 - 酸液
  [MediaType.HOT_WATER]: '#EF5350',       // 红色 - 热水
  [MediaType.DISINFECTANT]: '#66BB6A',    // 绿色 - 消毒液
};

// 状态颜色映射
export const stateColors: Record<CleanState, string> = {
  [CleanState.IDLE]: '#8c8c8c',      // 灰色 - 待机
  [CleanState.READY]: '#1890ff',     // 蓝色 - 就绪
  [CleanState.STEP_EXEC]: '#52c41a', // 绿色 - 清洗中
  [CleanState.PAUSE]: '#faad14',     // 黄色 - 暂停
  [CleanState.FAULT]: '#ff4d4f',     // 红色 - 故障
};

// 介质名称映射
export const mediaText: Record<MediaType, string> = {
  [MediaType.PURE_WATER]: '纯水',
  [MediaType.CAUSTIC]: '碱液',
  [MediaType.ACID]: '酸液',
  [MediaType.HOT_WATER]: '热水',
  [MediaType.DISINFECTANT]: '消毒液',
};

// 状态名称映射
export const stateText: Record<CleanState, string> = {
  [CleanState.IDLE]: '待机',
  [CleanState.READY]: '就绪',
  [CleanState.STEP_EXEC]: '清洗中',
  [CleanState.PAUSE]: '暂停',
  [CleanState.FAULT]: '故障',
};

// CIP系统布局配置
export interface CIPLayoutConfig {
  tanks: Array<{
    id: string;
    name: string;
    position: [number, number, number];
    type: 'raw' | 'clean';
  }>;
  pumps: Array<{
    id: string;
    name: string;
    position: [number, number, number];
    type: 'metering' | 'cleaning';
  }>;
  valves: Array<{
    id: string;
    name: string;
    position: [number, number, number];
    type: 'zone_inlet' | 'zone_outlet' | 'bypass';
  }>;
  pipelines: Array<{
    id: string;
    start: [number, number, number];
    end: [number, number, number];
    type: string;
  }>;
}

// 默认CIP布局（俯视图布局）
export const defaultCIPLLayout: CIPLayoutConfig = {
  tanks: [
    // 原料罐 TT01-04
    { id: 'TT01', name: '原料罐1', position: [-8, 0, -4], type: 'raw' },
    { id: 'TT02', name: '原料罐2', position: [-8, 0, 0], type: 'raw' },
    { id: 'TT03', name: '原料罐3', position: [-8, 0, 4], type: 'raw' },
    { id: 'TT04', name: '原料罐4', position: [-8, 0, 8], type: 'raw' },
    // 清水罐 LT01-04
    { id: 'LT01', name: '清水罐1', position: [8, 0, -4], type: 'clean' },
    { id: 'LT02', name: '清水罐2', position: [8, 0, 0], type: 'clean' },
    { id: 'LT03', name: '清水罐3', position: [8, 0, 4], type: 'clean' },
    { id: 'LT04', name: '清水罐4', position: [8, 0, 8], type: 'clean' },
  ],
  pumps: [
    { id: 'P-CP06', name: '计量泵1', position: [-3, 0, 0], type: 'metering' },
    { id: 'P-CP07', name: '计量泵2', position: [-3, 0, 4], type: 'metering' },
    { id: 'P-CL01', name: '清洗泵', position: [3, 0, 2], type: 'cleaning' },
  ],
  valves: [
    // 计量泵入口阀
    { id: 'V-TT01', name: '原料罐1进液阀', position: [-5.5, 0, -4], type: 'zone_inlet' },
    { id: 'V-TT02', name: '原料罐2进液阀', position: [-5.5, 0, 0], type: 'zone_inlet' },
    { id: 'V-TT03', name: '原料罐3进液阀', position: [-5.5, 0, 4], type: 'zone_inlet' },
    { id: 'V-TT04', name: '原料罐4进液阀', position: [-5.5, 0, 8], type: 'zone_inlet' },
    // 计量泵出口阀
    { id: 'V-CP06', name: '计量泵1出口阀', position: [-1, 0, -1.5], type: 'zone_outlet' },
    { id: 'V-CP07', name: '计量泵2出口阀', position: [-1, 0, 2.5], type: 'zone_outlet' },
    // 清洗回路阀
    { id: 'V-LT01', name: '清水罐1进液阀', position: [5.5, 0, -4], type: 'zone_inlet' },
    { id: 'V-LT02', name: '清水罐2进液阀', position: [5.5, 0, 0], type: 'zone_inlet' },
    { id: 'V-LT03', name: '清水罐3进液阀', position: [5.5, 0, 4], type: 'zone_inlet' },
    { id: 'V-LT04', name: '清水罐4进液阀', position: [5.5, 0, 8], type: 'zone_inlet' },
    // 旁通阀
    { id: 'V-BP01', name: '旁通阀1', position: [0, 0, -3], type: 'bypass' },
    { id: 'V-BP02', name: '旁通阀2', position: [0, 0, 6], type: 'bypass' },
  ],
  pipelines: [
    // 原料罐到计量泵
    { id: 'P-TT01-CP06', start: [-6, 0, -4], end: [-4, 0, -1.5], type: 'raw' },
    { id: 'P-TT02-CP06', start: [-6, 0, 0], end: [-4, 0, -1.5], type: 'raw' },
    { id: 'P-TT03-CP07', start: [-6, 0, 4], end: [-4, 0, 2.5], type: 'raw' },
    { id: 'P-TT04-CP07', start: [-6, 0, 8], end: [-4, 0, 2.5], type: 'raw' },
    // 计量泵到清洗回路
    { id: 'P-CP06-CL01', start: [-1, 0, 0], end: [1, 0, 2], type: 'process' },
    { id: 'P-CP07-CL01', start: [-1, 0, 4], end: [1, 0, 2], type: 'process' },
    // 清洗回路到清水罐
    { id: 'P-CL01-LT01', start: [5, 0, 2], end: [6, 0, -4], type: 'clean' },
    { id: 'P-CL01-LT02', start: [5, 0, 2], end: [6, 0, 0], type: 'clean' },
    { id: 'P-CL01-LT03', start: [5, 0, 2], end: [6, 0, 4], type: 'clean' },
    { id: 'P-CL01-LT04', start: [5, 0, 2], end: [6, 0, 8], type: 'clean' },
    // 旁通管道
    { id: 'P-BP-TOP', start: [-1, 0, -3], end: [1, 0, 6], type: 'bypass' },
  ],
};
