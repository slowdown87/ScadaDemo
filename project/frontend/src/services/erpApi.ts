import axios from 'axios';

export interface ERPProductionPlan {
  plan_id: string;
  product_code: string;
  product_name: string;
  quantity: number;
  unit: string;
  due_date: string;
  priority: number;
  status: 'planned' | 'released' | 'in_production' | 'completed';
  materials: ERPMaterialRequirement[];
}

export interface ERPMaterialRequirement {
  material_code: string;
  material_name: string;
  required_quantity: number;
  available_quantity: number;
  shortage: number;
}

export interface ERPMaterialStock {
  material_code: string;
  material_name: string;
  quantity: number;
  unit: string;
  location: string;
  last_updated: string;
}

export interface ERPWorkOrder {
  order_id: string;
  plan_id: string;
  work_center: string;
  quantity: number;
  planned_hours: number;
  actual_hours: number;
  status: 'released' | 'in_progress' | 'completed' | 'closed';
  start_date: string;
  end_date: string;
}

export interface ERPCostRecord {
  cost_id: string;
  batch_id: string;
  cost_type: 'material' | 'labor' | 'energy' | 'maintenance' | 'other';
  amount: number;
  currency: string;
  description: string;
  record_date: string;
}

const erpApi = axios.create({
  baseURL: import.meta.env.VITE_ERP_API_URL || 'http://localhost:8003/api/erp',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

erpApi.interceptors.request.use((config) => {
  const token = localStorage.getItem('erp_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

erpApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('ERP认证失败，请重新登录');
    }
    return Promise.reject(error);
  }
);

export const productionPlanApi = {
  getPlans: async (params?: {
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<ERPProductionPlan[]> => {
    const response = await erpApi.get('/production-plans', { params });
    return response.data;
  },

  getPlan: async (planId: string): Promise<ERPProductionPlan> => {
    const response = await erpApi.get(`/production-plans/${planId}`);
    return response.data;
  },

  releasePlan: async (planId: string): Promise<void> => {
    await erpApi.post(`/production-plans/${planId}/release`);
  },

  updatePlanStatus: async (
    planId: string,
    status: string
  ): Promise<void> => {
    await erpApi.patch(`/production-plans/${planId}/status`, { status });
  },
};

export const materialApi = {
  getStock: async (params?: {
    material_code?: string;
    location?: string;
  }): Promise<ERPMaterialStock[]> => {
    const response = await erpApi.get('/materials/stock', { params });
    return response.data;
  },

  getMaterial: async (materialCode: string): Promise<ERPMaterialStock> => {
    const response = await erpApi.get(`/materials/${materialCode}`);
    return response.data;
  },

  checkAvailability: async (
    materialCode: string,
    quantity: number
  ): Promise<{ available: boolean; shortage: number }> => {
    const response = await erpApi.post('/materials/check-availability', {
      material_code: materialCode,
      quantity,
    });
    return response.data;
  },

  reserveMaterial: async (
    materialCode: string,
    quantity: number,
    reference: string
  ): Promise<void> => {
    await erpApi.post('/materials/reserve', {
      material_code: materialCode,
      quantity,
      reference,
    });
  },

  releaseMaterial: async (
    materialCode: string,
    quantity: number,
    reference: string
  ): Promise<void> => {
    await erpApi.post('/materials/release', {
      material_code: materialCode,
      quantity,
      reference,
    });
  },
};

export const workOrderApi = {
  getOrders: async (params?: {
    status?: string;
    work_center?: string;
  }): Promise<ERPWorkOrder[]> => {
    const response = await erpApi.get('/work-orders', { params });
    return response.data;
  },

  getOrder: async (orderId: string): Promise<ERPWorkOrder> => {
    const response = await erpApi.get(`/work-orders/${orderId}`);
    return response.data;
  },

  updateProgress: async (
    orderId: string,
    actualHours: number
  ): Promise<void> => {
    await erpApi.patch(`/work-orders/${orderId}/progress`, {
      actual_hours: actualHours,
    });
  },

  completeOrder: async (orderId: string): Promise<void> => {
    await erpApi.post(`/work-orders/${orderId}/complete`);
  },
};

export const costApi = {
  recordCost: async (record: Omit<ERPCostRecord, 'cost_id'>): Promise<void> => {
    await erpApi.post('/costs', record);
  },

  getCosts: async (params?: {
    batch_id?: string;
    cost_type?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<ERPCostRecord[]> => {
    const response = await erpApi.get('/costs', { params });
    return response.data;
  },

  getCostSummary: async (batchId: string): Promise<{
    material_cost: number;
    labor_cost: number;
    energy_cost: number;
    maintenance_cost: number;
    total_cost: number;
  }> => {
    const response = await erpApi.get(`/costs/summary/${batchId}`);
    return response.data;
  },
};

export const erpConfigApi = {
  getConfig: async (): Promise<Record<string, any>> => {
    const response = await erpApi.get('/config');
    return response.data;
  },

  updateConfig: async (config: Record<string, any>): Promise<void> => {
    await erpApi.put('/config', config);
  },

  testConnection: async (): Promise<{ success: boolean; message: string }> => {
    const response = await erpApi.get('/health');
    return response.data;
  },
};

export default erpApi;
