# CIP清洗系统 - PLC程序文件索引

> 文档版本: v2.0
> 更新日期: 2026-05-15
> PLC: S7-1500 (TIA Portal V17)
> 用途: CIP就地清洗系统PLC控制程序

---

## 📁 文件目录结构

```
project/plc/
├── types/                    # 数据类型定义
│   ├── CIP_EnumTypes.scl    # 枚举类型 (7个)
│   ├── CIP_StructTypes.scl  # 结构体类型 (9个)
│   └── CIP_DataBlockDefs.scl # DB块模板 (参考)
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

---

## 🎯 系统架构

### 5区同时清洗架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CIP清洗系统架构                                     │
│                                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│  │  1区    │    │  2区    │    │  3区    │    │  4区    │    │  5区    │ │
│  │ 水处理   │    │ 茶叶    │    │ 调配    │    │  UHT   │    │ 灌装    │ │
│  │ P-CP01  │    │ P-CP02  │    │ P-CP03  │    │ P-CP04  │    │ P-CP05  │ │
│  │ Zx-V-01~5│    │ Zx-V-01~5│    │ Zx-V-01~5│    │ Zx-V-01~5│    │ Zx-V-01~5│ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════  │
│                              公用管路                                        │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│     │  碱液罐   │  │  酸液罐   │  │  热水罐   │  │  纯水罐   │                │
│     │ 2% NaOH  │  │ 1% HNO₃ │  │  85℃    │  │  常温    │                │
│     └──────────┘  └──────────┘  └──────────┘  └──────────┘                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 阀门控制矩阵

| 阀门类型 | 代码 | 说明 |
|----------|------|------|
| 公用介质阀 | M-V-01~06 | 碱/酸/热水/纯水/循环/排放 |
| 分区阀门 | Zx-V-01~05 | 每区5个：进液/回流/排放/循环/介质选择 |

---

## 📦 数据类型定义 (types/)

### 枚举类型 (7个)

| 枚举 | 值范围 | 用途 |
|------|--------|------|
| `Enum_MediaType` | PURE_WATER(0), ALKALI(1), ACID(2), HOT_WATER(3), DISINFECT(4) | 清洗介质类型 |
| `Enum_CleanState` | IDLE(0), READY(1), STEP_EXEC(2), STEP_TRANSITION(3), COMPLETE(4), PAUSE(5), FAULT(6) | 清洗状态机 |
| `Enum_AlarmLevel` | L0_CRITICAL(0), L1_WARNING(1), L2_INFO(2) | 报警等级 |
| `Enum_HandsMode` | LOCAL(0), REMOTE(1) | 就地/远程模式 |
| `Enum_ValveState` | VALVE_CLOSED(0), VALVE_OPEN(1), VALVE_FAULT(2) | 阀门状态 |
| `Enum_PumpState` | PUMP_STOP(0), PUMP_RUN(1), PUMP_FAULT(2), PUMP_WARNING(3) | 泵状态 |
| `Enum_ControlCmd` | CMD_NONE(0), CMD_START(1), CMD_STOP(2), CMD_PAUSE(3), CMD_RESUME(4), CMD_RESET(5) | 控制命令 |

### 结构体类型 (9个)

| 结构体 | 用途 |
|--------|------|
| `UDT_StepData` | 单个清洗步骤数据（介质/温度/时间/流量/电导率） |
| `UDT_RecipeData` | 清洗配方数据（最多10步骤） |
| `UDT_ZoneData` | 单区状态数据（状态机/传感器/设备/报警） |
| `UDT_MediaStatus` | 介质状态（使用中区域/请求队列） |
| `UDT_TankStatus` | 罐区状态（液位/温度/电导率） |
| `UDT_AlarmInfo` | 报警信息（ID/代码/等级/时间戳） |
| `UDT_HistoryRecord` | 历史记录（10步骤详情/结果/操作员） |
| `UDT_PIDParams` | PID参数（Kp/Ki/Kd/SP/PV/MV/限幅） |
| `UDT_SystemStatus` | 系统状态（运行模式/连接状态/统计数据） |

---

## 🔄 组织块 (ob/)

### CIP_OB.scl

| OB | 周期 | 功能 |
|----|------|------|
| **OB1** | 循环扫描 | 急停检查 → 模式检查 → 主调度 → 系统状态更新 |
| **OB100** | 启动 | 全局数据初始化 → 各区数据初始化 → 配方初始化 → 复位急停 |
| **OB35** | 100ms | 传感器采集 → PID控制 → 报警检测 → 秒级计时 |

### OB1 执行流程

```
OB1_Main
├── 1. 急停检查 → FC_EmergencyStop (急停时直接RETURN)
├── 2. 模式检查 → LOCAL模式直接RETURN
├── 3. CIP主调度 → FC100_CIP_System()
└── 4. 系统状态 → FC_UpdateSystemStatus()
```

### OB35 执行流程

```
OB35 (100ms)
├── 1. 传感器采集 → FC_ReadSensorData()
├── 2. 温度PID → FC_TempPIDControl()
├── 3. 流量PID → FC_FlowPIDControl(i) ×5区
├── 4. 报警检测 → FC_CheckAlarms()
└── 5. 秒级计时 → FC_UpdateSecondTimers() (每10个100ms)
```

---

## ⚙️ 控制逻辑 (control/)

### CIP_Main.scl - 主调度

| 函数 | 功能 |
|------|------|
| **FC100_CIP_System** | 主调度：更新区域数据 → 处理队列 → 执行各区控制 → 介质管理 → 报警处理 |
| **FC101~105_ZoneControl** | 各区控制封装（调用通用FC_ZoneControl） |

### CIP_ZoneControl.scl - 区域清洗控制

| 函数 | 功能 |
|------|------|
| **FC_ZoneControl** | 区域状态机（7状态转换） |
| **FC_ExecuteStep** | 执行清洗步骤（介质选择/泵启动/温度控制） |
| **FC_StepMonitor** | 步骤监控（温度监测/完成判定/无流量检测） |
| **FC_ExecuteInsertedStep** | 执行插入的冲洗步骤（化学介质间自动插入） |
| **FC_ValidateSequence** | 校验清洗序列（防止化学介质直接切换） |

### 状态机转换

```
     ┌──────────────────────────────────────────────────────────┐
     │                                                          │
     ▼                                                          │
  ┌──────┐    启动命令     ┌──────┐    步骤完成     ┌─────────────┐
  │ IDLE │──────────────▶│ READY │───────────────▶│ STEP_EXEC  │
  │ 待机 │               │就绪   │                │ 步骤执行中  │
  └──────┘               └───┬──┘                └──────┬──────┘
     ▲                       │                           │
     │                       │ 序列非法                  │ 步骤完成
     │                       ▼                           ▼
     │                    ┌──────┐               ┌─────────────┐
     │                    │ FAULT│               │STEP_TRANSITION
     │ 复位命令           │ 故障 │               │  步骤切换中  │
     │                    └──┬───┘               └──────┬──────┘
     │                       │                          │
     │◀──────────────────────┘                          │
     │                                                  │
     │◀─────────────────────────────────────────────────┘
     │
  ┌──────────┐    恢复命令     ┌────────┐
  │  PAUSE   │◀──────────────│ 任意  │
  │   暂停   │               │ 状态   │
  └──────────┘    停止命令     └───┬──┘
                                   │
                                   ▼
                              ┌──────────┐
                              │ COMPLETE │
                              │  清洗完成 │
                              └─────┬────┘
                                    │ 完成记录
                                    ▼
                                 ┌──────┐
                                 │ IDLE │
                                 │ 待机  │
                                 └──────┘
```

### CIP_MediaControl.scl - 介质选择

| 函数 | 功能 |
|------|------|
| **FC200_MediaSelect** | 分区介质选择（公用阀+分区阀组合） |
| **FC_IsChemicalMedia** | 判断是否为化学介质 |
| **FC_CloseAllValves** | 关闭所有阀门 |

### 阀门组合逻辑

| 介质 | 公用阀 | 分区阀门组合 | 说明 |
|------|--------|--------------|------|
| 纯水 | PureWater | 进液 + 排放 | 预冲洗/最终冲洗 |
| 碱/酸/热水/消毒液 | Alkali/Acid/HotWater/Disinfect | 进液 + 循环 | 化学清洗 |

### CIP_PIDControl.scl - PID控制

| 函数 | 功能 |
|------|------|
| **FC_TempPIDControl** | 温度PID（完整PID+死区+积分限幅+多区协调） |
| **FC_FlowPIDControl** | 流量PID（各区独立） |

### PID参数

| 参数类型 | Kp | Ti (s) | Td (s) | 死区 |
|----------|-----|--------|--------|------|
| 温度PID | 2.0 | 60 | 10 | 2.0℃ |
| 流量PID | 2.0 | - | - | - |

---

## 🔧 工具函数 (utility/)

### CIP_Alarm.scl - 报警处理

| 函数 | 功能 |
|------|------|
| **FC300_AlarmHandler** | 报警处理（蜂鸣器控制） |
| **FC_CheckAlarms** | 报警检测（罐区液位/温度/泵过载） |
| **FC_TriggerAlarm** | 触发报警（去重/空闲槽分配） |

### 报警代码定义

| 报警号 | 描述 | 等级 | 处理 |
|--------|------|------|------|
| CP-001~004 | 碱/酸/热水/纯水罐液位低 | L2 | 提示补充 |
| CP-005 | 清洗温度不达标 | L1 | 延长清洗 |
| CP-006 | 电导率超标 | L1 | 增加冲洗 |
| CP-009 | 泵过载 | L0 | 停止清洗 |
| CP-012~016 | 1-5区无流量 | L1 | 检查管路 |
| CP-017 | 急停触发 | L0 | 复位启动 |
| CP-018 | 清洗序列非法 | L1 | 检查配方 |

### CIP_History.scl - 历史记录

| 函数 | 功能 |
|------|------|
| **FC_LogHistory** | 记录清洗历史（100条环形存储） |

### 历史记录字段

- RecordID, ZoneID, ZoneName
- RecipeID, RecipeName
- StartTime, EndTime, TotalTime
- Step1~10_Media, Step1~10_Time
- FinalConduct, Result, FailReason
- Operator

### CIP_System.scl - 系统功能

| 函数 | 功能 |
|------|------|
| **FC_EmergencyStop** | 急停处理 |
| **FC_InitGlobalData** | 初始化全局数据 |
| **FC_InitZoneData** | 初始化区域数据 |
| **FC_InitRecipeData** | 初始化配方数据（6个默认配方） |
| **FC_InitTankData** | 初始化罐区数据 |
| **FC_ManageMediaResources** | 介质资源管理 |
| **FC_RequestMedia** | 请求介质资源 |
| **FC_ReleaseAllMedia** | 释放介质资源 |
| **FC_UpdateZoneData** | 更新区域数据 |
| **FC_UpdateSystemStatus** | 更新系统状态 |
| **FC_UpdateSecondTimers** | 秒级计时更新 |

### 默认配方 (FC_InitRecipeData)

| 配方ID | 名称 | 步骤数 | 总时间 |
|--------|------|--------|--------|
| 1 | 纯水冲洗 | 1 | 10min |
| 2 | 热水冲洗 | 1 | 10min |
| 3 | 碱洗+冲洗 | 3 | 45min |
| 4 | 酸洗+冲洗 | 3 | 40min |
| 5 | 碱洗+酸洗+冲洗 | 5 | 70min |
| 6 | 消毒液清洗 | 3 | 25min |

---

## 📊 全局数据块结构

### Global_Data (DB1)

```
Global_Data
├── System: UDT_SystemStatus         // 系统状态
├── Valve: STRUCT                     // 阀门状态
│   ├── Alkali, Acid, HotWater, PureWater, Disinfect, Drain, Circulate
│   └── ZoneValve[1..25]: Bool      // 5区×5阀
├── PID_Temp[1..5]: UDT_PIDParams    // 温度PID参数
├── PID_Flow[1..5]: UDT_PIDParams    // 流量PID参数
├── MediaAlkali/Acid/HotWater/PureWater/Disinfect: UDT_MediaStatus
├── TankAlkali/Acid/HotWater/PureWater: UDT_TankStatus
├── AlarmActive[1..50]: UDT_AlarmInfo // 报警数组
├── History[1..100]: UDT_HistoryRecord // 历史记录(100条)
├── RecipeList[1..10]: UDT_RecipeData  // 配方列表
├── Output: STRUCT                   // 输出命令
│   ├── PumpCmd, SteamValve, Buzzer
├── AI_TT_Outlet[1..5], AI_TT_Return[1..5]: Real
├── AI_Conductivity[1..5], AI_Pressure[1..5], AI_Flow[1..5]: Real
└── DI_FlowSwitch[1..5], DI_PumpOverload[1..5]: Bool
```

### Zone_Data (DB100-DB104)

```
DB_Zone[1..5]
└── Zone: UDT_ZoneData               // 区域状态数据
```

---

## 📝 TIA Portal 导入顺序

### 导入顺序（必须按此顺序）

```
1️⃣ types/ (数据类型)
   ├── CIP_EnumTypes.scl      ← 先导入枚举
   ├── CIP_StructTypes.scl     ← 再导入结构体
   └── CIP_DataBlockDefs.scl  ← DB块模板(参考创建)

2️⃣ ob/ (组织块)
   └── CIP_OB.scl

3️⃣ control/ (控制逻辑)
   ├── CIP_Main.scl           ← 主调度
   ├── CIP_ZoneControl.scl    ← 区域控制
   ├── CIP_MediaControl.scl   ← 介质控制
   └── CIP_PIDControl.scl     ← PID控制

4️⃣ utility/ (工具函数)
   ├── CIP_System.scl         ← 系统功能
   ├── CIP_Queue.scl          ← 队列管理
   ├── CIP_Alarm.scl          ← 报警处理
   ├── CIP_History.scl        ← 历史记录
   └── CIP_Sensor.scl          ← 传感器
```

---

## 🔗 文件依赖关系

```
types/     (基础层 - 无依赖)
    │
    ├── CIP_EnumTypes.scl
    ├── CIP_StructTypes.scl
    └── CIP_DataBlockDefs.scl (参考)
           │
           ▼
ob/       (组织块层 - 依赖types)
    │
    └── CIP_OB.scl
           │
           ▼
control/  (控制层 - 依赖types/ob)
    │
    ├── CIP_Main.scl
    ├── CIP_ZoneControl.scl
    ├── CIP_MediaControl.scl
    └── CIP_PIDControl.scl
           │
           ▼
utility/  (工具层 - 依赖types/ob/control)
    │
    ├── CIP_System.scl
    ├── CIP_Queue.scl
    ├── CIP_Alarm.scl
    ├── CIP_History.scl
    └── CIP_Sensor.scl
```

---

## 📈 代码统计

| 目录 | 文件数 | 函数数 | 代码行数 |
|------|--------|--------|----------|
| types/ | 3 | 16 (类型定义) | ~470 |
| ob/ | 1 | 3 (OB) | ~135 |
| control/ | 4 | 12 | ~640 |
| utility/ | 5 | 22 | ~950 |
| **总计** | **13** | **~53** | **~2195** |

---

## ⚠️ 关键特性

### 1. 插入冲洗步骤
化学介质间自动插入纯水冲洗，防止交叉污染

### 2. 多区介质协调
碱/酸/热水/消毒液独占使用，纯水可多区共享

### 3. 返回温度监测
监控进出口温差，防止热交换器故障

### 4. 无流量保护
30秒无流量自动暂停并报警

### 5. 温度达标计时
温度达标后才开始步骤计时

---

**最后更新**: 2026-05-15
**维护者**: 项目组
**版本**: v2.0
