# CIP清洗系统 - PLC程序文件索引

## 文件组织结构

```
project/plc/
├── types/                    # 数据类型
│   ├── CIP_EnumTypes.scl   # 枚举类型 (7个)
│   ├── CIP_StructTypes.scl  # 结构体类型 (9个)
│   └── CIP_DataBlockDefs.scl # DB块模板
│
├── ob/                      # 组织块
│   └── CIP_OB.scl          # OB1/OB100/OB35
│
├── control/                 # 控制逻辑
│   ├── CIP_Main.scl        # 主调度 (FC100-105)
│   ├── CIP_ZoneControl.scl # 区域清洗控制
│   ├── CIP_MediaControl.scl # 介质选择控制
│   └── CIP_PIDControl.scl  # PID控制
│
├── utility/                 # 工具函数
│   ├── CIP_Alarm.scl       # 报警处理
│   ├── CIP_History.scl      # 历史记录
│   ├── CIP_Sensor.scl       # 传感器
│   ├── CIP_Queue.scl        # 队列管理
│   └── CIP_System.scl       # 系统功能
│
└── docs/                   # 文档
    └── README.md           # 本索引文件
```

## 分类说明

| 目录 | 内容 | 说明 |
|------|------|------|
| `types/` | 数据类型 | 枚举、结构体、DB块模板 |
| `ob/` | 组织块 | OB1(循环)、OB100(启动)、OB35(中断) |
| `control/` | 控制逻辑 | 主调度、区域控制、介质控制、PID |
| `utility/` | 工具函数 | 报警、历史、传感器、队列、系统 |
| `docs/` | 文档 | 索引说明 |

## 文件依赖关系

```
types/     (基础层 - 无依赖)
    ↓
ob/       (组织块层 - 依赖types)
    ↓
control/  (控制层 - 依赖types/ob)
    ↓
utility/  (工具层 - 依赖types/ob/control)
```

## TIA Portal 导入顺序

### 1. 数据类型 (types/)
```
导入顺序: 1
- CIP_EnumTypes.scl      ← 先导入枚举
- CIP_StructTypes.scl     ← 再导入结构体
- CIP_DataBlockDefs.scl  ← DB块模板(参考创建)
```

### 2. 组织块 (ob/)
```
导入顺序: 2
- CIP_OB.scl
```

### 3. 控制逻辑 (control/)
```
导入顺序: 3
- CIP_Main.scl           ← 主调度
- CIP_ZoneControl.scl    ← 区域控制
- CIP_MediaControl.scl   ← 介质控制
- CIP_PIDControl.scl     ← PID控制
```

### 4. 工具函数 (utility/)
```
导入顺序: 4
- CIP_System.scl         ← 系统功能(初始化等)
- CIP_Queue.scl          ← 队列管理
- CIP_Alarm.scl          ← 报警处理
- CIP_History.scl        ← 历史记录
- CIP_Sensor.scl          ← 传感器
```

## 模块详情

### types/ - 数据类型

| 文件 | 内容 | 行数 |
|------|------|------|
| `CIP_EnumTypes.scl` | 7个枚举: MediaType, CleanState, AlarmLevel, HandsMode, ValveState, PumpState, ControlCmd | 73 |
| `CIP_StructTypes.scl` | 9个结构体: StepData, RecipeData, ZoneData, MediaStatus, TankStatus, AlarmInfo, HistoryRecord, PIDParams, SystemStatus | 266 |
| `CIP_DataBlockDefs.scl` | 全局DB块模板(注释) | 132 |

### ob/ - 组织块

| 文件 | 内容 | 行数 |
|------|------|------|
| `CIP_OB.scl` | OB1(主循环), OB100(启动初始化), OB35(100ms中断) | 112 |

### control/ - 控制逻辑

| 文件 | 函数 | 功能 | 行数 |
|------|------|------|------|
| `CIP_Main.scl` | FC100, FC101-105 | 主调度、各区封装 | 96 |
| `CIP_ZoneControl.scl` | FC_ZoneControl, FC_StepMonitor, FC_ExecuteStep, FC_ExecuteInsertedStep, FC_ValidateSequence | 区域状态机、步骤监控 | 276 |
| `CIP_MediaControl.scl` | FC200_MediaSelect, FC_IsChemicalMedia, FC_CloseAllValves | 介质选择、阀门控制 | 121 |
| `CIP_PIDControl.scl` | FC_TempPIDControl, FC_FlowPIDControl | 温度/流量PID | 147 |

### utility/ - 工具函数

| 文件 | 函数 | 功能 | 行数 |
|------|------|------|------|
| `CIP_Alarm.scl` | FC300_AlarmHandler, FC_CheckAlarms, FC_TriggerAlarm | 报警处理 | 129 |
| `CIP_History.scl` | FC_LogHistory | 历史记录 | 89 |
| `CIP_Sensor.scl` | FC_ReadSensorData, FC_MonitorReturnTemp | 传感器、返回温度 | 97 |
| `CIP_Queue.scl` | FC400_QueueManager, FC_AddToQueue | 清洗队列 | 89 |
| `CIP_System.scl` | FC_EmergencyStop, FC_InitGlobalData, FC_InitZoneData, FC_InitRecipeData, FC_InitTankData, FC_ManageMediaResources, FC_RequestMedia, FC_ReleaseAllMedia, FC_UpdateZoneData, FC_UpdateSystemStatus, FC_UpdateSecondTimers | 系统功能 | 481 |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.0 | 2026-05-14 | 文件拆分重构，按功能模块分类 |
| v1.0 | 2026-05-14 | 初始版本，单文件设计 |
