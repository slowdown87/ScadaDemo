# CIP清洗系统 - AI增强功能规格

> 文档版本: v1.0
> 创建日期: 2026-05-13
> 工段: CP (CIP Cleaning In Place)
> 用途: 异常检测、预测维护、参数优化、能源管理

---

## 1. 概述

### 1.1 AI增强架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI增强系统架构                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          数据采集层                                       │   │
│  │                                                                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ 实时数据 │  │ 历史数据 │  │ 报警数据 │  │ 设备数据 │              │   │
│  │  │ (Redis) │  │ (SQL)   │  │          │  │          │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          AI服务层                                       │   │
│  │                                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    AI Engine (Python)                              │   │   │
│  │  │                                                                  │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │   │   │
│  │  │  │ 异常检测 │  │ 预测维护 │  │ 参数优化 │  │ 能源优化 │        │   │   │
│  │  │  │(Isolation│  │(LSTM/   │  │(RL/     │  │(Time    │        │   │   │
│  │  │  │ Forest) │  │ Prophet)│  │ Bayesian)│  │ Series) │        │   │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          业务应用层                                     │   │
│  │                                                                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ 实时预警 │  │ 维护计划 │  │ 参数推荐 │  │ 能耗报表 │              │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 AI功能矩阵

| 功能模块 | 算法 | 输入数据 | 输出 | 实时性 |
|----------|------|----------|------|--------|
| **异常检测** | Isolation Forest | 传感器数据 | 异常分数/类型 | **实时** |
| **预测维护** | LSTM / Prophet | 历史故障数据 | 剩余寿命/故障概率 | 定期 |
| **参数优化** | Bayesian Optimization | 清洗效果+参数 | 最优参数推荐 | 定期 |
| **能源优化** | Time Series + RL | 能耗历史+排程 | 最优清洗时间 | 定期 |

---

## 2. 异常检测

### 2.1 检测目标

| 检测类型 | 说明 | 检测指标 |
|----------|------|----------|
| **温度异常** | 温度偏离正常范围 | TT_Outlet, TT_Return |
| **电导率异常** | 电导率异常波动 | CD |
| **流量异常** | 流量异常 | FT |
| **压力异常** | 压力异常 | PT |
| **趋势异常** | 数据趋势偏离 | 多指标组合 |

### 2.2 算法实现

```python
# anomaly_detection.py
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Tuple
import joblib
import os


class AnomalyDetector:
    """基于Isolation Forest的异常检测"""

    def __init__(self, config: Dict):
        self.config = config
        self.model = None
        self.threshold = config.get('threshold', 0.5)
        self.contamination = config.get('contamination', 0.01)
        self.n_estimators = config.get('n_estimators', 100)

    def train(self, historical_data: np.ndarray):
        """训练异常检测模型"""

        # 训练Isolation Forest
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination=self.contamination,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(historical_data)
        print(f"异常检测模型训练完成，使用 {len(historical_data)} 条历史数据")

    def predict(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        预测异常

        Returns:
            scores: 异常分数 (-1=异常, 1=正常)
            anomaly_scores: 异常程度分数 (越负越异常)
        """

        if self.model is None:
            raise ValueError("模型未训练")

        scores = self.model.predict(data)
        anomaly_scores = self.model.score_samples(data)

        return scores, anomaly_scores

    def detect_realtime(
        self,
        zone_id: int,
        current_data: Dict[str, float]
    ) -> Dict:
        """
        实时异常检测

        Args:
            zone_id: 区域ID
            current_data: 当前传感器数据
                {
                    'temp_outlet': 85.2,
                    'temp_return': 72.1,
                    'conductivity': 32.5,
                    'pressure': 0.45,
                    'flow': 5.1
                }

        Returns:
            {
                'is_anomaly': bool,
                'anomaly_score': float,
                'anomaly_type': str,  # 'temperature', 'flow', etc.
                'confidence': float,
                'recommendation': str
            }
        """

        # 构造特征向量
        features = np.array([[
            current_data.get('temp_outlet', 0),
            current_data.get('temp_return', 0),
            current_data.get('conductivity', 0),
            current_data.get('pressure', 0),
            current_data.get('flow', 0)
        ]])

        # 预测
        scores, anomaly_scores = self.predict(features)

        # 判断异常
        is_anomaly = scores[0] == -1
        anomaly_score = float(anomaly_scores[0])

        # 识别异常类型
        anomaly_type = None
        if is_anomaly:
            anomaly_type = self._identify_anomaly_type(
                features[0],
                self.model
            )

        # 生成建议
        recommendation = self._generate_recommendation(
            anomaly_type,
            current_data
        )

        return {
            'zone_id': zone_id,
            'is_anomaly': is_anomaly,
            'anomaly_score': anomaly_score,
            'anomaly_type': anomaly_type,
            'confidence': abs(anomaly_score) / 10,  # 归一化
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }

    def _identify_anomaly_type(
        self,
        features: np.ndarray,
        model
    ) -> str:
        """识别异常类型"""

        # 获取特征重要性 (通过特征贡献度)
        temp_out, temp_ret, cond, press, flow = features

        # 简单规则判断
        if temp_out > 95 or temp_out < 40:
            return 'temperature_high' if temp_out > 95 else 'temperature_low'
        elif flow < 0.5:
            return 'flow_low'
        elif cond > 500:
            return 'conductivity_high'
        elif press > 0.8 or press < 0.1:
            return 'pressure_abnormal'
        else:
            return 'unknown'

    def _generate_recommendation(
        self,
        anomaly_type: str,
        data: Dict
    ) -> str:
        """生成处理建议"""

        recommendations = {
            'temperature_high': '温度过高，建议检查换热器和蒸汽阀',
            'temperature_low': '温度过低，建议检查蒸汽供应',
            'flow_low': '流量过低，建议检查泵和阀门状态',
            'conductivity_high': '电导率异常，建议检查清洗剂浓度',
            'pressure_abnormal': '压力异常，建议检查管路',
            'unknown': '检测到异常，建议现场检查'
        }

        return recommendations.get(anomaly_type, '建议现场检查确认')


# 实时异常检测服务
class RealtimeAnomalyService:
    """实时异常检测服务"""

    def __init__(self, detector: AnomalyDetector):
        self.detector = detector
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.mqtt_client = mqtt.Client()
        self.alarm_threshold = -0.5  # 异常分数阈值

    async def start_monitoring(self, zone_ids: List[int]):
        """启动实时监控"""

        while True:
            for zone_id in zone_ids:
                # 从Redis获取最新数据
                data = await self._get_latest_data(zone_id)

                if data:
                    # 执行异常检测
                    result = self.detector.detect_realtime(zone_id, data)

                    # 异常告警
                    if result['is_anomaly']:
                        await self._trigger_alarm(result)

                    # 更新Redis缓存
                    await self._cache_result(zone_id, result)

            await asyncio.sleep(10)  # 每10秒检测一次

    async def _get_latest_data(self, zone_id: int) -> Dict:
        """获取最新传感器数据"""
        key = f'cip:zone:{zone_id}:latest'
        data = self.redis_client.get(key)

        if data:
            return json.loads(data)
        return None

    async def _trigger_alarm(self, result: Dict):
        """触发报警"""

        alarm = {
            'type': 'ai_anomaly',
            'zone_id': result['zone_id'],
            'alarm_code': 'AI-001',
            'level': 'L1',
            'anomaly_type': result['anomaly_type'],
            'anomaly_score': result['anomaly_score'],
            'recommendation': result['recommendation'],
            'timestamp': result['timestamp']
        }

        # 发布到MQTT
        self.mqtt_client.publish(
            f'cip/zone/{result["zone_id"]}/anomaly',
            json.dumps(alarm)
        )

        # 存储到数据库
        await self._save_alarm(alarm)
```

---

## 3. 预测维护

### 3.1 预测目标

| 预测项目 | 说明 | 预测时间 |
|----------|------|----------|
| **泵故障预测** | 预测泵的剩余使用寿命 | 7-30天 |
| **阀门状态预测** | 预测阀门密封性 | 30-60天 |
| **传感器校准** | 预测传感器漂移 | 30-90天 |
| **清洗效果预测** | 预测下次清洗质量 | 实时 |

### 3.2 泵故障预测 (LSTM)

```python
# predictive_maintenance.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd


class PumpLSTMPredictor(nn.Module):
    """基于LSTM的泵故障预测模型"""

    def __init__(self, input_size=5, hidden_size=64, num_layers=2):
        super().__init__()

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )

        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        lstm_out, _ = self.lstm(x)
        # 取最后一个时间步
        out = self.fc(lstm_out[:, -1, :])
        return self.sigmoid(out)


class PredictiveMaintenance:
    """预测性维护服务"""

    def __init__(self, model_path: str):
        self.model = PumpLSTMPredictor()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

        # 设备健康阈值
        self.health_threshold = 0.7
        self.maintenance_window_days = 7

    def calculate_rul(self, zone_id: int) -> Dict:
        """
        计算设备剩余使用寿命 (Remaining Useful Life)

        Returns:
            {
                'zone_id': int,
                'equipment': str,
                'rul_days': float,  # 剩余天数
                'health_score': float,  # 健康分数 0-1
                'maintenance_recommended': bool,
                'confidence': float
            }
        """

        # 获取设备最近数据
        recent_data = self._get_recent_features(zone_id)

        if len(recent_data) < 100:
            return {
                'zone_id': zone_id,
                'equipment': 'pump',
                'rul_days': None,
                'health_score': None,
                'maintenance_recommended': False,
                'confidence': 0.0,
                'message': '数据不足，无法预测'
            }

        # 转换为tensor
        features = torch.FloatTensor(recent_data).unsqueeze(0)

        # 预测健康分数
        with torch.no_grad():
            health_score = self.model(features).item()

        # 计算剩余使用寿命
        rul_days = self._health_to_rul(health_score)

        # 判断是否需要维护
        maintenance_recommended = (
            health_score < self.health_threshold or
            rul_days < self.maintenance_window_days
        )

        return {
            'zone_id': zone_id,
            'equipment': 'pump',
            'rul_days': round(rul_days, 1),
            'health_score': round(health_score, 3),
            'maintenance_recommended': maintenance_recommended,
            'confidence': 0.85,
            'recommended_date': (
                datetime.now() + timedelta(days=max(0, rul_days - 7))
            ).strftime('%Y-%m-%d')
        }

    def _get_recent_features(self, zone_id: int, days: int = 30) -> np.ndarray:
        """获取最近N天的设备特征"""

        query = """
            SELECT temp_outlet, temp_return, conductivity,
                   pressure, flow
            FROM cip_batch_datapoints
            WHERE zone_id = %s
            AND timestamp > NOW() - INTERVAL '%s days'
            ORDER BY timestamp
        """

        df = pd.read_sql(query, db, params=[zone_id, days])
        return df.values

    def _health_to_rul(self, health_score: float) -> float:
        """将健康分数转换为剩余使用寿命"""

        # 简单线性映射
        # health_score 1.0 -> RUL = 90天
        # health_score 0.0 -> RUL = 0天
        max_rul_days = 90
        return health_score * max_rul_days

    def generate_maintenance_report(self) -> Dict:
        """生成维护报告"""

        report = {
            'generated_at': datetime.now().isoformat(),
            'equipment_status': []
        }

        for zone_id in range(1, 6):
            pump_status = self.calculate_rul(zone_id)
            report['equipment_status'].append(pump_status)

        # 统计需要维护的设备
        needs_maintenance = [
            e for e in report['equipment_status']
            if e.get('maintenance_recommended')
        ]

        report['summary'] = {
            'total_equipment': 5,
            'healthy': 5 - len(needs_maintenance),
            'needs_maintenance': len(needs_maintenance),
            'critical': len([
                e for e in needs_maintenance
                if e.get('rul_days', 999) < 7
            ])
        }

        return report
```

---

## 4. 参数优化

### 4.1 优化目标

| 优化项目 | 目标 | 约束 |
|----------|------|------|
| **清洗时间优化** | 最小化总清洗时间 | 清洗质量不变 |
| **能源消耗优化** | 降低蒸汽/水消耗 | 清洗质量不变 |
| **参数推荐** | 推荐最佳PID参数 | 设备安全 |

### 4.2 Bayesian Optimization

```python
# parameter_optimization.py
from bayes_opt import BayesianOptimization
from sklearn.model_selection import cross_val_score
import numpy as np


class ParameterOptimizer:
    """基于贝叶斯优化的参数优化"""

    def __init__(self):
        self.optimizer = None
        self.best_params = None

    def optimize_pid(
        self,
        zone_id: int,
        historical_data: pd.DataFrame
    ) -> Dict:
        """
        优化PID参数

        Args:
            zone_id: 区域ID
            historical_data: 历史数据包含 Kp, Ki, Kd, 清洗效果

        Returns:
            {
                'zone_id': int,
                'best_kp': float,
                'best_ki': float,
                'best_kd': float,
                'expected_effectiveness': float
            }
        """

        def objective(kp, ki, kd):
            """目标函数: 最大化清洗效果"""

            # 简单模型: 效果与PID参数的关系
            # 实际应用中应使用历史数据训练模型
            temp_score = (kp * 0.4 + ki * 0.3 + kd * 0.3)
            stability_score = 1.0 / (1.0 + abs(kd - 0.5))  # Kd不宜过大

            # 综合分数
            score = temp_score * 0.7 + stability_score * 0.3

            return score

        # 定义参数范围
        pbounds = {
            'kp': (0.5, 5.0),
            'ki': (0.01, 1.0),
            'kd': (0.01, 0.5)
        }

        # 贝叶斯优化
        self.optimizer = BayesianOptimization(
            f=objective,
            pbounds=pbounds,
            random_state=42,
            verbose=2
        )

        self.optimizer.maximize(
            init_points=10,  # 初始探索点
            n_iter=30        # 迭代次数
        )

        best_params = self.optimizer.max['params']

        return {
            'zone_id': zone_id,
            'best_kp': round(best_params['kp'], 2),
            'best_ki': round(best_params['ki'], 3),
            'best_kd': round(best_params['kd'], 3),
            'expected_effectiveness': round(self.optimizer.max['target'], 3)
        }

    def optimize_cleaning_schedule(
        self,
        zone_id: int,
        available_slots: List[Dict]
    ) -> List[Dict]:
        """
        优化清洗排程 (降低能源成本)

        Args:
            zone_id: 区域ID
            available_slots: 可用时间段
                [
                    {'start': '22:00', 'end': '06:00', 'electricity_rate': 0.3},
                    {'start': '06:00', 'end': '22:00', 'electricity_rate': 0.8}
                ]

        Returns:
            优化后的排程建议
        """

        # 优先安排在低电价时段
        optimized = sorted(
            available_slots,
            key=lambda x: x.get('electricity_rate', 1.0)
        )

        return optimized
```

---

## 5. 能源管理

### 5.1 能耗监控

```python
# energy_management.py
class EnergyMonitor:
    """能源消耗监控"""

    def __init__(self):
        self.energy_baseline = {
            'steam_kg_per_batch': 150,  # 每批次蒸汽消耗 (kg)
            'water_l_per_batch': 2000,  # 每批次水消耗 (L)
            'electricity_kwh_per_batch': 15  # 每批次电耗 (kWh)
        }

    def calculate_batch_energy(self, batch_id: str) -> Dict:
        """计算单批次能耗"""

        # 获取批次数据
        batch = db.query(CipBatch).filter(
            CipBatch.batch_id == batch_id
        ).first()

        # 获取步骤数据
        steps = db.query(CipBatchStep).filter(
            CipBatchStep.batch_id == batch_id
        ).all()

        # 计算蒸汽消耗 (基于加热时间和温差)
        total_steam = 0
        total_water = 0
        total_electricity = 15  # 基础电耗

        for step in steps:
            if step.target_temp:
                # 估算蒸汽消耗
                steam_needed = (
                    step.actual_duration * 60 *  # 秒
                    step.target_temp / 100 *     # 温升系数
                    0.5  # 基础系数
                )
                total_steam += steam_needed

            # 水消耗 (冲洗时间 * 流量)
            if '冲洗' in step.media_name:
                total_water += step.actual_duration * 60 * 3.5  # L/min

        return {
            'batch_id': batch_id,
            'zone_id': batch.zone_id,
            'recipe_name': batch.recipe_name,
            'duration': batch.duration,
            'energy': {
                'steam_kg': round(total_steam, 1),
                'water_l': round(total_water, 1),
                'electricity_kwh': round(total_electricity, 1)
            },
            'cost': {
                'steam': round(total_steam * 0.15, 2),   # 蒸汽价格 元/kg
                'water': round(total_water * 0.005, 2),  # 水价格 元/L
                'electricity': round(total_electricity * 0.8, 2),  # 电价 元/kWh
                'total': round(
                    total_steam * 0.15 +
                    total_water * 0.005 +
                    total_electricity * 0.8,
                    2
                )
            },
            'efficiency': self._calculate_efficiency(batch, steps)
        }

    def _calculate_efficiency(self, batch, steps) -> float:
        """计算清洗效率"""

        if not batch.duration:
            return 0.0

        # 目标效率 vs 实际效率
        target_duration = sum(s.target_time for s in steps)
        actual_duration = batch.duration

        efficiency = min(100, target_duration / actual_duration * 100)
        return round(efficiency, 1)

    def get_energy_trend(self, start_date: datetime, end_date: datetime) -> Dict:
        """获取能耗趋势"""

        batches = db.query(CipBatch).filter(
            CipBatch.start_time >= start_date,
            CipBatch.start_time <= end_date
        ).all()

        daily_energy = {}
        for batch in batches:
            date_key = batch.start_time.strftime('%Y-%m-%d')

            energy = self.calculate_batch_energy(batch.batch_id)

            if date_key not in daily_energy:
                daily_energy[date_key] = {
                    'date': date_key,
                    'total_steam_kg': 0,
                    'total_water_l': 0,
                    'total_electricity_kwh': 0,
                    'total_cost': 0,
                    'batch_count': 0
                }

            daily_energy[date_key]['total_steam_kg'] += energy['energy']['steam_kg']
            daily_energy[date_key]['total_water_l'] += energy['energy']['water_l']
            daily_energy[date_key]['total_electricity_kwh'] += energy['energy']['electricity_kwh']
            daily_energy[date_key]['total_cost'] += energy['cost']['total']
            daily_energy[date_key]['batch_count'] += 1

        return list(daily_energy.values())
```

---

## 6. AI API服务

### 6.1 FastAPI路由

```python
# ai_api.py
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class AnomalyDetectionRequest(BaseModel):
    zone_id: int


class AnomalyDetectionResponse(BaseModel):
    zone_id: int
    is_anomaly: bool
    anomaly_score: float
    anomaly_type: Optional[str]
    confidence: float
    recommendation: Optional[str]
    timestamp: str


@router.get("/anomaly/{zone_id}", response_model=AnomalyDetectionResponse)
async def detect_anomaly(zone_id: int):
    """实时异常检测"""

    # 获取最新数据
    data = await redis_client.get(f'cip:zone:{zone_id}:latest')
    if not data:
        raise HTTPException(status_code=404, detail="无最新数据")

    current_data = json.loads(data)

    # 执行检测
    result = anomaly_detector.detect_realtime(zone_id, current_data)

    return result


@router.get("/maintenance/pump/{zone_id}")
async def predict_pump_maintenance(zone_id: int):
    """泵维护预测"""

    result = predictive_maintenance.calculate_rul(zone_id)
    return result


@router.get("/maintenance/report")
async def get_maintenance_report():
    """获取维护报告"""

    report = predictive_maintenance.generate_maintenance_report()
    return report


@router.get("/optimization/pid/{zone_id}")
async def optimize_pid_parameters(zone_id: int):
    """优化PID参数"""

    # 获取历史数据
    historical_data = get_historical_cleaning_data(zone_id)

    result = parameter_optimizer.optimize_pid(zone_id, historical_data)
    return result


@router.get("/energy/batch/{batch_id}")
async def get_batch_energy(batch_id: str):
    """获取单批次能耗"""

    result = energy_monitor.calculate_batch_energy(batch_id)
    return result


@router.get("/energy/trend")
async def get_energy_trend(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """获取能耗趋势"""

    if not start_date:
        start_date = datetime.now() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now()

    result = energy_monitor.get_energy_trend(start_date, end_date)
    return result
```

---

## 7. HMI显示

### 7.1 AI监控面板

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  AI智能监控                                                  [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 设备健康状态                                        最后更新: 14:32    │   │
│  │                                                                         │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                             │   │
│  │  │ 1区 │ │ 2区 │ │ 3区 │ │ 4区 │ │ 5区 │                             │   │
│  │  │ ▓▓▓░│ │ ▓▓▓▓│ │ ▓▓░░│ │ ▓▓▓▓│ │ ▓▓▓░│                             │   │
│  │  │ 78% │ │ 95% │ │ 65% │ │ 92% │ │ 82% │                             │   │
│  │  │ ⚠️  │ │ ✅  │ │ ⚠️  │ │ ✅  │ │ ⚠️  │                             │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘                             │   │
│  │                                                                         │   │
│  │  图例: ▓▓▓▓ 健康(>80%)  ▓▓▓░ 预警(60-80%)  ▓▓░░ 警告(<60%)         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 异常检测                                                              │   │
│  │ ┌───────────────────────────────────────────────────────────────────┐ │   │
│  │ │ 时间        │ 区域  │ 异常类型     │ 分数   │ 建议                 │ │   │
│  │ ├────────────┼───────┼──────────────┼────────┼───────────────────────┤ │   │
│  │ │ 14:25:30  │ 3区   │ 温度偏低     │ -0.72  │ 检查蒸汽供应          │ │   │
│  │ │ 13:15:22  │ 2区   │ 流量偏低     │ -0.65  │ 检查泵状态            │ │   │
│  │ └───────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [查看维护建议]  [查看能耗报告]  [参数优化]                                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 维护预测

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  维护预测                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 设备健康概览                                      生成时间: 2026-05-13    │   │
│  │                                                                         │   │
│  │  设备总数: 5      健康: 2      需维护: 3      紧急: 1                    │   │
│  │                                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐ │   │
│  │  │ 区域  │ 设备    │ 健康分数 │ 剩余寿命 │ 建议维护日期 │ 状态       │ │   │
│  │  ├────────┼─────────┼──────────┼───────────┼──────────────┼─────────┤ │   │
│  │  │ 1区   │ 清洗泵  │ 78%     │ 15天     │ 2026-05-25   │ ⚠️ 预警   │ │   │
│  │  │ 2区   │ 清洗泵  │ 95%     │ 60天     │ 2026-06-30   │ ✅ 健康   │ │   │
│  │  │ 3区   │ 清洗泵  │ 62%     │ 5天      │ 2026-05-18   │ 🔴 紧急   │ │   │
│  │  │ 4区   │ 清洗泵  │ 92%     │ 45天     │ 2026-06-15   │ ✅ 健康   │ │   │
│  │  │ 5区   │ 清洗泵  │ 82%     │ 20天     │ 2026-05-30   │ ⚠️ 预警   │ │   │
│  │  └─────────────────────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 异常检测准确率 | ≥90% |  |
| 预测维护提前时间 | 7-30天 | 故障前预警 |
| 参数优化收敛 | ≤30次迭代 | 贝叶斯优化 |
| 实时检测延迟 | ≤1秒 |  |
| 模型更新周期 | 7天 |  |

---

**文档状态**: ✅ 已完成
**版本**: v1.0
**依赖**: 批次追踪规格 ✅
