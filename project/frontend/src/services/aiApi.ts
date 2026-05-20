import axios from 'axios';

export interface AnomalyResult {
  zone_id: number;
  is_anomaly: boolean;
  overall_score: number;
  confidence: number;
  alarm_level: 'normal' | 'warning' | 'error' | 'critical';
  message: string;
  recommended_action: string;
  detector_results: {
    [key: string]: {
      is_anomaly: boolean;
      anomaly_score: number;
      confidence: number;
      message: string;
    };
  };
  timestamp: string;
}

export interface RULResult {
  zone_id: number;
  equipment_id: string;
  rul_days: number;
  rul_hours: number;
  confidence: number;
  health_status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  maintenance_priority: 'low' | 'medium' | 'high' | 'critical';
  estimated_failure_date: string | null;
  trend: string;
  recommendation: string;
  maintenance_schedule: {
    next_inspection: number;
    maintenance_due: number;
    spare_parts_order: number;
    maintenance_team_alert: boolean;
  };
  risk_assessment: {
    overall_risk: string;
    risk_score: number;
    estimated_downtime: number;
  };
  timestamp: string;
}

export interface EnergyAnalysis {
  batch_id: string;
  total_energy_kwh: number;
  energy_per_batch: number;
  energy_per_hour: number;
  efficiency_score: number;
  recommendations: string[];
  timestamp: string;
}

export interface OptimizationResult {
  zone_id: number;
  current_parameters: Record<string, number>;
  optimized_parameters: Record<string, number>;
  expected_improvement_percent: number;
  confidence: number;
  recommendations: string[];
  timestamp: string;
}

export interface MaintenanceReport {
  report: string;
  markdown: string;
}

const aiApi = axios.create({
  baseURL: import.meta.env.VITE_AI_API_URL || 'http://localhost:8001',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

aiApi.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('AI API Error:', error.message);
    return Promise.reject(error);
  }
);

export const anomalyApi = {
  detect: async (zoneId: number): Promise<AnomalyResult> => {
    const response = await aiApi.get<AnomalyResult>(
      `/api/v1/ai/anomaly/${zoneId}`
    );
    return response.data;
  },

  detectWithData: async (
    zoneId: number,
    sensorData: {
      temperature?: number;
      conductivity?: number;
      flow_rate?: number;
      pressure?: number;
      temperature_rate?: number;
      conductivity_rate?: number;
      flow_rate_rate?: number;
      pressure_rate?: number;
      phase?: string;
    }
  ): Promise<AnomalyResult> => {
    const response = await aiApi.post<AnomalyResult>(
      '/api/v1/ai/anomaly/detect',
      {
        zone_id: zoneId,
        sensor_data: {
          ...sensorData,
          zone_id: zoneId,
        },
      }
    );
    return response.data;
  },
};

export const maintenanceApi = {
  predictRUL: async (
    zoneId: number,
    equipmentId: string,
    options?: {
      equipment_name?: string;
      current_health_score?: number;
      degradation_rate?: number;
    }
  ): Promise<RULResult> => {
    const params = new URLSearchParams({
      zone_id: zoneId.toString(),
      equipment_id: equipmentId,
    });

    if (options?.equipment_name) {
      params.append('equipment_name', options.equipment_name);
    }
    if (options?.current_health_score !== undefined) {
      params.append('current_health_score', options.current_health_score.toString());
    }
    if (options?.degradation_rate !== undefined) {
      params.append('degradation_rate', options.degradation_rate.toString());
    }

    const response = await aiApi.get<RULResult>(
      `/api/v1/ai/maintenance/${zoneId}/equipment/${equipmentId}?${params}`
    );
    return response.data;
  },

  generateReport: async (
    equipmentId: string,
    options?: {
      zone_id?: number;
      equipment_name?: string;
      equipment_type?: string;
      operating_hours?: number;
    }
  ): Promise<MaintenanceReport> => {
    const response = await aiApi.post<MaintenanceReport>(
      `/api/v1/ai/maintenance/equipment/${equipmentId}/report`,
      {
        zone_id: options?.zone_id || 1,
        equipment_name: options?.equipment_name || '清洗泵',
        equipment_type: options?.equipment_type || 'centrifugal_pump',
        operating_hours: options?.operating_hours || 3000,
      }
    );
    return response.data;
  },
};

export const energyApi = {
  analyzeBatch: async (batchId: string): Promise<EnergyAnalysis> => {
    const response = await aiApi.get<EnergyAnalysis>(
      `/api/v1/ai/energy/batch/${batchId}`
    );
    return response.data;
  },
};

export const optimizationApi = {
  getRecommendations: async (
    zoneId: number,
    target?: 'efficiency' | 'quality' | 'speed'
  ): Promise<OptimizationResult> => {
    const params = target ? `?optimization_target=${target}` : '';
    const response = await aiApi.get<OptimizationResult>(
      `/api/v1/ai/optimization/${zoneId}${params}`
    );
    return response.data;
  },

  optimize: async (
    zoneId: number,
    currentParameters: Record<string, number>,
    target: 'efficiency' | 'quality' | 'speed' = 'efficiency'
  ): Promise<OptimizationResult> => {
    const response = await aiApi.post<OptimizationResult>(
      `/api/v1/ai/optimization/${zoneId}`,
      {
        zone_id_body: zoneId,
        current_parameters: currentParameters,
        optimization_target: target,
      }
    );
    return response.data;
  },
};

export const aiHealthApi = {
  checkHealth: async (): Promise<{ status: string; service: string }> => {
    const response = await aiApi.get('/health');
    return response.data;
  },
};

export default aiApi;
