# CIP清洗系统 - 批次追踪规格

> 文档版本: v1.0
> 创建日期: 2026-05-13
> 工段: CP (CIP Cleaning In Place)
> 用途: 批次清洗全过程追溯、数据采集、与MES系统对接

---

## 1. 概述

### 1.1 批次追踪架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           批次追踪系统架构                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          批次数据采集层                                   │   │
│  │                                                                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │   │
│  │  │ 温度采集 │  │ 电导率   │  │ 流量采集 │  │ 阀门状态 │              │   │
│  │  │ (TT)    │  │ (CD)     │  │ (FT)    │  │ (V)     │              │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │   │
│  └────────┼────────────┴────────────┴─────────────┴─────────────────────────┘   │
│           │                                                                  │
│           ▼                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          批次数据处理层                                  │   │
│  │                                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐   │   │
│  │  │                    FC_LogHistory / FC_LogBatchData                  │   │   │
│  │  │  • 实时数据采样                                                    │   │   │
│  │  │  • 批次号生成                                                      │   │   │
│  │  │  • 步骤切换记录                                                    │   │   │
│  │  └─────────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          数据存储层                                     │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │   │
│  │  │ Redis缓存    │  │ PostgreSQL  │  │ 文件存储     │                  │   │
│  │  │ (实时数据)   │  │ (历史数据)  │  │ (趋势数据)   │                  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          数据展示层                                     │   │
│  │                                                                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │   │
│  │  │ HMI批次追踪  │  │ Web批次追踪  │  │ 报表系统    │                  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 批次追踪数据流

```
清洗开始 ──► 生成批次号 ──► 采集实时数据 ──► 存储 ──► 清洗完成
    │            │              │              │            │
    │            ▼              ▼              ▼            ▼
    │       CIP-YYYYMMDD-Z-NNN  温度/电导率/流量   Redis缓存   批次报告
    │                              │
    │                              ▼
    │                       趋势数据文件
```

---

## 2. 批次数据模型

### 2.1 批次主数据

```sql
CREATE TABLE cip_batch (
    -- 主键
    batch_id VARCHAR(20) PRIMARY KEY,  -- CIP-20260513-1-001

    -- 基本信息
    zone_id INTEGER NOT NULL,           -- 区域ID
    zone_name VARCHAR(50),              -- 区域名称
    recipe_id INTEGER NOT NULL,         -- 配方ID
    recipe_name VARCHAR(50),            -- 配方名称

    -- 时间信息
    start_time TIMESTAMP NOT NULL,      -- 开始时间
    end_time TIMESTAMP,                 -- 结束时间
    duration INTEGER,                   -- 总时长(分钟)

    -- 判定结果
    final_result BOOLEAN,               -- 最终结果 TRUE=合格
    final_conductivity REAL,            -- 最终电导率

    -- 操作信息
    operator VARCHAR(50),               -- 操作员
    start_method VARCHAR(20),          -- 启动方式
    skip_step_count INTEGER DEFAULT 0, -- 跳步次数

    -- MES集成
    mes_work_order VARCHAR(50),         -- MES工单号
    mes_product_id VARCHAR(50),         -- MES产品ID

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_zone_time (zone_id, start_time),
    INDEX idx_mes_order (mes_work_order)
);
```

### 2.2 批次步骤数据

```sql
CREATE TABLE cip_batch_steps (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(20) REFERENCES cip_batch(batch_id),

    step_index INTEGER NOT NULL,        -- 步骤索引
    media_id INTEGER,                  -- 介质ID
    media_name VARCHAR(30),            -- 介质名称

    -- 目标值
    target_temp REAL,                  -- 目标温度
    target_time INTEGER,               -- 目标时间
    target_flow REAL,                  -- 目标流量
    pass_conductivity REAL,            -- 合格电导率

    -- 实际值
    actual_start_time TIMESTAMP,        -- 实际开始时间
    actual_end_time TIMESTAMP,          -- 实际结束时间
    actual_duration INTEGER,            -- 实际时长
    actual_temp_avg REAL,               -- 平均温度
    actual_temp_min REAL,               -- 最低温度
    actual_temp_max REAL,               -- 最高温度
    final_conductivity REAL,            -- 最终电导率

    -- 判定
    temp_ok BOOLEAN,                   -- 温度达标
    time_ok BOOLEAN,                   -- 时间达标
    conductivity_ok BOOLEAN,           -- 电导率达标

    -- 索引
    INDEX idx_batch_step (batch_id, step_index)
);
```

### 2.3 批次实时数据点

```sql
CREATE TABLE cip_batch_datapoints (
    id BIGSERIAL PRIMARY KEY,
    batch_id VARCHAR(20) NOT NULL,
    zone_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- 传感器数据
    temp_outlet REAL,                   -- 出口温度
    temp_return REAL,                   -- 回流温度
    conductivity REAL,                  -- 电导率
    pressure REAL,                      -- 管路压力
    flow REAL,                          -- 清洗流量

    -- 设备状态
    pump_speed REAL,                   -- 泵速
    steam_valve REAL,                  -- 蒸汽阀开度

    -- 索引
    INDEX idx_batch_time (batch_id, timestamp)
);
```

---

## 3. 数据采集规格

### 3.1 采样周期

| 数据类型 | 采样周期 | 存储方式 | 保留时间 |
|----------|----------|----------|----------|
| 实时数据点 | **10秒** | PostgreSQL | **60天** |
| 报警事件 | 事件触发 | PostgreSQL | 60天 |
| 操作日志 | 事件触发 | PostgreSQL | **180天** |
| 趋势数据 | 1秒 | Redis | 1小时 |

### 3.2 PLC数据采集

```pascal
FUNCTION "FC_CollectBatchData" : Void
VAR_INPUT
    ZoneID : Int;
END_VAR
VAR
    CurrentStep : Int;
    StepData : "UDT_StepData";
    SampleTimer : Int;
BEGIN

    // 获取当前批次号
    IF "DB_Zone"[ZoneID].BatchID = '' THEN
        RETURN;  // 无批次号，不采集
    END_IF;

    // 获取当前步骤
    CurrentStep := "DB_Zone"[ZoneID].CurrentStep;
    StepData := "DB_Zone"[ZoneID].Recipe.Steps[CurrentStep];

    // 采样计时器 (每10秒采集一次)
    "DB_Zone"[ZoneID].SampleTimer := "DB_Zone"[ZoneID].SampleTimer + 1;

    IF "DB_Zone"[ZoneID].SampleTimer >= 100 THEN  // OB35=100ms, 100次=10秒
        "DB_Zone"[ZoneID].SampleTimer := 0;

        // 写入实时数据点
        "FC_WriteDatapoint"(
            ZoneID,
            "DB_Zone"[ZoneID].BatchID,
            "DB_Zone"[ZoneID].TT_Outlet,
            "DB_Zone"[ZoneID].TT_Return,
            "DB_Zone"[ZoneID].CD,
            "DB_Zone"[ZoneID].PT,
            "DB_Zone"[ZoneID].FT,
            "DB_Zone"[ZoneID].PumpSpeed,
            "Global".Output.SteamValve
        );

        // 更新步骤统计
        "FC_UpdateStepStats"(ZoneID, CurrentStep);
    END_IF;

END_FUNCTION
```

### 3.3 数据点写入

```python
# batch_data.py
from datetime import datetime
from typing import List

class BatchDataCollector:
    """批次数据采集器"""

    def __init__(self, db_pool):
        self.db_pool = db_pool

    async def write_datapoint(self, batch_id: str, zone_id: int, data: dict):
        """写入单个数据点"""

        query = """
            INSERT INTO cip_batch_datapoints
            (batch_id, zone_id, timestamp, temp_outlet, temp_return,
             conductivity, pressure, flow, pump_speed, steam_valve)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        async with self.db_pool.acquire() as conn:
            await conn.execute(query,
                batch_id,
                zone_id,
                datetime.now(),
                data.get('temp_outlet'),
                data.get('temp_return'),
                data.get('conductivity'),
                data.get('pressure'),
                data.get('flow'),
                data.get('pump_speed'),
                data.get('steam_valve')
            )

    async def write_batch_step(self, batch_id: str, step_data: dict):
        """写入步骤数据"""

        query = """
            INSERT INTO cip_batch_steps
            (batch_id, step_index, media_id, media_name,
             target_temp, target_time, target_flow, pass_conductivity,
             actual_start_time, actual_duration, actual_temp_avg,
             temp_ok, time_ok, conductivity_ok)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        async with self.db_pool.acquire() as conn:
            await conn.execute(query,
                batch_id,
                step_data.get('step_index'),
                step_data.get('media_id'),
                step_data.get('media_name'),
                step_data.get('target_temp'),
                step_data.get('target_time'),
                step_data.get('target_flow'),
                step_data.get('pass_conductivity'),
                step_data.get('actual_start_time'),
                step_data.get('actual_duration'),
                step_data.get('actual_temp_avg'),
                step_data.get('temp_ok'),
                step_data.get('time_ok'),
                step_data.get('conductivity_ok')
            )
```

---

## 4. 追溯查询

### 4.1 批次详情查询

```python
@router.get("/batch/{batch_id}")
async def get_batch_detail(batch_id: str):
    """获取批次详细信息"""

    # 查询批次主数据
    batch = await db.query(CipBatch).filter(
        CipBatch.batch_id == batch_id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    # 查询步骤数据
    steps = await db.query(CipBatchStep).filter(
        CipBatchStep.batch_id == batch_id
    ).order_by(CipBatchStep.step_index).all()

    # 查询趋势数据 (最近1000点)
    datapoints = await db.query(CipBatchDatapoint).filter(
        CipBatchDatapoint.batch_id == batch_id
    ).order_by(
        CipBatchDatapoint.timestamp
    ).limit(1000).all()

    return {
        "batch": batch,
        "steps": steps,
        "datapoints": [
            {
                "timestamp": d.timestamp.isoformat(),
                "temp_outlet": d.temp_outlet,
                "temp_return": d.temp_return,
                "conductivity": d.conductivity,
                "flow": d.flow
            }
            for d in datapoints
        ]
    }
```

### 4.2 时间范围追溯

```python
@router.get("/trace/by-time-range")
async def trace_by_time_range(
    start_time: datetime,
    end_time: datetime,
    zone_id: Optional[int] = None
):
    """按时间范围追溯"""

    query = db.query(CipBatch).filter(
        CipBatch.start_time >= start_time,
        CipBatch.start_time <= end_time
    )

    if zone_id:
        query = query.filter(CipBatch.zone_id == zone_id)

    batches = query.order_by(CipBatch.start_time.desc()).all()

    return [
        {
            "batch_id": b.batch_id,
            "zone_name": b.zone_name,
            "recipe_name": b.recipe_name,
            "start_time": b.start_time.isoformat(),
            "duration": b.duration,
            "result": b.final_result
        }
        for b in batches
    ]
```

### 4.3 物料追溯

```python
@router.get("/trace/by-product/{product_id}")
async def trace_by_product(product_id: str):
    """按产品追溯使用的清洗批次"""

    batches = await db.query(CipBatch).filter(
        CipBatch.mes_product_id == product_id
    ).order_by(CipBatch.start_time.desc()).all()

    return [
        {
            "batch_id": b.batch_id,
            "zone_name": b.zone_name,
            "recipe_name": b.recipe_name,
            "start_time": b.start_time.isoformat(),
            "end_time": b.end_time.isoformat() if b.end_time else None,
            "result": b.final_result
        }
        for b in batches
    ]
```

---

## 5. 报表生成

### 5.1 批次报告

```python
@router.get("/report/batch/{batch_id}")
async def generate_batch_report(batch_id: str):
    """生成批次报告 PDF/HTML"""

    batch = await get_batch_detail(batch_id)

    report = {
        "title": "CIP清洗批次报告",
        "batch_id": batch_id,
        "basic_info": {
            "批次号": batch['batch'].batch_id,
            "区域": batch['batch'].zone_name,
            "配方": batch['batch'].recipe_name,
            "开始时间": batch['batch'].start_time,
            "结束时间": batch['batch'].end_time,
            "总时长": f"{batch['batch'].duration}分钟",
            "结果": "合格" if batch['batch'].final_result else "不合格",
            "操作员": batch['batch'].operator
        },
        "steps": [
            {
                "步骤": f"步骤{s.step_index}",
                "介质": s.media_name,
                "目标温度": f"{s.target_temp}℃" if s.target_temp else "-",
                "实际平均温度": f"{s.actual_temp_avg}℃" if s.actual_temp_avg else "-",
                "目标时间": f"{s.target_time}分钟",
                "实际时间": f"{s.actual_duration}分钟" if s.actual_duration else "-",
                "温度达标": "✓" if s.temp_ok else "✗",
                "时间达标": "✓" if s.time_ok else "✗",
                "电导率达标": "✓" if s.conductivity_ok else "✗"
            }
            for s in batch['steps']
        ],
        "trend_data": batch['datapoints']
    }

    return report
```

### 5.2 统计报表

```python
@router.get("/report/statistics")
async def get_statistics(
    start_date: datetime,
    end_date: datetime,
    group_by: str = "day"  # day, week, month, zone
):
    """获取统计报表"""

    records = await db.query(CipBatch).filter(
        CipBatch.start_time >= start_date,
        CipBatch.start_time <= end_date
    ).all()

    # 按日期分组统计
    stats = {}
    for r in records:
        if group_by == "day":
            key = r.start_time.strftime('%Y-%m-%d')
        elif group_by == "zone":
            key = r.zone_name
        else:
            key = r.start_time.strftime('%Y-%m')

        if key not in stats:
            stats[key] = {
                "group": key,
                "total": 0,
                "pass": 0,
                "fail": 0,
                "pass_rate": 0.0,
                "total_duration": 0,
                "avg_duration": 0
            }

        stats[key]["total"] += 1
        stats[key]["total_duration"] += r.duration or 0
        if r.final_result:
            stats[key]["pass"] += 1
        else:
            stats[key]["fail"] += 1

    # 计算合格率
    for s in stats.values():
        if s["total"] > 0:
            s["pass_rate"] = round(s["pass"] / s["total"] * 100, 2)
            s["avg_duration"] = round(s["total_duration"] / s["total"], 1)

    return list(stats.values())
```

---

## 6. MES集成

### 6.1 MES接口

```python
@router.post("/mes/sync")
async def sync_with_mes(batch_id: str):
    """同步批次数据到MES"""

    batch = await db.query(CipBatch).filter(
        CipBatch.batch_id == batch_id
    ).first()

    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")

    # 构建MES消息
    mes_message = {
        "work_order": batch.mes_work_order,
        "product_id": batch.mes_product_id,
        "equipment_id": f"CIP-Z{batch.zone_id}",
        "batch_id": batch.batch_id,
        "start_time": batch.start_time.isoformat(),
        "end_time": batch.end_time.isoformat() if batch.end_time else None,
        "result": "PASS" if batch.final_result else "FAIL",
        "cleaning_parameters": {
            "recipe": batch.recipe_name,
            "duration": batch.duration,
            "final_conductivity": batch.final_conductivity
        }
    }

    # 发送到MES (示例: RabbitMQ)
    await mes_publisher.publish('cip.batch.completed', mes_message)

    return {"status": "synced", "message": "MES同步成功"}


@router.get("/mes/work-order/{work_order}")
async def get_batches_by_work_order(work_order: str):
    """根据MES工单查询清洗批次"""

    batches = await db.query(CipBatch).filter(
        CipBatch.mes_work_order == work_order
    ).all()

    return batches
```

---

## 7. HMI显示

### 7.1 批次追踪画面

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  批次追踪                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  批次号: [CIP-20260513-2-001_______________]  [查询]                         │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 批次信息                                                              │   │
│  │ ──────────────────────────────────────────────────────────────────── │   │
│  │ 批次号: CIP-20260513-2-001        状态: ✅ 已完成                     │   │
│  │ 区域: 2区-茶叶萃取                 配方: EXCIP-01                      │   │
│  │ 开始: 2026-05-13 14:00            结束: 2026-05-13 15:35             │   │
│  │ 操作员: 张三                        结果: 合格                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 步骤详情                                                              │   │
│  │ ┌─────┬────────┬────────┬───────┬───────┬───────┐                     │   │
│  │ │步骤 │ 介质   │ 目标温度│实际均温│ 目标时间│ 实际时间│ 状态         │   │
│  │ ├─────┼────────┼────────┼───────┼───────┼───────┤                     │   │
│  │ │  1  │ 纯水冲洗│  85℃  │ 84.2℃│ 15min │ 15min │ ✅ 合格        │   │
│  │ │  2  │ 碱洗    │  85℃  │ 84.8℃│ 25min │ 26min │ ✅ 合格        │   │
│  │ │  3  │ 中间冲洗│  70℃  │ 69.5℃│ 10min │ 10min │ ✅ 合格        │   │
│  │ │  4  │ 酸洗    │  60℃  │ 59.8℃│ 20min │ 20min │ ✅ 合格        │   │
│  │ │  5  │ 最终冲洗│  --    │ 25.0℃│ 15min │ 18min │ ✅ 合格(28μS) │   │
│  │ └─────┴────────┴────────┴───────┴───────┴───────┘                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [查看趋势图] [导出报告] [打印]                                                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 实时趋势图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  实时趋势 - CIP-20260513-2-001                               [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  曲线选择:  ☑温度  ☑电导率  ☑流量  时间范围: [全程▼]                        │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 温度(℃)                                                          90 ┤   │
│  │                                                                    85 ┤ ══╗│
│  │                                                               84.2℃ ──┼─╝  │   │
│  │                                                                    70 ┤ ────│
│  │                                                                    60 ┤     │   │
│  │                                                                     0 ┼─────┼───
│  │       14:00  14:15  14:30  14:45  15:00  15:15  15:35         │   │
│  │       ├────────┴────────┴────────┴────────┴────────┴────────┤     │   │
│  │              步骤1     步骤2      步骤3     步骤4      步骤5       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 电导率(μS/cm)                                                    400 ┤   │
│  │                                                                    50 ┼──┬──│
│  │                                                               28μS ──┼──┘  │   │
│  │                                                                     0 ┼─────┼───
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  统计: 最大温度=85.2℃  最小温度=25.0℃  平均=68.3℃                        │
│       最大电导=320μS  最小电导=28μS   最终=28μS ✓                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. 数据保留策略

| 数据类型 | 保留时间 | 存储位置 | 备注 |
|----------|----------|----------|------|
| 批次主数据 | **永久** | PostgreSQL | 重要追溯依据 |
| 批次步骤数据 | **永久** | PostgreSQL | 重要追溯依据 |
| 实时数据点 | **60天** | PostgreSQL | 趋势数据 |
| 操作日志 | **180天** | PostgreSQL | 审计需要 |
| 报警记录 | **180天** | PostgreSQL | 审计需要 |

---

**文档状态**: ✅ 已完成
**版本**: v1.0
**依赖**: 子任务11 (历史记录) ✅
