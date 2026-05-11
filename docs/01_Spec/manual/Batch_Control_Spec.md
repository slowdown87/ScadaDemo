# Batch_Control_Spec

> 文档版本: v1.0
> 创建日期: 2026-04-30
> 所属工段: 批次控制（EX萃取、BL调配）
> PLC编号: PLC-3(EX)、PLC-5(BL)
> 控制级别: **P1 - 重要**
> 数据来源: BL_调配控制规格.md、EX_萃取控制规格.md

---

## 1. 概述

### 1.1 目的

本文档定义茶饮料生产线批次控制系统的通用规格，作为PLC程序开发、SCADA画面设计、操作员操作的基准依据。批次控制系统涵盖从原料处理（萃取）到产品调配的完整批次控制流程。

### 1.2 系统定位

| 项目 | 说明 |
|------|------|
| 控制范围 | EX萃取工段 + BL调配工段 |
| 控制类型 | **批次顺序控制 + 连续PID控制** |
| 控制重点 | 配方管理、顺序控制、质量监控、批次追溯 |
| 重要性 | **核心批次工段**，直接影响产品品质和产能 |
| 批次类型 | 茶叶萃取批次、调配批次 |

### 1.3 核心技术指标

| 参数 | 设定值 | 控制精度 | 控制方式 |
|------|--------|----------|----------|
| 批次容量 | 2000L | ±2% | 液位计量 |
| 配料精度 | ±2% | ±2% | 流量累计 |
| Brix值 | 5.5°Bx | ±1.0°Bx | 串级PID |
| pH值 | 3.8 | ±0.5 | PID控制 |
| 萃取温度 | 85℃ | ±2℃ | PID控制 |
| 批次周期 | 45-60min | - | 时间控制 |

---

## 2. 批次控制架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           批次控制系统架构                                           │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                         批次调度层 (Batch Scheduler)                          │   │
│  │   - 批次队列管理                                                             │   │
│  │   - 工段协调 (EX→FL→HM→BL)                                                 │   │
│  │   - 产能优化调度                                                             │   │
│  └──────────────────────────────────┬────────────────────────────────────────┘   │
│                                       │                                            │
│  ┌────────────────────────────────────┼────────────────────────────────────────┐   │
│  │                                    │                                            │   │
│  ▼                                    ▼                                            ▼   │
│  ┌──────────────────────┐    ┌──────────────────────┐    ┌──────────────────────┐   │
│  │   萃取批次控制器      │    │    过滤/均质         │    │   调配批次控制器     │   │
│  │   (FB_EX_Batch)      │───▶│   连续处理           │───▶│   (FB_BL_Batch)     │   │
│  │   PLC-3              │    │   PLC-4/5            │    │   PLC-5              │   │
│  └──────────────────────┘    └──────────────────────┘    └──────────────────────┘   │
│           │                                                            │             │
│           │                                                            │             │
│           ▼                                                            ▼             │
│  ┌──────────────────────┐                              ┌──────────────────────┐       │
│  │  三级逆流萃取        │                              │  配方管理器          │       │
│  │  TK-201/202/203     │                              │  FB_Recipe_Manager   │       │
│  └──────────────────────┘                              └──────────────────────┘       │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 批次管理器架构

```
┌─────────────────────────────────────────────────────────┐
│              FB_Batch_Manager                           │
├─────────────────────────────────────────────────────────┤
│ 功能: 批次状态机管理，配方执行，数据记录                   │
│                                                      │
│ INPUT:                                               │
│   - Recipe_Select : INT    // 配方选择 (1-20)        │
│   - Batch_Start   : BOOL   // 批次启动命令           │
│   - Batch_Stop    : BOOL   // 批次停止命令           │
│   - Batch_Pause   : BOOL   // 批次暂停命令           │
│   - Reset         : BOOL   // 复位命令               │
│                                                      │
│ OUTPUT:                                              │
│   - Batch_Status  : INT    // 批次状态 (0-9)        │
│   - Current_Step   : INT    // 当前步骤              │
│   - Step_Progress : REAL   // 步骤进度 (%)          │
│   - Batch_Complete: BOOL   // 批次完成标志           │
│   - Batch_Fault   : BOOL   // 批次故障标志           │
│   - Batch_ID      : STRING // 批次号                  │
│                                                      │
│ IN_OUT:                                              │
│   - Recipe_Data   : RecipeStruct  // 配方数据       │
│   - Batch_Record  : BatchLogStruct // 批次记录       │
│                                                      │
│ PARAM:                                               │
│   - Max_Steps     : INT := 20   // 最大步骤数       │
│   - Timeout       : TIME := 2H  // 批次超时          │
│                                                      │
└─────────────────────────────────────────────────────────┘
```

### 2.3 批次状态定义

| 状态码 | 状态名称 | 说明 |
|--------|----------|------|
| 0 | IDLE | 空闲，等待配方加载 |
| 1 | LOADING | 配方加载中 |
| 2 | WAIT | 等待启动条件 |
| 3 | RUNNING | 批次运行中 |
| 4 | PAUSED | 批次暂停 |
| 5 | STEP_COMPLETE | 步骤完成 |
| 6 | QUALITY_CHECK | 质量检查中 |
| 7 | COMPLETE | 批次完成 |
| 8 | ABORTED | 批次中止 |
| 9 | FAULT | 批次故障 |

---

## 3. 配方管理

### 3.1 配方结构

```yaml
batch_recipe:
  recipe_id: "BL-001"
  recipe_name: "绿茶饮料调配"
  version: "v1.0"
  batch_size: 2000L

  ingredients:
    tea_concentrate:
      id: "IC-001"
      name: "茶浓缩汁"
      amount: 400L
      tolerance: 2.0
      brix: 8.0
      temperature_min: 60
      temperature_max: 80

    sugar_syrup:
      id: "IC-002"
      name: "糖浆"
      amount: 150L
      tolerance: 2.0
      brix: 65.0

    citric_acid:
      id: "IC-003"
      name: "柠檬酸"
      amount: 5kg
      tolerance: 2.0
      concentration: 50.0

    tea_aroma:
      id: "IC-004"
      name: "茶香精"
      amount: 2L
      tolerance: 1.0

    water:
      id: "IC-005"
      name: "纯水"
      amount: 1443L
      tolerance: 2.0

  quality_targets:
    final_brix:
      target: 5.5
      tolerance: 1.0
      unit: "°Bx"
    final_ph:
      target: 3.8
      tolerance: 0.5
    final_volume:
      target: 2000
      tolerance: 2.0
      unit: "L"
    temperature:
      target: 25
      tolerance: 5.0
      unit: "°C"

  process_steps:
    - step: 1
      name: "添加纯水"
      action: ADD_WATER
      target_level: 30
      unit: "%"
      time_limit: 300
      timeout_action: PAUSE

    - step: 2
      name: "添加茶浓缩汁"
      action: ADD_INGREDIENT
      ingredient: tea_concentrate
      target_brix: 2.5
      time_limit: 600
      timeout_action: PAUSE

    - step: 3
      name: "添加糖浆"
      action: ADD_INGREDIENT
      ingredient: sugar_syrup
      target_brix: 5.5
      time_limit: 300
      timeout_action: PAUSE

    - step: 4
      name: "添加柠檬酸"
      action: ADD_INGREDIENT
      ingredient: citric_acid
      target_ph: 3.8
      time_limit: 180
      timeout_action: PAUSE

    - step: 5
      name: "添加茶香精"
      action: ADD_INGREDIENT
      ingredient: tea_aroma
      time_limit: 60
      timeout_action: PAUSE

    - step: 6
      name: "补水至目标量"
      action: ADD_WATER
      target_level: 100
      time_limit: 180
      timeout_action: PAUSE

    - step: 7
      name: "搅拌混合"
      action: MIX
      time_limit: 900
      speed: 50
      interval: 30

    - step: 8
      name: "质量确认"
      action: QUALITY_CHECK
      check_points:
        - brix: 5.5 ± 1.0
        - ph: 3.8 ± 0.5
        - temperature: 25 ± 5
      time_limit: 120
      retry_limit: 3

    - step: 9
      name: "转移至均质"
      action: TRANSFER
      destination: HM
      time_limit: 300
      condition: QUALITY_PASSED
```

### 3.2 配方加载流程

```
┌─────────────────────────────────────────────────────────┐
│              配方加载流程 (FB_Recipe_Loader)             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  配方选择 ──▶ 配方验证 ──▶ 参数下载 ──▶ 批次就绪        │
│      │           │            │            │             │
│      ▼           ▼            ▼            ▼             │
│   选择配方   检查配方完整  下载到PLC    启动允许         │
│   (HMI)     性+版本      DB块         检查             │
│                                                          │
│  验证内容:                                               │
│    - 配方ID存在                                         │
│    - 配方版本有效                                         │
│    - 原料清单完整                                         │
│    - 质量目标合理                                         │
│    - 步骤顺序正确                                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 顺序控制

### 4.1 批次执行状态机

```
                    ┌─────────┐
                    │  IDLE   │
                    └────┬────┘
                         │ Load_Recipe
                         ▼
                    ┌─────────┐
              ┌─────│LOADING  │─────┐
              │     └────┬────┘     │
              │          │ OK       │ Error
              │          ▼          ▼
              │     ┌─────────┐  ┌─────────┐
              │     │  WAIT   │  │ FAULT   │
              │     └────┬────┘  └────┬────┘
              │          │ Start     │ Reset
              │          ▼           │
              │     ┌─────────┐       │
              │     │RUNNING │       │
              │     └────┬────┘       │
              │          │             │
              │    ┌─────┴─────┐      │
              │    │           │      │
              │    ▼           ▼      │
         Step_Complete    Pause       │
              │    │           │      │
              │    └─────┬─────┘      │
              │          │ Resume     │
              │          ▼            │
              │     ┌─────────┐       │
              │     │PAUSED   │───────┘
              │     └─────────┘
              │
              │ Last_Step
              ▼
         ┌─────────┐
         │QUALITY  │
         │_CHECK   │
         └────┬────┘
              │ Pass/Fail
              ▼
         ┌─────────┐
         │COMPLETE │ or ABORTED
         └─────────┘
```

### 4.2 启动允许条件

| 条件 | 检查项 | 来源 | 说明 |
|------|--------|------|------|
| 配方已加载 | Recipe_Loaded | 内部 | 配方数据完整 |
| 设备就绪 | Equipment_Ready | DI点 | 各设备无故障 |
| 上游就绪 | Upstream_Ready | 通讯 | 前工段可供应 |
| 原料充足 | Ingredient_Level | 液位检测 | 原料足够 |
| 操作员确认 | Operator_Ack | HMI按钮 | 确认开始 |

### 4.3 步骤执行控制

```
┌─────────────────────────────────────────────────────────┐
│              步骤执行控制器 (FB_Step_Controller)        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ INPUT:                                                   │
│   - Step_Command : INT     // 步骤命令 (0=空闲,1=启动)  │
│   - Step_Config  : StepStruct // 步骤配置               │
│                                                          │
│ OUTPUT:                                                  │
│   - Step_Status  : INT     // 步骤状态                  │
│   - Step_Timer   : TIME    // 步骤计时                 │
│   - Step_Progress: REAL    // 步骤进度 (0-100%)        │
│   - Step_Done    : BOOL    // 步骤完成                 │
│   - Step_Fault   : BOOL    // 步骤故障                 │
│                                                          │
│ IN_OUT:                                                  │
│   - Measured_Value: REAL    // 测量值                    │
│   - Setpoint      : REAL    // 设定值                   │
│                                                          │
│ LOGIC:                                                   │
│   CASE Step_Command OF                                  │
│   1: // 执行配料                                         │
│      IF Measured >= Setpoint * (1 - Tolerance) THEN      │
│          Step_Progress := Measured/Setpoint * 100;       │
│          IF Measured >= Setpoint THEN                    │
│              Step_Done := TRUE;                         │
│          END_IF;                                        │
│      END_IF;                                            │
│                                                          │
│   2: // 时间等待                                         │
│      Step_Timer := Step_Timer + CycleTime;              │
│      Step_Progress := Step_Timer / Step_Time * 100;     │
│      IF Step_Timer >= Step_Time THEN                     │
│          Step_Done := TRUE;                             │
│      END_IF;                                            │
│                                                          │
│   3: // 质量检查                                         │
│      IF Quality_Check(Measured, Setpoint, Tolerance)     │
│          Step_Done := TRUE;                             │
│      END_IF;                                            │
│                                                          │
│   END_CASE;                                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 5. 质量控制

### 5.1 质量监控点

| 工段 | 监控参数 | 位号 | 设定值 | 控制精度 | 监控方式 |
|------|----------|------|--------|----------|----------|
| EX | 萃取温度 | TT-201~203 | 85℃ | ±2℃ | PID |
| EX | 茶水比 | WT/FT | 1:12 | ±3% | 重量控制 |
| EX | 茶汁浓度 | BT-204 | 2.5°Brix | ±0.2°Brix | 监控 |
| BL | Brix值 | BT-101/102 | 5.5°Bx | ±1.0°Bx | 串级PID |
| BL | pH值 | AT-101/102 | 3.8 | ±0.5 | PID |
| BL | 液位 | LT-101/102 | 目标值 | ±2% | PID |

### 5.2 Brix串级控制

```
┌─────────────────────────────────────────────────────────┐
│              Brix串级控制架构                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│         ┌──────────────────┐                            │
│         │ 外环: Brix主控   │                            │
│         │   BIC-201       │                            │
│         │  设定: 5.5°Bx   │                            │
│         └────────┬─────────┘                            │
│                  │                                       │
│                  │ 糖浆流量设定                          │
│                  ▼                                       │
│         ┌──────────────────┐                            │
│         │ 内环: 流量副控   │                            │
│         │   FIC-201       │                            │
│         │  反馈: FV流量   │                            │
│         └────────┬─────────┘                            │
│                  │                                       │
│                  │ 调节阀输出                            │
│                  ▼                                       │
│         ┌──────────────────┐                            │
│         │   FV-201        │                            │
│         │  糖浆调节阀     │                            │
│         └────────┬─────────┘                            │
│                  │                                       │
│                  │ 糖浆流量反馈                          │
│                  ▼                                       │
│         ┌──────────────────┐                            │
│         │   FT-201        │                            │
│         │  质量流量计     │                            │
│         └──────────────────┘                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 5.3 质量判定标准

| 参数 | 合格标准 | 处理方式 |
|------|----------|----------|
| Brix值 | 5.5±1.0°Bx | 超出则调整 |
| pH值 | 3.8±0.5 | 超出则调整 |
| 温度 | 25±5℃ | 超出则等待 |
| 液位 | 目标值±2% | 不达标则重配 |

---

## 6. 批次记录

### 6.1 批次记录结构

```yaml
batch_record:
  batch_id: "B20260430001"
  recipe_id: "BL-001"
  recipe_name: "绿茶饮料调配"

  timing:
    planned_start: "2026-04-30 08:00:00"
    actual_start: "2026-04-30 08:02:35"
    planned_end: "2026-04-30 08:55:00"
    actual_end: "2026-04-30 08:52:18"
    total_time: 2963
    unit: "seconds"

  ingredients_actual:
    tea_concentrate:
      planned: 400L
      actual: 398.5L
      deviation: -0.4%
    sugar_syrup:
      planned: 150L
      actual: 151.2L
      deviation: +0.8%
    citric_acid:
      planned: 5kg
      actual: 4.95kg
      deviation: -1.0%
    tea_aroma:
      planned: 2L
      actual: 2.0L
      deviation: 0.0%
    water:
      planned: 1443L
      actual: 1448.3L
      deviation: +0.4%

  quality_results:
    final_brix:
      target: 5.5
      actual: 5.48
      deviation: -0.4%
      status: PASS
    final_ph:
      target: 3.8
      actual: 3.82
      deviation: +0.5%
      status: PASS
    final_volume:
      target: 2000L
      actual: 2000.0L
      deviation: 0.0%
      status: PASS

  step_records:
    - step: 1
      name: "添加纯水"
      duration: 245s
      status: COMPLETE
    - step: 2
      name: "添加茶浓缩汁"
      duration: 512s
      status: COMPLETE
    # ... 其他步骤记录

  operator:
    batch_creator: "张三"
    batch_released: "李四"
    batch_supervisor: "王五"

  status: COMPLETE
  release_status: RELEASED
```

### 6.2 批次号编码规则

```
B + YYYYMMDD + 序号(3位)
例如: B20260430001
  B        = 批次标识
  20260430 = 生产日期
  001      = 当日第1批
```

### 6.3 批次追溯

| 追溯项 | 数据来源 | 保存周期 |
|--------|----------|----------|
| 原料批次 | 配料记录 | 2年 |
| 操作记录 | 批次日志 | 2年 |
| 质量数据 | 过程数据 | 2年 |
| 设备参数 | 参数记录 | 2年 |
| 操作员 | 用户登录 | 2年 |

---

## 7. 报警与联锁

### 7.1 批次报警配置

| 报警号 | 描述 | 等级 | 设定值 | 处理方式 |
|--------|------|------|--------|----------|
| B001 | 配料超差 | L1 | >±2% | 暂停+确认 |
| B002 | 配料超时 | L2 | >设定时间 | 暂停+提示 |
| B003 | Brix超限 | L1 | >±1.0°Bx | 暂停+调整 |
| B004 | pH超限 | L1 | >±0.5 | 暂停+调整 |
| B005 | 批次超时 | L2 | >2小时 | 报警+确认 |
| B006 | 配方数据错误 | L0 | - | 禁止启动 |
| B007 | 质量不达标 | L1 | 3次重试失败 | 隔离+审批 |
| B008 | 原料不足 | L2 | <批次需求 | 暂停+补料 |

### 7.2 批次联锁逻辑

| 联锁条件 | 联锁动作 | 复位方式 |
|----------|----------|----------|
| 配料超差>±5% | 批次暂停，阀门关闭 | 手动复位 |
| Brix连续3次不合格 | 批次隔离，等待审批 | 工程师复位 |
| 设备故障 | 批次暂停，安全停机 | 故障清除后复位 |
| 急停触发 | 批次中止，阀门复位 | 手动复位 |

---

## 8. 功能块规格

### 8.1 功能块清单

| 功能块 | 功能描述 | 版本 | 调用位置 |
|--------|----------|------|----------|
| FB_Batch_Manager | 批次状态机管理 | v1.0 | OB100 |
| FB_Recipe_Loader | 配方加载与验证 | v1.0 | OB100 |
| FB_Step_Controller | 步骤执行控制 | v1.0 | OB100 |
| FB_Brix_Cascade | Brix串级控制器 | v1.0 | OB100 |
| FB_PH_Controller | pH控制器 | v1.0 | OB100 |
| FB_Flow_Accumulator | 流量累计器 | v1.0 | OB100 |
| FB_Batch_Recorder | 批次记录器 | v1.0 | OB100 |
| FB_Quality_Checker | 质量判定器 | v1.0 | OB100 |

### 8.2 核心功能块详细定义

#### FB_Batch_Manager

```
┌─────────────────────────────────────────────────────────┐
│              FB_Batch_Manager                            │
├─────────────────────────────────────────────────────────┤
│ 功能: 批次状态机管理                                     │
│                                                          │
│ INPUT:                                                   │
│   - iRecipe_Select : INT     // 配方选择 (1-20)        │
│   - iBatch_Start   : BOOL    // 批次启动               │
│   - iBatch_Stop    : BOOL    // 批次停止               │
│   - iBatch_Pause   : BOOL    // 批次暂停               │
│   - iReset         : BOOL    // 复位                   │
│                                                          │
│ OUTPUT:                                                  │
│   - qBatch_Status  : INT     // 批次状态 (0-9)        │
│   - qCurrent_Step  : INT     // 当前步骤              │
│   - qStep_Progress : REAL    // 步骤进度 (%)          │
│   - qBatch_Complete: BOOL    // 批次完成               │
│   - qBatch_Fault   : BOOL    // 批次故障               │
│   - qBatch_ID      : STRING  // 批次号                 │
│                                                          │
│ IN_OUT:                                                  │
│   - xRecipe_Loaded : BOOL    // 配方已加载标志         │
│   - xBatch_Started : BOOL    // 批次已启动标志         │
│                                                          │
│ PARAM:                                                   │
│   - Max_Steps      : INT := 20  // 最大步骤数          │
│   - Batch_Timeout  : TIME := 2H // 批次超时时间        │
│                                                          │
│ LOGIC:                                                   │
│   // 状态机转换逻辑                                      │
│   CASE qBatch_Status OF                                 │
│   0: // IDLE                                            │
│       IF iRecipe_Select > 0 THEN                         │
│           qBatch_Status := 1; // LOADING               │
│       END_IF;                                           │
│                                                          │
│   1: // LOADING                                         │
│       IF Recipe_Load_OK() THEN                          │
│           qBatch_Status := 2; // WAIT                   │
│       END_IF;                                           │
│                                                          │
│   2: // WAIT                                            │
│       IF iBatch_Start AND Start_Conditions_OK() THEN    │
│           qBatch_Status := 3; // RUNNING                │
│           Generate_Batch_ID();                           │
│       END_IF;                                           │
│                                                          │
│   3: // RUNNING                                         │
│       Execute_Current_Step();                            │
│       IF Step_Complete() THEN                            │
│           IF Last_Step() THEN                           │
│               qBatch_Status := 6; // QUALITY_CHECK     │
│           ELSE                                          │
│               qBatch_Status := 5; // STEP_COMPLETE     │
│               qCurrent_Step := qCurrent_Step + 1;      │
│           END_IF;                                       │
│       END_IF;                                           │
│       IF iBatch_Pause THEN                              │
│           qBatch_Status := 4; // PAUSED                 │
│       END_IF;                                           │
│                                                          │
│   4: // PAUSED                                          │
│       IF NOT iBatch_Pause THEN                          │
│           qBatch_Status := 3; // RUNNING                │
│       END_IF;                                           │
│                                                          │
│   5: // STEP_COMPLETE                                   │
│       qBatch_Status := 3; // RUNNING (自动进入下一步)   │
│                                                          │
│   6: // QUALITY_CHECK                                    │
│       IF Quality_Check_Pass() THEN                      │
│           qBatch_Status := 7; // COMPLETE               │
│       ELSE                                              │
│           Retry_Count := Retry_Count + 1;               │
│           IF Retry_Count >= 3 THEN                      │
│               qBatch_Fault := TRUE;                     │
│               qBatch_Status := 8; // ABORTED            │
│           END_IF;                                       │
│       END_IF;                                           │
│                                                          │
│   7: // COMPLETE                                        │
│       qBatch_Complete := TRUE;                          │
│       Save_Batch_Record();                              │
│                                                          │
│   8: // ABORTED                                         │
│       Save_Batch_Record();                              │
│                                                          │
│   9: // FAULT                                           │
│       IF iReset THEN                                    │
│           Reset_Batch_Data();                           │
│           qBatch_Status := 0; // IDLE                   │
│       END_IF;                                           │
│                                                          │
│   END_CASE;                                             │
│                                                          │
│   // 超时检测                                           │
│   IF Batch_Running_Time > Batch_Timeout THEN            │
│       Generate_Alarm(B005);                             │
│       qBatch_Fault := TRUE;                            │
│   END_IF;                                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### FB_Recipe_Loader

```
┌─────────────────────────────────────────────────────────┐
│              FB_Recipe_Loader                           │
├─────────────────────────────────────────────────────────┤
│ 功能: 配方加载与验证                                     │
│                                                          │
│ INPUT:                                                   │
│   - iRecipe_Select : INT     // 配方选择号              │
│   - iLoad_Command  : BOOL    // 加载命令                │
│                                                          │
│ OUTPUT:                                                  │
│   - qLoad_Status   : INT     // 加载状态 (0=空闲,1=加载中,2=成功,3=失败) │
│   - qRecipe_Valid  : BOOL    // 配方有效标志           │
│   - qError_Code    : INT     // 错误代码                │
│                                                          │
│ IN_OUT:                                                  │
│   - Recipe_Data    : RecipeStruct // 配方数据结构       │
│                                                          │
│ LOGIC:                                                   │
│   qLoad_Status := 1; // 加载中                          │
│                                                          │
│   // 读取配方数据                                       │
│   Recipe_Data := Read_Recipe_DB(iRecipe_Select);        │
│                                                          │
│   // 配方验证                                           │
│   IF Recipe_Data.ID = 0 THEN                            │
│       qLoad_Status := 3; // 失败                        │
│       qError_Code := 1; // 配方不存在                   │
│       RETURN;                                           │
│   END_IF;                                               │
│                                                          │
│   IF NOT Validate_Recipe(Recipe_Data) THEN             │
│       qLoad_Status := 3; // 失败                        │
│       qError_Code := 2; // 配方验证失败                 │
│       RETURN;                                           │
│   END_IF;                                               │
│                                                          │
│   // 下载配方参数到控制DB                               │
│   Download_Recipe_To_Control(Recipe_Data);              │
│                                                          │
│   qLoad_Status := 2; // 成功                           │
│   qRecipe_Valid := TRUE;                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 8.3 数据块清单

| 数据块 | 名称 | 类型 | 用途 |
|--------|------|------|------|
| DB_Batch_Config | 批次配置 | 参数 | 批次运行参数 |
| DB_Batch_Status | 批次状态 | 状态 | 批次运行状态 |
| DB_Recipe_List | 配方列表 | 参数 | 配方存储区 |
| DB_Batch_Log | 批次记录 | 日志 | 历史批次记录 |
| DB_Batch_Statistics | 批次统计 | 统计 | 批次统计信息 |

---

## 9. 数据采集

### 9.1 采集参数清单

| 位号 | 描述 | 类型 | 采集周期 | 存储周期 |
|------|------|------|----------|----------|
| BT-101/102 | 调配罐Brix值 | AI | 10s | 1min平均 |
| AT-101/102 | 调配罐pH值 | AI | 10s | 1min平均 |
| LT-101/102 | 调配罐液位 | AI | 1s | 1min平均 |
| FT-xxx | 原料流量 | AI | 1s | 累计 |
| TT-101/102 | 调配罐温度 | AI | 30s | 1min平均 |
| TT-201~203 | 萃取罐温度 | AI | 10s | 1min平均 |
| BT-204 | 茶汁Brix值 | AI | 30s | 1min平均 |

### 9.2 历史数据存储

| 参数 | 存储方式 | 保留时间 | 说明 |
|------|----------|----------|------|
| 批次记录 | 记录 | 2年 | 完整追溯 |
| 质量趋势 | 曲线 | 1年 | 每分钟数据 |
| 报警记录 | 事件 | 1年 | 完整记录 |
| 配方修改 | 审计 | 永久 | 合规要求 |

---

## 10. HMI画面

### 10.1 批次控制主画面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  批次控制系统                                                    [主画面]  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ 批次状态: [●运行]  批次号: B20260430001  配方: 绿茶饮料调配          │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────────┐ │
│  │ 当前步骤: 3/9           │  │  步骤进度                              │ │
│  │ 添加糖浆                │  │  [████████████████░░░░] 78%           │ │
│  │ 目标Brix: 5.5°Bx       │  │  配方进度: [████████░░░░░░░░░] 33%   │ │
│  │ 当前Brix: 4.28°Bx      │  │                                         │ │
│  └─────────────────────────┘  └─────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │  质量监控                                                             │ │
│  │  Brix: 4.28°Bx [●]    pH: 3.82 [●]    温度: 25.3°C [●]           │ │
│  │  液位: 1560L [●]      累计时间: 00:18:35 [●]                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │ 操作: [启动] [暂停] [停止] [急停] [配方选择] [批次记录]              │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. 附录

### 11.1 专业术语定义

| 缩写 | 全称 | 中文 |
|------|------|------|
| Batch | Batch | 批次 |
| Recipe | Recipe | 配方 |
| Step | Process Step | 工艺步骤 |
| Brix | Brix | 白利度（糖度） |
| CCP | Critical Control Point | 关键控制点 |
| Cascade | Cascade Control | 串级控制 |

### 11.2 版本记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-04-30 | 初始版本，基于BL_调配控制规格批次控制章节 |

---

**文档状态**: 正式版
**审核状态**: 待审核
**批准人**: -
