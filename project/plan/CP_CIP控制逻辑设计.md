# CIP清洗系统控制逻辑设计

> 文档版本: v2.0
> 创建日期: 2026-05-12
> 更新日期: 2026-05-12
> 工段: CP (CIP Cleaning In Place)
> PLC: PLC-16 (192.168.2.26)

---

## 1. 系统控制架构

### 1.1 5区同时清洗架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CIP清洗控制系统                                        │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                         中央调度层 (FC100_CIP_System)                   │   │
│  │  • 清洗队列管理                                                           │   │
│  │  • 介质资源协调                                                          │   │
│  │  • 报警综合处理                                                          │   │
│  │  • 配方参数下发                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                    │                    │                    │                    │
│        ┌───────────┴───────────┐ ┌─────┴─────┐ ┌─────────┴─────────┐           │
│        │                       │ │           │ │                   │           │
│  ┌─────▼─────┐  ┌─────▼─────┐  │▼           │▼                   │           │
│  │ Zone1     │  │ Zone2     │  │Zone3       │Zone4                │Zone5     │
│  │ FC101     │  │ FC102     │  │FC103       │FC104                │FC105     │
│  │ 水处理    │  │ 茶叶萃取  │  │调配        │UHT                  │灌装      │
│  └─────┬─────┘  └─────┬─────┘  │─┴─────────│─┴──────────────────│─┴─────    │
│        │              │        │           │                    │           │
│  ┌─────▼──────────────▼────────▼──────────▼────────────────────▼─────┐     │
│  │                    介质供给层                                             │     │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │     │
│  │  │ 碱液罐  │  │ 酸液罐  │  │ 热水罐  │  │ 纯水罐  │                 │     │
│  │  │ CP-101  │  │ CP-102  │  │ CP-103  │  │ CP-104  │                 │     │
│  │  │ 10m³   │  │ 10m³   │  │ 10m³   │  │ 5m³    │                 │     │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                 │     │
│  │       │            │            │            │                       │     │
│  │       └────────────┴────────────┴────────────┘                       │     │
│  │                           │                                             │     │
│  │                    ┌──────▼──────┐                                    │     │
│  │                    │ 介质选择阀   │                                    │     │
│  │                    │ M-V-01~05   │                                    │     │
│  │                    └──────┬──────┘                                    │     │
│  └───────────────────────────┼─────────────────────────────────────────────┘     │
│                              │                                                      │
└──────────────────────────────┼──────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │     执行层           │
                    │ 泵 + 阀门 + 传感器  │
                    └─────────────────────┘
```

### 1.2 控制系统分层

| 层级 | 名称 | 功能 | 程序块 |
|------|------|------|--------|
| **L3** | 中央调度层 | 队列管理、资源协调、配方下发 | FC100 |
| **L2** | 区域控制层 | 单区清洗控制、步骤执行 | FC101~105 |
| **L1** | 设备驱动层 | 泵/阀驱动、数据采集 | FB_Drive |
| **L0** | 现场设备层 | 变频器、阀门、传感器 | 硬件 |

---

## 2. 可用介质

### 2.1 介质定义

| 介质ID | 介质名称 | 类型 | 温度 | 浓度 | 用途 |
|--------|----------|------|------|------|------|
| 0 | 纯水 | 冲洗 | 常温/加热 | - | 预冲洗/中间冲洗/最终冲洗 |
| 1 | 碱液(NaOH) | 化学清洗 | 85℃ | 2% | 皂化油脂、溶解蛋白 |
| 2 | 酸液(HNO₃) | 化学清洗 | 60℃ | 1% | 去除无机垢 |
| 3 | 热水 | 化学清洗 | 85℃ | - | 热水浸泡 |
| 4 | 消毒液 | 化学清洗 | 常温 | 0.5% | 消毒处理 |
| ... | 其他 | ... | ... | ... | ... |

### 2.2 介质类型分类

| 类型 | 说明 | 约束 |
|------|------|------|
| **冲洗介质** | 纯水 | 可以连续使用 |
| **化学清洗介质** | 碱液、酸液、热水、消毒液等 | 切换时必须经过冲洗 |

---

## 3. 清洗序列约束

### 3.1 核心约束

```
清洗序列规则:
1. 冲洗介质(纯水)可以连续使用
2. 化学清洗介质之间必须至少插入1次冲洗
3. 清洗序列由用户在HMI上自由选择组合
4. 系统自动校验序列合法性，不合法则拒绝执行
```

### 3.2 合法序列示例

| 序列 | 合法性 | 说明 |
|------|--------|------|
| 纯水冲洗 | ✅ 合法 | 简单冲洗 |
| 碱洗 → 冲洗 | ✅ 合法 | 简单碱洗 |
| 热水洗 → 冲洗 → 碱洗 → 冲洗 | ✅ 合法 | 组合清洗 |
| 碱洗 → 酸洗 | ❌ 非法 | 化学介质直接切换 |
| 冲洗 → 冲洗 → 冲洗 | ✅ 合法 | 但没必要 |
| 碱洗 → 冲洗 → 冲洗 → 酸洗 → 冲洗 | ✅ 合法 | 中间多次冲洗 |

### 3.3 序列校验逻辑

```pascal
// 校验清洗序列合法性
FUNCTION FC_ValidateSequence : BOOL
    VAR_INPUT
        Sequence : ARRAY[1..10] OF INT;  // 步骤序列
        StepCount: INT;
    END_VAR
    VAR
        i : INT;
        CurrentIsChemical, PrevIsChemical : BOOL;
    END_VAR

    FC_ValidateSequence := TRUE;

    FOR i := 1 TO StepCount DO
        CurrentIsChemical := IsChemicalMedia(Sequence[i]);

        IF i > 1 THEN
            PrevIsChemical := IsChemicalMedia(Sequence[i-1]);

            // 化学介质直接切换到化学介质 = 非法
            IF CurrentIsChemical AND PrevIsChemical THEN
                FC_ValidateSequence := FALSE;
                TriggerAlarm(CP-SEQUENCE_ERROR);
                RETURN;
            END_IF;
        END_IF;
    END_FOR;
END_FUNCTION

// 判断是否为化学清洗介质
FUNCTION IsChemicalMedia : BOOL
    VAR_INPUT
        MediaID : INT;
    END_VAR

    CASE MediaID OF
        0: IsChemicalMedia := FALSE;  // 纯水=冲洗
        1,2,3,4: IsChemicalMedia := TRUE;  // 化学介质
        ELSE: IsChemicalMedia := FALSE;
    END_CASE;
END_FUNCTION
```

---

## 4. 每区清洗状态机

### 4.1 状态定义

| 状态 | 名称 | 说明 |
|------|------|------|
| 0 | **IDLE** | 待机 |
| 1 | **READY** | 准备就绪 |
| 2 | **STEP_EXEC** | 步骤执行中 |
| 3 | **STEP_TRANSITION** | 步骤切换中 |
| 4 | **COMPLETE** | 清洗完成 |
| 5 | **PAUSE** | 暂停 |
| 6 | **FAULT** | 故障 |

### 4.2 状态转换图

```
                         ┌──────────────────────────────────────────────────────┐
                         │                                                      │
                         ▼                                                      │
                   ┌─────────┐     Start      ┌─────────┐     Step Done       │
              ────▶│  IDLE  │──────────────▶│  READY  │──────────────────────┤
                    └─────────┘                └────┬────┘                      │
                         ▲                          │                          │
                         │                          │ Timer>0                 │
                         │ Stop                    ▼                          │
                         │                   ┌─────────────┐                    │
                         │                   │ STEP_EXEC   │◀────────────────────┘
                         │                   │ 步骤执行中   │     Step Done
                         │                   └──────┬──────┘
                         │                          │
                         │               ┌─────────┴─────────┐
                         │               │                   │
                         │               ▼                   ▼
                         │        ┌─────────────┐     ┌─────────────┐
                         │        │   冲洗完成   │     │  冲洗未完成  │
                         │        │ 准备切换    │     │ 继续冲洗    │
                         │        │ STEP_TRANS  │     │ STEP_EXEC  │
                         │        └──────┬──────┘     └─────────────┘
                         │               │
                         │        检查下一介质是否化学
                         │               │
                         │        ┌─────┴─────┐
                         │        │           │
                         │        ▼           ▼
                         │    ┌───────┐  ┌───────────┐
                         │    │需冲洗 │  │ 直接执行  │
                         │    │加冲洗 │  │ 下一步骤  │
                         │    │步骤   │  │           │
                         │    └───┬───┘  └─────┬─────┘
                         │        │              │
                         │        └──────┬───────┘
                         │               │
                         │               ▼
                         │      返回 STEP_EXEC
                         │
                         │    ┌───────────┐
                         └────│  PAUSE    │◀───────── Pause
                              └───────────┘
                                   │  │
                                   │  │ Resume
                                   ▼  ▼
                              返回原状态
```

### 4.3 状态转换条件

| 当前状态 | 事件 | 下一状态 | 动作 |
|----------|------|----------|------|
| IDLE | 启动命令 + 序列校验通过 | READY | 加载配方 |
| READY | 配方加载完成 | STEP_EXEC | 执行第1步 |
| STEP_EXEC | 当前步骤时间到 + 温度达标 | STEP_TRANSITION | 进入切换判断 |
| STEP_TRANSITION | 冲洗未完成 | STEP_EXEC | 添加冲洗步骤 |
| STEP_TRANSITION | 冲洗完成 + 还有下一步 | STEP_EXEC | 执行下一步 |
| STEP_TRANSITION | 冲洗完成 + 最后一步完成 | COMPLETE | 清洗完成 |
| ANY | 暂停命令 | PAUSE | 保存当前状态 |
| PAUSE | 恢复命令 | 原状态 | 恢复执行 |
| ANY | 急停/故障 | FAULT | 停止所有输出 |

---

## 5. 配方结构（步骤序列形式）

### 5.1 配方数据结构

```pascal
// 单个步骤
TYPE StepData
    STRUCT
        MediaID      : INT;     // 介质ID (0=纯水,1=碱液,2=酸液,3=热水,4=消毒液)
        MediaName    : STRING[20];  // 介质名称
        TargetTemp   : REAL;    // 目标温度(℃)
        TargetTime   : INT;     // 目标时间(秒)
        TargetFlow   : REAL;    // 目标流量(m³/h)
        PassConduct  : REAL;    // 合格电导率(μS/cm) - 仅最终冲洗有效
    END_STRUCT
END_TYPE

// 配方
TYPE RecipeData
    STRUCT
        RecipeID     : INT;     // 配方ID
        RecipeName   : STRING[20];  // 配方名称
        StepCount    : INT;     // 步骤数量(1-10)
        Steps        : ARRAY[1..10] OF StepData;  // 步骤序列
        TotalTime    : INT;     // 总时间(分钟)
        Description  : STRING[50];  // 配方描述
    END_STRUCT
END_TYPE
```

### 5.2 配方示例

```pascal
// 配方1: 快速冲洗
Recipe_QuickClean ::
    RecipeID := 1;
    RecipeName := 'QuickClean';
    StepCount := 1;
    Steps[1] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=25, TargetTime:=600, ...);
    TotalTime := 10;  // 10分钟
END_RECIPE

// 配方2: 标准碱洗
Recipe_StandardAlkali ::
    RecipeID := 2;
    RecipeName := 'StandardAlkali';
    StepCount := 3;
    Steps[1] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=85, TargetTime:=900, ...);  // 预热
    Steps[2] := (MediaID:=1, MediaName:='碱洗', TargetTemp:=85, TargetTime:=1500, ...);   // 碱洗
    Steps[3] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=25, TargetTime:=600, ...); // 冲洗
    TotalTime := 30;  // 30分钟
END_RECIPE

// 配方3: 全面清洗
Recipe_FullClean ::
    RecipeID := 3;
    RecipeName := 'FullClean';
    StepCount := 7;
    Steps[1] := (MediaID:=3, MediaName:='热水洗', TargetTemp:=85, TargetTime:=900, ...);   // 热水预浸
    Steps[2] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=85, TargetTime:=600, ...); // 冲洗
    Steps[3] := (MediaID:=1, MediaName:='碱洗', TargetTemp:=85, TargetTime:=1800, ...);   // 碱洗
    Steps[4] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=70, TargetTime:=600, ...);  // 中间冲洗
    Steps[5] := (MediaID:=2, MediaName:='酸洗', TargetTemp:=60, TargetTime:=1200, ...);   // 酸洗
    Steps[6] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=60, TargetTime:=600, ...);  // 中间冲洗
    Steps[7] := (MediaID:=0, MediaName:='纯水最终冲洗', TargetTemp:=25, TargetTime:=600, PassConduct:=50, ...); // 最终冲洗
    TotalTime := 75;  // 75分钟
END_RECIPE
```

### 5.3 步骤切换逻辑

```pascal
// 步骤切换处理
FUNCTION FC_StepTransition : VOID
    VAR_INPUT
        ZoneID : INT;
    END_VAR
    VAR
        CurrentStep, NextStep : INT;
        CurrentMedia, NextMedia : INT;
    END_VAR

    CurrentStep := Zone[ZoneID].CurrentStep;
    NextStep := CurrentStep + 1;

    // 检查是否还有下一步
    IF NextStep > Zone[ZoneID].Recipe.StepCount THEN
        // 最后一步完成
        Zone[ZoneID].State := COMPLETE;
        RETURN;
    END_IF;

    // 获取当前介质和下一介质
    CurrentMedia := Zone[ZoneID].Recipe.Steps[CurrentStep].MediaID;
    NextMedia := Zone[ZoneID].Recipe.Steeps[NextStep].MediaID;

    // 检查是否需要在化学介质之间插入冲洗
    IF IsChemicalMedia(CurrentMedia) AND IsChemicalMedia(NextMedia) THEN
        // 插入冲洗步骤
        Zone[ZoneID].InsertedStep := TRUE;  // 标记插入的冲洗步骤
        Zone[ZoneID].InsertedMedia := 0;    // 冲洗介质=纯水
        Zone[ZoneID].InsertedTemp := 60;    // 冲洗温度60℃
        Zone[ZoneID].InsertedTime := 300;   // 冲洗5分钟

        // 执行插入的冲洗步骤
        FC_ExecuteStep(ZoneID, InsertedStep);
    ELSE
        // 直接执行下一步
        Zone[ZoneID].CurrentStep := NextStep;
        FC_ExecuteStep(ZoneID, NextStep);
    END_IF;
END_FUNCTION
```

---

## 6. 每步执行控制

### 6.1 通用步骤执行

```pascal
// 执行单个步骤
FUNCTION FC_ExecuteStep : VOID
    VAR_INPUT
        ZoneID : INT;
        StepID : INT;  // 步骤索引(1-n 或 InsertedStep标记)
    END_VAR
    VAR
        MediaID : INT;
        TargetTemp, TargetTime, TargetFlow : REAL;
    END_VAR

    // 获取步骤参数
    IF StepID = InsertedStep THEN
        // 插入的冲洗步骤
        MediaID := Zone[ZoneID].InsertedMedia;
        TargetTemp := Zone[ZoneID].InsertedTemp;
        TargetTime := Zone[ZoneID].InsertedTime;
        TargetFlow := 3.0;  // 默认冲洗流量
    ELSE
        // 正常步骤
        MediaID := Zone[ZoneID].Recipe.Steps[StepID].MediaID;
        TargetTemp := Zone[ZoneID].Recipe.Steps[StepID].TargetTemp;
        TargetTime := Zone[ZoneID].Recipe.Steps[StepID].TargetTime;
        TargetFlow := Zone[ZoneID].Recipe.Steps[StepID].TargetFlow;
    END_IF;

    // 1. 选择介质
    FC_SelectMedia(ZoneID, MediaID);

    // 2. 启动泵
    Zone[ZoneID].PUMP.Start := TRUE;
    Zone[ZoneID].PUMP.Speed := TargetFlow / 5.0 * 100%;  // 流量转换为速度百分比

    // 3. 启动温度控制
    IF TargetTemp > 30 THEN
        Zone[ZoneID].TempSP := TargetTemp;
        Zone[ZoneID].TempControl := TRUE;
    ELSE
        Zone[ZoneID].TempControl := FALSE;
    END_IF;

    // 4. 启动步骤计时
    Zone[ZoneID].StepTimer := 0;
    Zone[ZoneID].TempReached := FALSE;
    Zone[ZoneID].TimeReached := FALSE;

END_FUNCTION

// 介质选择
FUNCTION FC_SelectMedia : VOID
    VAR_INPUT
        ZoneID : INT;
        MediaID : INT;
    END_VAR

    // 先关闭所有介质阀
    M-V-01 := FALSE;  // 碱液
    M-V-02 := FALSE;  // 酸液
    M-V-03 := FALSE;  // 热水
    M-V-04 := FALSE;  // 纯水
    M-V-05 := FALSE;  // 消毒液

    // 根据介质ID打开对应阀门
    CASE MediaID OF
        0: M-V-04 := TRUE;  // 纯水
        1: M-V-01 := TRUE;  // 碱液
        2: M-V-02 := TRUE;  // 酸液
        3: M-V-03 := TRUE;  // 热水
        4: M-V-05 := TRUE;  // 消毒液
    END_CASE;

    // 记录当前介质
    Zone[ZoneID].CurrentMedia := MediaID;
END_FUNCTION
```

### 6.2 步骤监控

> **温度控制说明**：
> - 当前实现使用**出口温度(TT_Outlet)**进行步骤完成判定
> - **返回温度(TT_Return)**用于安全监测（防止烫伤），为可选功能
> - 若启用返回温度控制，需在配方中设置 `bEnableReturnTempCheck = TRUE`

```pascal
// 步骤监控 (在FC101~105中循环调用)
FUNCTION FC_StepMonitor : VOID
    VAR_INPUT
        ZoneID : INT;
    END_VAR

    // 1. 温度监测
    IF Zone[ZoneID].TempControl THEN
        // 出口温度达标判定（当前实现）
        IF Zone[ZoneID].TT_Outlet >= Zone[ZoneID].TempSP - 5 THEN
            Zone[ZoneID].TempReached := TRUE;
        END_IF;

        // 返回温度监测（可选，用于安全联锁）
        IF Zone[ZoneID].TT_Return > 95 THEN
            TriggerAlarm(CP-TEMP_RETURN_HIGH);  // 返回温度过高报警
        END_IF;
    ELSE
        Zone[ZoneID].TempReached := TRUE;  // 不需加热则视为达标
    END_IF;

    // 2. 计时
    Zone[ZoneID].StepTimer := Zone[ZoneID].StepTimer + 1;

    IF Zone[ZoneID].StepTimer >= Zone[ZoneID].CurrentStepTime THEN
        Zone[ZoneID].TimeReached := TRUE;
    END_IF;

    // 3. 步骤完成判定
    IF Zone[ZoneID].TempReached AND Zone[ZoneID].TimeReached THEN
        // 检查是否为最终冲洗步骤
        IF Zone[ZoneID].CurrentStep = Zone[ZoneID].Recipe.StepCount THEN
            // 最终冲洗 - 检查电导率
            IF Zone[ZoneID].CD <= Zone[ZoneID].Recipe.Steps[Zone[ZoneID].CurrentStep].PassConduct THEN
                Zone[ZoneID].State := STEP_TRANSITION;
            ELSE
                // 电导率未达标，延长冲洗时间
                Zone[ZoneID].CurrentStepTime := Zone[ZoneID].CurrentStepTime + 300;  // +5分钟
                TriggerAlarm(CP-006);  // 电导率超标报警
            END_IF;
        ELSE
            Zone[ZoneID].State := STEP_TRANSITION;
        END_IF;
    END_IF;

    // 4. 安全联锁 - 无流量检测
    IF Zone[ZoneID].FS = FALSE THEN
        Zone[ZoneID].NoFlowTimer := Zone[ZoneID].NoFlowTimer + 1;
        IF Zone[ZoneID].NoFlowTimer >= 30 THEN
            Zone[ZoneID].State := PAUSE;
            TriggerAlarm(CP-011 + ZoneID);  // CP-012~016
        END_IF;
    ELSE
        Zone[ZoneID].NoFlowTimer := 0;
    END_IF;

END_FUNCTION
```

---

## 7. 介质资源管理

### 7.1 介质冲突解决策略

5区同时清洗时，共享介质资源（碱液/酸液/热水/纯水），采用以下策略：

| 策略 | 说明 | 适用场景 |
|------|------|----------|
| **先到先得** | 先请求介质的区域优先使用 | 默认策略 |
| **区域优先级** | 优先级高的区域优先（可配置） | 重要工段优先 |
| **时间片轮转** | 各区域按时间片交替使用 | 公平使用 |

**默认采用"先到先得"策略**，具体实现：

1. 区域请求介质时，检查介质是否空闲
2. 若空闲，标记为该区域使用，返回成功
3. 若已被占用，等待当前区域释放后重新竞争
4. 高优先级区域可通过配置获得优先权

> **可配置选项**（在HMI参数设置中）：
> - `MediaPriority[1..5]`: 各区域介质优先级（1-5，5最高）
> - `bEnablePriority`: 是否启用优先级策略（默认关闭）

### 7.2 介质冲突检测

```pascal
// 介质使用状态
VAR_GLOBAL
    MediaInUse : ARRAY[0..4] OF BOOL;      // 各介质是否被使用
    MediaUsingZone : ARRAY[0..4] OF INT;   // 使用该介质的区域
END_VAR

// 请求介质
FUNCTION FC_RequestMedia : BOOL
    VAR_INPUT
        ZoneID : INT;
        MediaID : INT;
    END_VAR

    IF MediaInUse[MediaID] THEN
        // 介质已被其他区使用
        RETURN FALSE;
    ELSE
        // 分配介质
        MediaInUse[MediaID] := TRUE;
        MediaUsingZone[MediaID] := ZoneID;
        RETURN TRUE;
    END_IF;
END_FUNCTION

// 释放介质
FUNCTION FC_ReleaseMedia : VOID
    VAR_INPUT
        ZoneID : INT;
        MediaID : INT;
    END_VAR

    IF MediaUsingZone[MediaID] = ZoneID THEN
        MediaInUse[MediaID] := FALSE;
    END_IF;
END_FUNCTION

// 释放区域所有介质
FUNCTION FC_ReleaseAllMedia : VOID
    VAR_INPUT
        ZoneID : INT;
    END_VAR
    VAR
        i : INT;
    END_VAR

    FOR i := 0 TO 4 DO
        FC_ReleaseMedia(ZoneID, i);
    END_FOR;
END_FUNCTION
```

---

## 8. 安全联锁逻辑

### 8.1 急停联锁

```pascal
// 急停处理
IF CP-DI-ESTOP = TRUE THEN
    // 停止所有泵
    FOR i := 1 TO 5 DO
        Zone[i].PUMP.Stop := TRUE;
        Zone[i].State := FAULT;
    END_FOR;

    // 关闭所有阀门
    M-V-01 := FALSE;
    M-V-02 := FALSE;
    M-V-03 := FALSE;
    M-V-04 := FALSE;
    M-V-05 := FALSE;
    M-V-06 := FALSE;

    // 关闭蒸汽
    CP-VALVE-STEAM := 0;

    // 触发急停报警
    TriggerAlarm(CP-EMERGENCY);

    bSystemReady := FALSE;
END_IF;
```

### 8.2 温度超限联锁

```pascal
// 温度超限处理
IF Zone[ZoneID].TT_Outlet > 95 THEN
    // 温度过高，关闭蒸汽
    CP-VALVE-STEAM := 0;
    TriggerAlarm(CP-TEMP_HIGH + ZoneID);
END_IF;

IF Zone[ZoneID].TT_Outlet < Zone[ZoneID].TempSP - 10 THEN
    Zone[ZoneID].LowTempTimer := Zone[ZoneID].LowTempTimer + 1;
    IF Zone[ZoneID].LowTempTimer >= 300 THEN  // 5分钟
        TriggerAlarm(CP-TEMP_LOW);
    END_IF;
ELSE
    Zone[ZoneID].LowTempTimer := 0;
END_IF;
```

---

## 9. 报警管理

### 9.1 报警列表

| 报警号 | 描述 | 等级 | 处理方式 |
|--------|------|------|----------|
| CP-001~004 | 罐区液位低 | L2 | 提示补充 |
| CP-005 | 温度不达标超时 | L1 | 报警，继续运行 |
| CP-006 | 电导率超标 | L1 | 继续冲洗或终止 |
| CP-008 | 管路压力异常 | L2 | 检查泵和管路 |
| CP-009 | 清洗泵过载 | L0 | 停止该区清洗 |
| CP-012~016 | 1-5区无流量 | L1 | 检查管路 |
| CP-017 | 急停触发 | L0 | 停止所有清洗 |
| **CP-018** | **清洗序列非法** | **L1** | **禁止启动，检查序列** |

---

## 10. 数据块设计

### 10.1 区域数据块

```pascal
// DB167 ~ DB171: Zone[1] ~ Zone[5]
TYPE ZoneData
    STRUCT
        // 状态
        State       : INT;          // 状态机状态
        CurrentStep : INT;          // 当前步骤索引(1-n)
        StepTimer   : INT;          // 当前步骤计时(秒)
        CurrentStepTime: INT;       // 当前步骤目标时间
        Result      : BOOL;         // 清洗结果

        // 介质
        CurrentMedia: INT;           // 当前介质ID
        TempControl : BOOL;         // 是否需要温度控制
        TempSP      : REAL;         // 温度设定值
        TempReached : BOOL;         // 温度是否达标

        // 插入步骤
        InsertedStep: BOOL;         // 是否为插入的冲洗步骤
        InsertedMedia: INT;         // 插入的冲洗介质
        InsertedTemp: REAL;         // 插入的冲洗温度
        InsertedTime: INT;          // 插入的冲洗时间

        // 传感器值
        TT_Outlet   : REAL;         // 出口温度
        TT_Return   : REAL;         // 回流温度
        CD          : REAL;         // 电导率
        PT          : REAL;         // 压力
        FT          : REAL;         // 流量
        FS          : BOOL;         // 流动开关

        // 报警计时
        NoFlowTimer : INT;
        LowTempTimer: INT;

        // 配方引用
        Recipe      : RecipeData;    // 当前配方

        // 时间戳
        StartTime   : TIME;
        EndTime     : TIME;
    END_STRUCT
END_TYPE
```

### 10.2 配方数据块

```pascal
// 配方存储 DB200 ~ DB210
// 可存储10个配方

DATA_BLOCK Recipe_QuickClean : RecipeData
    RecipeID := 1;
    RecipeName := 'QuickClean';
    StepCount := 1;
    Steps[1] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=25, TargetTime:=600, TargetFlow:=3.0);
END_DATA_BLOCK

DATA_BLOCK Recipe_StandardAlkali : RecipeData
    RecipeID := 2;
    RecipeName := 'StandardAlkali';
    StepCount := 3;
    Steps[1] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=85, TargetTime:=900, TargetFlow:=3.0);
    Steps[2] := (MediaID:=1, MediaName:='碱洗', TargetTemp:=85, TargetTime:=1500, TargetFlow:=5.0);
    Steps[3] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=25, TargetTime:=600, TargetFlow:=3.0, PassConduct:=50);
END_DATA_BLOCK

DATA_BLOCK Recipe_FullClean : RecipeData
    RecipeID := 3;
    RecipeName := 'FullClean';
    StepCount := 7;
    Steps[1] := (MediaID:=3, MediaName:='热水洗', TargetTemp:=85, TargetTime:=900, TargetFlow:=3.0);
    Steps[2] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=85, TargetTime:=600, TargetFlow:=3.0);
    Steps[3] := (MediaID:=1, MediaName:='碱洗', TargetTemp:=85, TargetTime:=1800, TargetFlow:=5.0);
    Steps[4] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=70, TargetTime:=600, TargetFlow:=3.0);
    Steps[5] := (MediaID:=2, MediaName:='酸洗', TargetTemp:=60, TargetTime:=1200, TargetFlow:=5.0);
    Steps[6] := (MediaID:=0, MediaName:='纯水冲洗', TargetTemp:=60, TargetTime:=600, TargetFlow:=3.0);
    Steps[7] := (MediaID:=0, MediaName:='纯水最终冲洗', TargetTemp:=25, TargetTime:=600, TargetFlow:=3.0, PassConduct:=50);
END_DATA_BLOCK
```

---

## 11. 程序调用结构

### 11.1 OB1主程序

```pascal
ORGANIZATION_BLOCK OB1
    // 急停检查
    IF CP-DI-ESTOP = TRUE THEN
        FC_EmergencyStop();
        RETURN;
    END_IF;

    // 执行CIP系统主程序
    FC100_CIP_System();
END_ORGANIZATION_BLOCK
```

### 11.2 FC100_CIP_System

```pascal
FUNCTION FC100_CIP_System : VOID

    // 1. 更新传感器数据
    FOR i := 1 TO 5 DO
        Zone[i].TT_Outlet := Zx-TT01;
        Zone[i].TT_Return := Zx-TT02;
        Zone[i].CD := Zx-CD01;
        Zone[i].PT := Zx-PT01;
        Zone[i].FT := Zx-FT01;
        Zone[i].FS := Zx-FS01;
    END_FOR;

    // 2. 处理清洗队列
    FC_ProcessQueue();

    // 3. 执行各区清洗控制
    FOR i := 1 TO 5 DO
        FC_ZoneControl(i);
    END_FOR;

    // 4. 处理报警
    FC_AlarmHandler();

END_FUNCTION
```

### 11.3 FC_ZoneControl

```pascal
FUNCTION FC_ZoneControl : VOID
    VAR_INPUT
        ZoneID : INT;
    END_VAR

    CASE Zone[ZoneID].State OF
        IDLE:
            // 待机，无动作

        READY:
            // 加载配方，执行第1步
            Zone[ZoneID].CurrentStep := 1;
            FC_ExecuteStep(ZoneID, 1);
            Zone[ZoneID].State := STEP_EXEC;

        STEP_EXEC:
            // 执行当前步骤
            FC_StepMonitor(ZoneID);

        STEP_TRANSITION:
            // 步骤切换判断
            FC_StepTransition(ZoneID);

        COMPLETE:
            // 清洗完成
            Zone[ZoneID].EndTime := TIME();
            Zone[ZoneID].State := IDLE;
            FC_LogHistory(ZoneID);
            FC_ReleaseAllMedia(ZoneID);

        PAUSE:
            // 暂停，等待恢复

        FAULT:
            // 故障，需人工复位
    END_CASE;

END_FUNCTION
```

---

## 12. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-05-12 | 初始版本，固定5步清洗流程 |
| **v2.0** | **2026-05-12** | **支持自由组合清洗序列，化学介质切换自动插入冲洗步骤** |
| **v2.1** | **2026-05-13** | **补充介质冲突解决策略(先到先得+优先级可选)、明确返回温度为可选功能** |

---

**文档状态**: ✅ 已完善
**待确认**: 清洗剂配制功能移至Phase 2实现
