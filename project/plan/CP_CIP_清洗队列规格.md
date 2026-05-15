# CIP清洗系统 - 清洗队列功能规格

> 文档版本: v1.0
> 创建日期: 2026-05-13
> 工段: CP (CIP Cleaning In Place)
> 用途: 清洗任务排队、优先级管理、队列调度

---

## 1. 概述

### 1.1 队列系统架构

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           清洗队列系统                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          队列管理层                                       │   │
│  │                                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │                    FC400_QueueManager                             │    │   │
│  │  │  • 队列添加/移除/排序                                              │    │   │
│  │  │  • 优先级调度                                                      │    │   │
│  │  │  • 串行/并行模式                                                   │    │   │
│  │  │  • 预计时间计算                                                    │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                    │                                           │
│                                    ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                          调度执行层                                       │   │
│  │                                                                          │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐           │   │
│  │  │ 1区    │  │ 2区    │  │ 3区    │  │ 4区    │  │ 5区    │           │   │
│  │  │ 清洗   │  │ 待机   │  │ 待机   │  │ 待机   │  │ 待机   │           │   │
│  │  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘           │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 清洗模式

| 模式 | 说明 | 同时清洗区域数 | 适用场景 |
|------|------|---------------|----------|
| **串行清洗** | 逐区依次清洗 | 1 | 单一清洗介质，资源有限 |
| **并行清洗** | 多区同时清洗 | ≤5 | 多介质，多区域同时清洗 |

---

## 2. 队列管理

### 2.1 队列数据结构

```pascal
TYPE "UDT_QueueItem"
    STRUCT
        QueueID      : Int;              // 队列序号
        ZoneID       : Int;              // 区域ID (1-5)
        RecipeID     : Int;              // 配方ID
        Priority     : Int;              // 优先级 (1-9, 1最高)
        RequestTime  : LDT;              // 请求时间
        ScheduledTime: LDT;              // 计划开始时间
        EstimatedDuration: Int;          // 预计时长(分钟)
        Status       : Int;             // 状态 (0=等待, 1=执行, 2=完成, 3=暂停)
        BatchID      : String[20];       // 批次号
    END_STRUCT
END_TYPE

// 全局队列
"Global".CleaningQueue : Array[1..20] of "UDT_QueueItem";
"Global".QueueCount   : Int;            // 队列长度
"Global".QueueMax     : Int := 20;      // 最大队列长度
```

### 2.2 队列状态

| 状态值 | 名称 | 说明 |
|--------|------|------|
| 0 | WAITING | 等待中 |
| 1 | EXECUTING | 执行中 |
| 2 | COMPLETED | 已完成 |
| 3 | PAUSED | 暂停 |
| 4 | CANCELLED | 已取消 |

### 2.3 优先级定义

| 优先级 | 名称 | 说明 | 典型用途 |
|--------|------|------|----------|
| 1 | 紧急 | 最高优先级 | 食品安全事故、污染应急 |
| 2 | 高 | 高优先级 | 重要产品切换前清洗 |
| 3 | 标准 | 默认优先级 | 常规清洗任务 |
| 4-9 | 低 | 低优先级 | 预防性清洗、计划清洗 |

---

## 3. 队列操作

### 3.1 添加到队列

```pascal
FUNCTION "FC_AddToQueue" : Int
VAR_INPUT
    ZoneID   : Int;
    RecipeID : Int;
    Priority : Int;
END_VAR
VAR
    i : Int;
    EmptySlot : Int;
BEGIN
    // 检查队列是否已满
    IF "Global".QueueCount >= "Global".QueueMax THEN
        "FC_AddToQueue" := -1;  // 队列已满
        RETURN;
    END_IF;

    // 检查区域是否已在队列中
    FOR i := 1 TO "Global".QueueMax DO
        IF "Global".CleaningQueue[i].ZoneID = ZoneID
        AND "Global".CleaningQueue[i].Status = 0 THEN
            "FC_AddToQueue" := -2;  // 区域已在队列中
            RETURN;
        END_IF;
    END_FOR;

    // 查找空闲槽位
    EmptySlot := 0;
    FOR i := 1 TO "Global".QueueMax DO
        IF "Global".CleaningQueue[i].Status = 4  // CANCELLED 或空闲
        OR "Global".CleaningQueue[i].Status = 2 THEN  // COMPLETED
            EmptySlot := i;
            EXIT;
        END_IF;
    END_FOR;

    IF EmptySlot = 0 THEN
        EmptySlot := "Global".QueueCount + 1;
    END_IF;

    // 填充队列项
    "Global".CleaningQueue[EmptySlot].QueueID := EmptySlot;
    "Global".CleaningQueue[EmptySlot].ZoneID := ZoneID;
    "Global".CleaningQueue[EmptySlot].RecipeID := RecipeID;
    "Global".CleaningQueue[EmptySlot].Priority := Priority;
    "Global".CleaningQueue[EmptySlot].RequestTime := "Global".System.SystemTime;
    "Global".CleaningQueue[EmptySlot].Status := 0;  // WAITING
    "Global".CleaningQueue[EmptySlot].EstimatedDuration := "FC_GetRecipeDuration"(RecipeID);

    // 生成批次号
    "Global".CleaningQueue[EmptySlot].BatchID :=
        "FC_GenerateBatchID"(ZoneID);

    // 增加队列计数
    "Global".QueueCount := "Global".QueueCount + 1;

    // 按优先级排序
    "FC_SortQueue";

    "FC_AddToQueue" := EmptySlot;  // 成功

END_FUNCTION
```

### 3.2 从队列移除

```pascal
FUNCTION "FC_RemoveFromQueue" : Bool
VAR_INPUT
    QueueID : Int;
END_VAR
BEGIN
    IF QueueID < 1 OR QueueID > "Global".QueueMax THEN
        "FC_RemoveFromQueue" := FALSE;
        RETURN;
    END_IF;

    IF "Global".CleaningQueue[QueueID].Status = 1 THEN
        // 正在执行，不允许移除
        "FC_RemoveFromQueue" := FALSE;
        RETURN;
    END_IF;

    // 标记为取消
    "Global".CleaningQueue[QueueID].Status := 4;  // CANCELLED

    // 减少队列计数
    "Global".QueueCount := "Global".QueueCount - 1;

    // 重新排序
    "FC_SortQueue";

    "FC_RemoveFromQueue" := TRUE;

END_FUNCTION
```

### 3.3 队列排序 (按优先级)

```pascal
FUNCTION "FC_SortQueue" : Void
VAR
    i, j : Int;
    Temp : "UDT_QueueItem";
END_VAR

    // 冒泡排序 - 按优先级升序 (1=最高)
    FOR i := 1 TO "Global".QueueMax - 1 DO
        FOR j := 1 TO "Global".QueueMax - i DO
            IF "Global".CleaningQueue[j].Priority >
               "Global".CleaningQueue[j+1].Priority
            AND "Global".CleaningQueue[j].Status = 0
            AND "Global".CleaningQueue[j+1].Status = 0 THEN
                // 交换
                Temp := "Global".CleaningQueue[j];
                "Global".CleaningQueue[j] := "Global".CleaningQueue[j+1];
                "Global".CleaningQueue[j+1] := Temp;
            END_IF;
        END_FOR;
    END_FOR;

END_FUNCTION
```

---

## 4. 调度逻辑

### 4.1 主调度函数

```pascal
FUNCTION "FC100_CIP_System" : Void
VAR
    i : Int;
    ExecutingCount : Int;
    NextQueueID : Int;
END_VAR

    // ========================================================================
    // 1. 统计当前执行中的任务数
    // ========================================================================
    ExecutingCount := 0;
    FOR i := 1 TO "Global".QueueMax DO
        IF "Global".CleaningQueue[i].Status = 1 THEN
            ExecutingCount := ExecutingCount + 1;
        END_IF;
    END_FOR;

    // ========================================================================
    // 2. 串行模式: 最多1个执行中
    //    并行模式: 最多5个执行中 (全部区域)
    // ========================================================================
    IF NOT "Global".System.ParallelMode THEN
        // 串行模式: 最多1个执行中
        IF ExecutingCount < 1 THEN
            // 查找下一个待执行任务
            NextQueueID := "FC_FindNextTask";

            IF NextQueueID > 0 THEN
                // 启动清洗任务
                "FC_StartCleaningTask"(NextQueueID);
            END_IF;
        END_IF;
    ELSE
        // 并行模式: 最多5个执行中
        IF ExecutingCount < 5 THEN
            NextQueueID := "FC_FindNextTask";

            WHILE NextQueueID > 0 AND ExecutingCount < 5 DO
                "FC_StartCleaningTask"(NextQueueID);
                ExecutingCount := ExecutingCount + 1;
                NextQueueID := "FC_FindNextTask";
            END_WHILE;
        END_IF;
    END_IF;

    // ========================================================================
    // 3. 更新系统队列信息
    // ========================================================================
    "Global".System.QueueCount := "Global".QueueCount;

END_FUNCTION
```

### 4.2 查找下一个任务

```pascal
FUNCTION "FC_FindNextTask" : Int
VAR
    i : Int;
BEGIN
    // 查找优先级最高的等待任务
    FOR i := 1 TO "Global".QueueMax DO
        IF "Global".CleaningQueue[i].Status = 0 THEN
            "FC_FindNextTask" := i;
            RETURN;
        END_IF;
    END_FOR;

    "FC_FindNextTask" := 0;  // 没有等待任务

END_FUNCTION
```

### 4.3 启动清洗任务

```pascal
FUNCTION "FC_StartCleaningTask" : Void
VAR_INPUT
    QueueID : Int;
END_VAR
VAR
    ZoneID : Int;
BEGIN
    ZoneID := "Global".CleaningQueue[QueueID].ZoneID;

    // 更新队列状态
    "Global".CleaningQueue[QueueID].Status := 1;  // EXECUTING
    "Global".CleaningQueue[QueueID].ScheduledTime := "Global".System.SystemTime;

    // 启动对应区域的清洗
    "DB_Zone"[ZoneID].Command := 1;  // START
    "DB_Zone"[ZoneID].RecipeID := "Global".CleaningQueue[QueueID].RecipeID;
    "DB_Zone"[ZoneID].BatchID := "Global".CleaningQueue[QueueID].BatchID;

    // 记录启动日志
    "FC_LogHistory"(ZoneID, 1, '清洗任务启动');

END_FUNCTION
```

---

## 5. 预计时间计算

### 5.1 计算逻辑

```pascal
FUNCTION "FC_CalculateEstimatedTime" : Int
VAR
    i : Int;
    TotalTime : Int;
    RecipeDuration : Int;
BEGIN
    TotalTime := 0;

    FOR i := 1 TO "Global".QueueMax DO
        IF "Global".CleaningQueue[i].Status = 0 THEN
            // 获取配方时长
            RecipeDuration := "FC_GetRecipeDuration"(
                "Global".CleaningQueue[i].RecipeID
            );

            TotalTime := TotalTime + RecipeDuration;
        END_IF;
    END_FOR;

    "FC_CalculateEstimatedTime" := TotalTime;

END_FUNCTION
```

### 5.2 显示格式

```
串行模式: 45 + 95 + 85 + 85 + 85 = 395 分钟 (约6.5小时)
          ↑      ↑     ↑      ↑      ↑
        区域1   区域2  区域3  区域4  区域5

当前时间: 14:32:15
预计结束: 20:57:15
```

---

## 6. HMI显示

### 6.1 清洗队列画面

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  清洗队列                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌────────────────────────────────┐  ┌────────────────────────────────┐        │
│  │        待清洗队列              │  │        清洗中                   │        │
│  │  ┌──────────────────────────┐ │  │  ┌──────────────────────────┐ │        │
│  │  │ [1] 2区-茶叶萃取    [▼] │ │  │  │ [3] 1区-水处理          │ │        │
│  │  │     配方: EXCIP-01      │ │  │  │     配方: WTCIP-01        │ │        │
│  │  │     优先级: [3]        │ │  │  │──────────────────────────│ │        │
│  │  ├──────────────────────────┤ │  │  │ 步骤: 2/5 碱洗           │ │        │
│  │  │ [2] 3区-调配系统    [▼] │ │  │  │ 时间: 15:30/25:00        │ │        │
│  │  │     配方: BLCIP-01      │ │  │  │温度: 82℃✓ 电导: 320μS │ │        │
│  │  │     优先级: [2]        │ │  │  │                          │ │        │
│  │  ├──────────────────────────┤ │  │  │ [提升优先级] [延后]     │ │        │
│  │  │ [3] 4区-UHT杀菌    [▼] │ │  │  └──────────────────────────┘ │        │
│  │  │     配方: UHCIP-01      │ │  │                                │        │
│  │  │     优先级: [1]        │ │  │                                │        │
│  │  └──────────────────────────┘ │  │                                │        │
│  │                                 │  │                                │        │
│  │ [添加] [编辑] [移除] [清空]   │  │                                │        │
│  └────────────────────────────────┘  └────────────────────────────────┘        │
│                                                                                 │
│  清洗模式:  ●串行清洗    ○并行清洗(需二次确认)                                 │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  预计时间计算:                                                          │   │
│  │                                                                         │   │
│  │  串行模式: 45 + 95 + 85 + 85 + 85 = 395 分钟 (约6.5小时)              │   │
│  │                                                                         │   │
│  │  当前时间: 14:32:15     预计开始: 清洗中                               │   │
│  │                     预计结束: 20:57:15                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [返回主画面]                                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 添加到队列弹窗

```
┌───────────────────────────────────────────────────────────────┐
│  添加清洗任务                                              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  目标区域: [1区-水处理        ▼]                           │
│                                                               │
│  清洗配方: [WTCIP-01 水处理标准▼]                           │
│                                                               │
│  配方预览:                                                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ 步骤1: 纯水冲洗    70℃   15min                         │ │
│  │ 步骤2: 碱洗        85℃   25min                         │ │
│  │ 步骤3: 纯水冲洗    70℃   10min                         │ │
│  │ 步骤4: 酸洗        60℃   20min                         │ │
│  │ 步骤5: 纯水冲洗    70℃   15min (电导率≤50μS)           │ │
│  │ ────────────────────────────────────────                │ │
│  │ 总计: 85分钟                                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                               │
│  优先级:  ○紧急(1)  ○高(2)  ●标准(3)  ○低(4-9)             │
│                                                               │
│           [取消]                        [添加到队列]          │
└───────────────────────────────────────────────────────────────┘
```

---

## 7. 历史记录

### 7.1 队列历史

| 字段 | 类型 | 说明 |
|------|------|------|
| BatchID | STRING | 批次号 |
| ZoneID | INT | 区域ID |
| RecipeID | INT | 配方ID |
| RequestTime | LDT | 请求时间 |
| StartTime | LDT | 开始时间 |
| EndTime | LDT | 结束时间 |
| Duration | INT | 实际时长(分钟) |
| Priority | INT | 优先级 |
| Result | BOOL | 结果 (TRUE=合格) |

### 7.2 统计报表

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  清洗统计                                    日期: 2026-05-13                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  今日清洗次数: 12          本周清洗次数: 56        本月清洗次数: 234           │
│                                                                                 │
│  清洗趋势:                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │    15 ┤                                                        ╭──      │  │
│  │       │                                                  ╭───╯         │  │
│  │    10 ┤                                            ╭────╯               │  │
│  │       │                                      ╭───╯                     │  │
│  │     5 ┤                                ╭────╯                           │  │
│  │       │                          ╭───╯                                 │  │
│  │     0 ┤__________________________╯___________________________________    │  │
│  │         5/7   5/8   5/9   5/10  5/11  5/12  5/13                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
│  各区域清洗次数:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │  1区: ████████████████████ 45次                                           │  │
│  │  2区: ██████████████████ 38次                                            │  │
│  │  3区: ████████████████ 32次                                               │  │
│  │  4区: ████████████████████ 42次                                           │  │
│  │  5区: █████████████████ 35次                                             │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

**文档状态**: ✅ 已完成
**版本**: v1.0
**依赖**: 子任务10 (Profinet通讯) ✅
