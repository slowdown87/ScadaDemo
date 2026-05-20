import axios from 'axios';
import type { BatchRecord } from '@/types';

export interface MESProductionOrder {
  order_id: string;
  product_code: string;
  product_name: string;
  quantity: number;
  planned_start: string;
  planned_end: string;
  priority: 'normal' | 'urgent' | 'low';
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
}

export interface MESBatchReport {
  batch_id: string;
  order_id: string;
  zone_id: number;
  recipe_id: number;
  recipe_name: string;
  start_time: string;
  end_time: string;
  duration: number;
  status: 'success' | 'partial' | 'failed';
  parameters: {
    temperature_avg: number;
    conductivity_avg: number;
    flow_avg: number;
  };
  quality_result: 'pass' | 'fail' | 'pending';
  operator: string;
}

export interface MESEquipmentStatus {
  equipment_id: string;
  equipment_name: string;
  status: 'available' | 'in_use' | 'maintenance' | 'offline';
  current_order?: string;
  utilization_rate: number;
  oee: number;
}

export interface MESShiftReport {
  shift_id: string;
  shift_name: string;
  date: string;
  production_count: number;
  batch_count: number;
  quality_rate: number;
  utilization_rate: number;
  downtime_minutes: number;
}

const mesApi = axios.create({
  baseURL: import.meta.env.VITE_MES_API_URL || 'http://localhost:8002/api/mes',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

mesApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('mes_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

mesApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('MES认证失败，请重新登录');
    }
    return Promise.reject(error);
  }
);

export const productionOrderApi = {
  getOrders: async (params?: {
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<MESProductionOrder[]> => {
    const response = await mesApi.get('/production-orders', { params });
    return response.data;
  },

  getOrder: async (orderId: string): Promise<MESProductionOrder> => {
    const response = await mesApi.get(`/production-orders/${orderId}`);
    return response.data;
  },

  updateOrderStatus: async (
    orderId: string,
    status: string,
    data?: Record<string, any>
  ): Promise<void> => {
    await mesApi.patch(`/production-orders/${orderId}/status`, {
      status,
      ...data,
    });
  },

  assignOrderToZone: async (
    orderId: string,
    zoneId: number
  ): Promise<void> => {
    await mesApi.post(`/production-orders/${orderId}/assign`, { zone_id: zoneId });
  },
};

export const batchReportApi = {
  submitReport: async (report: MESBatchReport): Promise<void> => {
    await mesApi.post('/batch-reports', report);
  },

  getReports: async (params?: {
    start_date?: string;
    end_date?: string;
    zone_id?: number;
    status?: string;
    limit?: number;
  }): Promise<MESBatchReport[]> => {
    const response = await mesApi.get('/batch-reports', { params });
    return response.data;
  },

  getReport: async (batchId: string): Promise<MESBatchReport> => {
    const response = await mesApi.get(`/batch-reports/${batchId}`);
    return response.data;
  },

  updateQualityResult: async (
    batchId: string,
    result: 'pass' | 'fail' | 'pending'
  ): Promise<void> => {
    await mesApi.patch(`/batch-reports/${batchId}/quality`, { result });
  },
};

export const equipmentApi = {
  getStatus: async (): Promise<MESEquipmentStatus[]> => {
    const response = await mesApi.get('/equipment/status');
    return response.data;
  },

  getEquipment: async (equipmentId: string): Promise<MESEquipmentStatus> => {
    const response = await mesApi.get(`/equipment/${equipmentId}`);
    return response.data;
  },

  updateEquipmentStatus: async (
    equipmentId: string,
    status: string,
    currentOrder?: string
  ): Promise<void> => {
    await mesApi.patch(`/equipment/${equipmentId}/status`, {
      status,
      current_order: currentOrder,
    });
  },
};

export const shiftReportApi = {
  getReports: async (params?: {
    start_date?: string;
    end_date?: string;
    shift_name?: string;
  }): Promise<MESShiftReport[]> => {
    const response = await mesApi.get('/shift-reports', { params });
    return response.data;
  },

  submitReport: async (report: Omit<MESShiftReport, 'shift_id'>): Promise<void> => {
    await mesApi.post('/shift-reports', report);
  },
};

export const mesConfigApi = {
  getConfig: async (): Promise<Record<string, any>> => {
    const response = await mesApi.get('/config');
    return response.data;
  },

  updateConfig: async (config: Record<string, any>): Promise<void> => {
    await mesApi.put('/config', config);
  },

  testConnection: async (): Promise<{ success: boolean; message: string }> => {
    const response = await mesApi.get('/health');
    return response.data;
  },
};

export default mesApi;
