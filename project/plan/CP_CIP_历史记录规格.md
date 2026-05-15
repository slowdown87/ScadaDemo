# CIP清洗系统 - 历史记录规格

> 文档版本: v1.1
> 创建日期: 2026-05-13
> 更新日期: 2026-05-13
> 变更记录: v1.1 - 修正批次号格式与HMI设计一致 (CIP-YYYYMMDD-Z-NNN)
> 工段: CP (CIP Cleaning In Place)
> 用途: 清洗历史记录存储、查询、导出

---

## 1. 概述

### 1.1 存储需求

| 项目 | 要求 |
|------|------|
| 存储周期 | **60天** |
| 存储介质 | PostgreSQL数据库 |
| 导出格式 | **CSV** |
| 最大记录数 | 约5000条 (5区×约17次/天×60天) |

### 1.2 记录内容

| 类别 | 内容 |
|------|------|
| 基本信息 | 批次号、区域、配方、开始/结束时间、总时长 |
| 步骤详情 | 每步骤的实际温度、时间、电导率 |
| 判定结果 | 最终电导率、合格/不合格 |
| 操作信息 | 操作员、启动方式、跳步记录 |

---

## 2. 数据库设计

### 2.1 主记录表

```sql
CREATE TABLE cip_cleaning_history (
    -- 主键
    record_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(20) NOT NULL UNIQUE,  -- 批次号 CIP-20260513-1-001

    -- 基本信息
    zone_id INTEGER NOT NULL,              -- 区域ID (1-5)
    zone_name VARCHAR(50),                  -- 区域名称
    recipe_id INTEGER NOT NULL,             -- 配方ID
    recipe_name VARCHAR(50),                -- 配方名称

    -- 时间信息
    start_time TIMESTAMP NOT NULL,          -- 开始时间
    end_time TIMESTAMP,                     -- 结束时间
    duration INTEGER,                        -- 总时长(分钟)

    -- 步骤详情 (JSON格式)
    steps_detail JSONB,                     -- 步骤详细数据

    -- 判定结果
    final_conductivity REAL,               -- 最终电导率 (μS/cm)
    conductivity_threshold REAL,           -- 合格阈值
    pass_fail BOOLEAN,                     -- 合格/不合格
    fail_reason VARCHAR(100),              -- 不合格原因

    -- 操作信息
    operator VARCHAR(50),                   -- 操作员
    start_method VARCHAR(20),              -- 启动方式 (自动/手动)
    skip_count INTEGER DEFAULT 0,          -- 跳步次数

    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 索引
    INDEX idx_zone_id (zone_id),
    INDEX idx_start_time (start_time),
    INDEX idx_batch_id (batch_id)
);
```

### 2.2 步骤详情JSON结构

```json
{
  "step_1": {
    "name": "预冲洗",
    "media": "PURE_WATER",
    "target_temp": 85.0,
    "actual_temp_avg": 84.2,
    "target_time": 15,
    "actual_time": 15,
    "target_conductivity": null,
    "actual_conductivity": null
  },
  "step_2": {
    "name": "碱洗",
    "media": "ALKALI",
    "target_temp": 85.0,
    "actual_temp_avg": 84.8,
    "target_time": 25,
    "actual_time": 26,
    "target_conductivity": null,
    "actual_conductivity": null
  },
  "step_3": {
    "name": "中间冲洗",
    "media": "PURE_WATER",
    "target_temp": 70.0,
    "actual_temp_avg": 69.5,
    "target_time": 10,
    "actual_time": 10,
    "target_conductivity": null,
    "actual_conductivity": null
  },
  "step_4": {
    "name": "酸洗",
    "media": "ACID",
    "target_temp": 60.0,
    "actual_temp_avg": 59.8,
    "target_time": 20,
    "actual_time": 20,
    "target_conductivity": null,
    "actual_conductivity": null
  },
  "step_5": {
    "name": "最终冲洗",
    "media": "PURE_WATER",
    "target_temp": null,
    "actual_temp_avg": 25.0,
    "target_time": 15,
    "actual_time": 18,
    "target_conductivity": 50.0,
    "actual_conductivity": 32.0
  }
}
```

### 2.3 趋势数据表 (可选)

```sql
CREATE TABLE cip_trend_data (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(20) NOT NULL,
    zone_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,

    -- 实时数据
    temperature REAL,                        -- 温度 (℃)
    conductivity REAL,                       -- 电导率 (μS/cm)
    pressure REAL,                          -- 压力 (MPa)
    flow REAL,                              -- 流量 (m³/h)

    -- 索引
    INDEX idx_batch_id (batch_id),
    INDEX idx_timestamp (timestamp)
);
```

---

## 3. 记录时机

### 3.1 记录触发

| 事件 | 触发时机 | 记录内容 |
|------|----------|----------|
| 清洗开始 | 按下启动按钮 | 批次号、区域、配方、开始时间、操作员 |
| 步骤切换 | 当前步骤完成 | 步骤详情(温度曲线摘要) |
| 清洗完成 | 程序结束 | 完整记录、最终判定结果 |
| 清洗取消 | 按下停止按钮 | 部分记录、取消原因 |
| 报警触发 | 报警产生 | 报警信息 |

### 3.2 PLC记录逻辑

```pascal
FUNCTION "FC_LogHistory" : Void
VAR_INPUT
    ZoneID : Int;
    EventType : Int;  // 1=开始, 2=步骤切换, 3=完成, 4=取消
END_VAR
VAR
    BatchID : String[20];
    StepData : "UDT_StepData";
    i : Int;
BEGIN

    CASE EventType OF
        // ====================================================================
        // 清洗开始
        // ====================================================================
        1:  // START
            // 生成批次号
            BatchID := "FC_GenerateBatchID"(ZoneID);
            "DB_Zone"[ZoneID].BatchID := BatchID;

            // 写入开始记录
            "DB_History"[ZoneID].BatchID := BatchID;
            "DB_History"[ZoneID].StartTime := "Global".System.SystemTime;
            "DB_History"[ZoneID].ZoneID := ZoneID;
            "DB_History"[ZoneID].RecipeID := "DB_Zone"[ZoneID].RecipeID;
            "DB_History"[ZoneID].Operator := "Global".CurrentUser;

            // 记录日志
            "FC_WriteLog"('清洗开始', BatchID);

        // ====================================================================
        // 步骤切换
        // ====================================================================
        2:  // STEP_CHANGE
            // 更新步骤详情
            i := "DB_Zone"[ZoneID].CurrentStep;
            "DB_History"[ZoneID].StepsDetail[i].ActualTime :=
                "DB_Zone"[ZoneID].StepTimer;
            "DB_History"[ZoneID].StepsDetail[i].ActualTempAvg :=
                "FC_CalculateAvgTemp"(ZoneID, i);

        // ====================================================================
        // 清洗完成
        // ====================================================================
        3:  // COMPLETE
            // 计算总时长
            "DB_History"[ZoneID].EndTime := "Global".System.SystemTime;
            "DB_History"[ZoneID].Duration :=
                "FC_CalculateDuration"(
                    "DB_History"[ZoneID].StartTime,
                    "DB_History"[ZoneID].EndTime
                );

            // 获取最终电导率
            "DB_History"[ZoneID].FinalConductivity := "DB_Zone"[ZoneID].CD;
            "DB_History"[ZoneID].ConductivityThreshold := 50.0;  // 默认阈值

            // 判定结果
            IF "DB_Zone"[ZoneID].Result THEN
                "DB_History"[ZoneID].PassFail := TRUE;
            ELSE
                "DB_History"[ZoneID].PassFail := FALSE;
                "DB_History"[ZoneID].FailReason := "DB_Zone"[ZoneID].ResultMsg;
            END_IF;

            // 写入数据库
            "FC_WriteToDatabase"(ZoneID);

        // ====================================================================
        // 清洗取消
        // ====================================================================
        4:  // CANCEL
            "DB_History"[ZoneID].EndTime := "Global".System.SystemTime;
            "DB_History"[ZoneID].PassFail := FALSE;
            "DB_History"[ZoneID].FailReason := '用户取消';
            "FC_WriteToDatabase"(ZoneID);

    END_CASE;

END_FUNCTION
```

---

## 4. 批次号生成规则

### 4.1 格式定义

```
批次号格式: CIP-YYYYMMDD-Z-NNN

示例: CIP-20260513-1-001
      │    │    │ │   │
      │    │    │ │   └── 当日该区域序号 (001-999)
      │    │    │ └────── 区域ID (1-5)
      │    │    └──────── 日期 (2026-05-13)
      │    └───────────── 年份 (2026)
      └────────────────── CIP系统标识
```

### 4.2 生成函数

```pascal
FUNCTION "FC_GenerateBatchID" : String[20]
VAR_INPUT
    ZoneID : Int;
END_VAR
VAR
    DateStr : String[12];
    ZoneStr : String[1];
    SeqStr : String[3];
    SeqNo : Int;
BEGIN
    // 获取完整日期字符串 YYYYMMDD
    DateStr := MID(DT_TO_STRING("Global".System.SystemTime), 1, 4);  // 年
    DateStr := CONCAT(DateStr, MID(DT_TO_STRING("Global".System.SystemTime), 6, 2));  // 月
    DateStr := CONCAT(DateStr, MID(DT_TO_STRING("Global".System.SystemTime), 9, 2));  // 日

    // 转换区域ID为字符串
    ZoneStr := INT_TO_STRING(ZoneID);

    // 获取当日该区域序号
    SeqNo := "Global".DailySeq[ZoneID];
    SeqNo := SeqNo + 1;
    "Global".DailySeq[ZoneID] := SeqNo;

    // 格式化序号 (3位)
    CASE SeqNo OF
        1..9:   SeqStr := CONCAT('00', INT_TO_STRING(SeqNo));
        10..99: SeqStr := CONCAT('0', INT_TO_STRING(SeqNo));
        ELSE:   SeqStr := INT_TO_STRING(SeqNo);
    END_CASE;

    // 组合批次号: CIP-YYYYMMDD-Z-NNN
    "FC_GenerateBatchID" := CONCAT('CIP-', DateStr);
    "FC_GenerateBatchID" := CONCAT("FC_GenerateBatchID", '-');
    "FC_GenerateBatchID" := CONCAT("FC_GenerateBatchID", ZoneStr);
    "FC_GenerateBatchID" := CONCAT("FC_GenerateBatchID", '-');
    "FC_GenerateBatchID" := CONCAT("FC_GenerateBatchID", SeqStr);

END_FUNCTION
```

---

## 5. 数据查询

### 5.1 查询接口 (Python/FastAPI)

```python
# history_api.py
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import csv
import io

router = APIRouter(prefix="/api/v1/history", tags=["history"])


class CleaningRecord(BaseModel):
    record_id: int
    batch_id: str
    zone_id: int
    zone_name: str
    recipe_id: int
    recipe_name: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[int]
    steps_detail: dict
    final_conductivity: Optional[float]
    conductivity_threshold: Optional[float]
    pass_fail: Optional[bool]
    fail_reason: Optional[str]
    operator: Optional[str]
    start_method: Optional[str]
    skip_count: int


@router.get("/records", response_model=List[CleaningRecord])
async def get_records(
    zone_id: Optional[int] = None,
    recipe_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    pass_fail: Optional[bool] = None,
    limit: int = Query(default=100, le=1000),
    offset: int = 0
):
    """查询清洗历史记录"""

    query = db.query(CleaningHistory)

    if zone_id:
        query = query.filter(CleaningHistory.zone_id == zone_id)
    if recipe_id:
        query = query.filter(CleaningHistory.recipe_id == recipe_id)
    if start_date:
        query = query.filter(CleaningHistory.start_time >= start_date)
    if end_date:
        query = query.filter(CleaningHistory.start_time <= end_date)
    if pass_fail is not None:
        query = query.filter(CleaningHistory.pass_fail == pass_fail)

    records = query.order_by(
        CleaningHistory.start_time.desc()
    ).offset(offset).limit(limit).all()

    return records


@router.get("/records/{batch_id}", response_model=CleaningRecord)
async def get_record(batch_id: str):
    """根据批次号查询单条记录"""
    record = db.query(CleaningHistory).filter(
        CleaningHistory.batch_id == batch_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")

    return record


@router.get("/export/csv")
async def export_csv(
    start_date: datetime = Query(default_factory=lambda: datetime.now() - timedelta(days=7)),
    end_date: datetime = Query(default_factory=lambda: datetime.now()),
    zone_id: Optional[int] = None
):
    """导出CSV格式的历史记录"""

    query = db.query(CleaningHistory).filter(
        CleaningHistory.start_time >= start_date,
        CleaningHistory.start_time <= end_date
    )

    if zone_id:
        query = query.filter(CleaningHistory.zone_id == zone_id)

    records = query.order_by(CleaningHistory.start_time.desc()).all()

    # 生成CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # 写入表头
    writer.writerow([
        '批次号', '区域', '配方', '开始时间', '结束时间', '总时长(分钟)',
        '最终电导率(μS/cm)', '合格阈值', '结果', '不合格原因',
        '操作员', '启动方式', '跳步次数'
    ])

    # 写入数据
    for r in records:
        writer.writerow([
            r.batch_id,
            r.zone_name,
            r.recipe_name,
            r.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            r.end_time.strftime('%Y-%m-%d %H:%M:%S') if r.end_time else '',
            r.duration or '',
            r.final_conductivity or '',
            r.conductivity_threshold or '',
            '合格' if r.pass_fail else '不合格',
            r.fail_reason or '',
            r.operator or '',
            r.start_method or '',
            r.skip_count
        ])

    # 返回CSV文件
    output.seek(0)
    filename = f"cip_history_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/statistics/daily")
async def get_daily_statistics(
    days: int = Query(default=7, le=90)
):
    """获取每日清洗统计"""

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    records = db.query(CleaningHistory).filter(
        CleaningHistory.start_time >= start_date,
        CleaningHistory.start_time <= end_date
    ).all()

    # 按日期分组统计
    stats = {}
    for r in records:
        date_key = r.start_time.strftime('%Y-%m-%d')
        if date_key not in stats:
            stats[date_key] = {
                'date': date_key,
                'total_count': 0,
                'pass_count': 0,
                'fail_count': 0,
                'total_duration': 0,
                'by_zone': {}
            }

        stats[date_key]['total_count'] += 1
        stats[date_key]['total_duration'] += r.duration or 0

        if r.pass_fail:
            stats[date_key]['pass_count'] += 1
        else:
            stats[date_key]['fail_count'] += 1

        # 按区域统计
        zone_name = r.zone_name
        if zone_name not in stats[date_key]['by_zone']:
            stats[date_key]['by_zone'][zone_name] = 0
        stats[date_key]['by_zone'][zone_name] += 1

    return list(stats.values())
```

---

## 6. HMI显示

### 6.1 历史记录列表

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  历史记录                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  筛选条件:                                                                    │
│  区域: [全部▼]  配方: [全部▼]  结果: [全部▼]  日期: [2026-05-06▼]~[今天▼]  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 批次号             │ 日期/时间      │ 区域  │ 配方     │ 电导率 │ 结果 │ 操作 │   │
│  ├───────────────────┼───────────────┼───────┼──────────┼────────┼──────┼─────┤   │
│  │ CIP-20260513-5-001│ 05-13 17:10   │ 5区-灌装│ PFCIP-01│ 32μS  │ 合格 │[查看]│   │
│  │ CIP-20260513-3-001│ 05-13 15:35   │ 3区-调配│ BLCIP-01│ 45μS  │ 合格 │[查看]│   │
│  │ CIP-20260513-2-001│ 05-13 14:00   │ 2区-茶叶│ EXCIP-01│ 28μS  │ 合格 │[查看]│   │
│  │ CIP-20260512-1-005│ 05-12 20:30   │ 1区-水处理│WTCIP-01│ 48μS  │ 合格 │[查看]│   │
│  │ CIP-20260512-4-001│ 05-12 18:45   │ 4区-UHT│ UHCIP-01│ --     │ 取消 │[查看]│   │
│  │ CIP-20260512-5-003│ 05-12 16:20   │ 5区-灌装│ PFCIP-01│ 55μS ✗│ 不合格│[查看]│   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  显示 1-6/156 条  [上一页] [下一页]  [导出CSV] [导出Excel]                    │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 记录详情

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  批次详情 - CIP-20260513-2-001                                          [子画面] │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 批次信息                              操作信息                           │   │
│  │ ─────────────────────                 ─────────────────────           │   │
│  │ 批次号: CIP-20260513-2-001           操作员: 张三                        │   │
│  │ 区域: 2区-茶叶萃取                    启动方式: 自动                      │   │
│  │ 配方: EXCIP-01                       开始时间: 2026-05-13 14:00        │   │
│  │ 结果: ✅ 合格                         结束时间: 2026-05-13 15:35        │   │
│  │                                     总时长: 95分钟                      │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 步骤详情                                                              │   │
│  │ ┌─────┬────────┬────────┬───────┬───────┬────────┐                     │   │
│  │ │步骤 │ 介质   │ 目标温度│ 实际均温│ 目标时间│ 实际时间│ 备注         │   │
│  │ ├─────┼────────┼────────┼───────┼───────┼────────┤                     │   │
│  │ │  1  │ 纯水冲洗│  85℃  │  84.2℃│ 15min │ 15min │              │   │
│  │ │  2  │ 碱洗    │  85℃  │  84.8℃│ 25min │ 26min │              │   │
│  │ │  3  │ 中间冲洗│  70℃  │  69.5℃│ 10min │ 10min │              │   │
│  │ │  4  │ 酸洗    │  60℃  │  59.8℃│ 20min │ 20min │              │   │
│  │ │  5  │ 最终冲洗│  --    │  25.0℃│ 15min │ 18min │ 跳步1次      │   │
│  │ └─────┴────────┴────────┴───────┴───────┴────────┘                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 温度趋势                                                              │   │
│  │ 90 ┤                                                                │   │
│  │    │                         ╭──                                        │   │
│  │ 85 ┤─────────────────────╯  (目标温度线)                               │   │
│  │    │                   ╭──                                              │   │
│  │    │               ╭──                                                  │   │
│  │ 60 ┤────────────╯                                                       │   │
│  │    └───────────────────────────────────────────────────────             │   │
│  │       14:00  14:15  14:30  14:45  15:00  15:15  15:30  15:35        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 电导率趋势                                                            │   │
│  │ 400 ┤                                                                │   │
│  │     │     ╭──                                                         │   │
│  │ 320 ┤────╯  (碱洗阶段)                                                │   │
│  │     │                                                                │   │
│  │  50 ┼──┬──┬──┬──┬──┬── (合格阈值)                                    │   │
│  │     │                          ╭──                                     │   │
│  │  28 ┤────────────────────────╯  (最终: 28μS ✓)                       │   │
│  │     └───────────────────────────────────────────────────────           │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [返回列表]                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. 数据管理

### 7.1 自动清理

```python
# 定期清理超过60天的记录
@router.on_event("startup")
async def setup_cleanup_task():
    # 每天凌晨2点执行清理
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_old_records, 'cron', hour=2, minute=0)
    scheduler.start()


def cleanup_old_records():
    """清理60天前的记录"""
    cutoff_date = datetime.now() - timedelta(days=60)

    # 删除历史记录
    db.query(CleaningHistory).filter(
        CleaningHistory.start_time < cutoff_date
    ).delete()

    # 删除趋势数据
    db.query(CipTrendData).filter(
        CipTrendData.timestamp < cutoff_date
    ).delete()

    db.commit()
    logger.info(f"已清理 {cutoff_date} 之前的记录")
```

### 7.2 存储估算

| 项目 | 单条大小 | 60天预估 | 说明 |
|------|----------|----------|------|
| 主记录 | ~2KB | ~10MB | 5000条 |
| 步骤详情 | ~1KB/条 | ~5MB | 每条5步骤 |
| 趋势数据 | ~100字节 | ~500MB | 每分钟1条 |
| **总计** | - | **~515MB** | 含索引 |

---

## 8. 权限管理

| 操作 | 操作员 | 技术员 | 工程师 | 管理员 |
|------|--------|--------|--------|--------|
| 查看历史记录 | ✅ | ✅ | ✅ | ✅ |
| 查看详情 | ✅ | ✅ | ✅ | ✅ |
| 导出CSV | ❌ | ✅ | ✅ | ✅ |
| 删除记录 | ❌ | ❌ | ❌ | ✅ |

---

**文档状态**: ✅ 已完成
**版本**: v1.0
**依赖**: 子任务10 (Profinet通讯) ✅
