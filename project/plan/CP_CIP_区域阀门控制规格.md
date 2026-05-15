# CIP清洗系统 - 区域阀门控制规格

> 文档版本: v1.0
> 创建日期: 2026-05-13
> 工段: CP (CIP Cleaning In Place)
> 用途: 各区阀门手动/自动控制

---

## 1. 概述

### 1.1 阀门配置

CIP系统共配置25个阀门，分布在5个区域：

| 区域 | 阀门编号 | 阀门类型 | 功能 |
|------|----------|----------|------|
| **1区** | V-101 ~ V-105 | 气动阀 | 进水/排水/介质切换 |
| **2区** | V-201 ~ V-205 | 气动阀 | 进水/排水/介质切换 |
| **3区** | V-301 ~ V-305 | 气动阀 | 进水/排水/介质切换 |
| **4区** | V-401 ~ V-405 | 气动阀 | 进水/排水/介质切换 |
| **5区** | V-501 ~ V-505 | 气动阀 | 进水/排水/介质切换 |
| **公用** | V-601 ~ V-603 | 气动阀 | 蒸汽/排放/循环 |

### 1.2 阀门类型

| 类型 | 代码 | 说明 |
|------|------|------|
| 气动阀 | ON/OFF | 两位式开关 |
| 调节阀 | Modulating | 0-100%连续调节 |
| 电动阀 | Motorized | 带反馈的电动阀 |

---

## 2. 阀门功能定义

### 2.1 每区阀门功能

| 阀门 | 功能 | 介质 |
|------|------|------|
| V-XX1 | 进水阀 | 纯水/碱/酸/热水 |
| V-XX2 | 排水阀 | 排放至地沟 |
| V-XX3 | 介质阀A | 碱液/酸液/消毒液 |
| V-XX4 | 介质阀B | 纯水/循环 |
| V-XX5 | 应急排放阀 | 紧急排放 |

### 2.2 公用阀门

| 阀门 | 功能 | 说明 |
|------|------|------|
| V-601 | 蒸汽总阀 | 加热介质 |
| V-602 | 排放总阀 | 排放收集 |
| V-603 | 循环总阀 | 清洗液循环 |

---

## 3. 阀门控制模式

### 3.1 控制模式

| 模式 | 说明 | 权限 |
|------|------|------|
| **自动** | 根据清洗程序自动控制 | 操作员及以上 |
| **手动** | 操作员手动开关 | 技术员及以上 |
| **就地** | 现场手动操作 | 现场开关 |

### 3.2 模式切换逻辑

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         控制模式切换流程                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  自动模式 ──► (技术员授权) ──► 手动模式                                        │
│     ▲                                    │                                      │
│     │                                    ▼                                      │
│     │                              手动操作阀门                                  │
│     │                                    │                                      │
│     │                                    ▼                                      │
│     │                       (技术员取消授权 或 60分钟超时)                       │
│     │                                    ▼                                      │
│     └────────────────────────────────────────────────────────────────────────── │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. PLC控制逻辑

### 4.1 阀门状态数据结构

```pascal
TYPE "UDT_ValveData"
    STRUCT
        ValveID      : Int;              // 阀门编号
        Command      : Bool;             // 命令 (TRUE=开)
        Feedback     : Bool;             // 反馈 (TRUE=开)
        State        : "Enum_ValveState";// 状态
        Fault        : Bool;             // 故障
        FaultCode    : Int;              // 故障代码
        LastCmdTime  : LDT;              // 最后命令时间
        AutoMode     : Bool;             // 自动模式
    END_STRUCT
END_TYPE

TYPE "Enum_ValveState"
    CLOSED     := 0;   // 关闭
    OPENING    := 1;   // 正在开启
    OPEN       := 2;   // 开启
    CLOSING    := 3;   // 正在关闭
    FAULT      := 4;   // 故障
    NO_FEEDBACK := 5;   // 无反馈
END_TYPE
```

### 4.2 阀门控制函数

```pascal
FUNCTION "FC_ValveControl" : Void
VAR_INPUT
    ZoneID  : Int;
    ValveNo : Int;
    Cmd     : Bool;  // TRUE=开, FALSE=关
END_VAR
VAR
    ValveData : "UDT_ValveData";
    ValveAddr : Int;
BEGIN
    // 计算阀门地址
    ValveAddr := (ZoneID - 1) * 5 + ValveNo;

    // 获取阀门数据
    ValveData := "Global".Valves[ValveAddr];

    // 检查控制权限
    IF NOT "FC_CheckManualControlPermission"(ZoneID) THEN
        RETURN;  // 无权限
    END_IF;

    // 检查阀门是否在自动模式
    IF ValveData.AutoMode THEN
        RETURN;  // 自动模式下不允许手动
    END_IF;

    // 发送命令
    "Global".Output.ValveCmd[ValveAddr] := Cmd;
    ValveData.Command := Cmd;
    ValveData.LastCmdTime := "Global".System.SystemTime;

    // 更新阀门状态为开启中/关闭中
    IF Cmd THEN
        ValveData.State := "Enum_ValveState".OPENING;
    ELSE
        ValveData.State := "Enum_ValveState".CLOSING;
    END_IF;

END_FUNCTION
```

### 4.3 阀门反馈检测

```pascal
FUNCTION "FC_CheckValveFeedback" : Void
VAR
    i : Int;
    ValveData : "UDT_ValveData";
    ExpectedState : Bool;
    TimeSinceCmd : LDT;
END_VAR

    FOR i := 1 TO 25 DO
        ValveData := "Global".Valves[i];

        // 如果阀门正在切换状态
        IF ValveData.State = "Enum_ValveState".OPENING
        OR ValveData.State = "Enum_ValveState".CLOSING THEN

            ExpectedState := (ValveData.State = "Enum_ValveState".OPENING);

            // 检查反馈是否与命令一致
            IF ValveData.Feedback = ExpectedState THEN
                // 阀门到位
                IF ExpectedState THEN
                    ValveData.State := "Enum_ValveState".OPEN;
                ELSE
                    ValveData.State := "Enum_ValveState".CLOSED;
                END_IF;
            ELSE
                // 检查超时 (5秒)
                TimeSinceCmd := "Global".System.SystemTime - ValveData.LastCmdTime;
                IF TimeSinceCmd > 5000 THEN
                    // 阀门无反馈故障
                    ValveData.State := "Enum_ValveState".NO_FEEDBACK;
                    ValveData.Fault := TRUE;
                    ValveData.FaultCode := 11;  // CP-011
                    "FC_TriggerAlarm"(11, "Enum_AlarmLevel".L1_WARNING, 0);
                END_IF;
            END_IF;
        END_IF;

        // 检查阀门故障
        IF ValveData.Feedback <> ValveData.Command
        AND ValveData.State <> "Enum_ValveState".OPENING
        AND ValveData.State <> "Enum_ValveState".CLOSING THEN
            ValveData.Fault := TRUE;
            ValveData.State := "Enum_ValveState".FAULT;
        END_IF;

    END_FOR;

END_FUNCTION
```

---

## 5. 阀门联锁

### 5.1 安全联锁

| 条件 | 动作 | 说明 |
|------|------|------|
| 急停触发 | 关闭所有阀门 | 安全优先 |
| 区域清洗中 | 禁止操作该区阀门 | 防误操作 |
| 泵运行中 | 禁止关闭排水阀 | 防止泵空转 |

### 5.2 工艺联锁

| 条件 | 允许组合 | 禁止组合 |
|------|----------|----------|
| 进水时 | V-XX1 + V-XX4 | V-XX1 + V-XX2 |
| 排放时 | V-XX2 + V-XX5 | V-XX1 + V-XX2 |
| 循环时 | V-XX4 + V-603 | V-XX1 + V-XX2 |

### 5.3 联锁逻辑

```pascal
FUNCTION "FC_CheckValveInterlock" : Bool
VAR_INPUT
    ZoneID  : Int;
    ValveNo : Int;
    Cmd     : Bool;
END_VAR
VAR
    Result : Bool;
    OtherValveState : Bool;
BEGIN
    Result := TRUE;

    // 检查急停
    IF "Global".System.EStop THEN
        Result := FALSE;
    END_IF;

    // 检查区域是否在清洗中
    IF "DB_Zone"[ZoneID].State <> "Enum_CleanState".IDLE
    AND "DB_Zone"[ZoneID].State <> "Enum_CleanState".READY THEN
        // 清洗中不允许手动操作
        Result := FALSE;
    END_IF;

    // 检查泵状态
    IF "DB_Zone"[ZoneID].PumpState = "Enum_PumpState".PUMP_RUNNING
    AND ValveNo = 2  // 尝试关闭排水阀
    AND Cmd = FALSE THEN
        // 泵运行时禁止关闭排水阀
        Result := FALSE;
    END_IF;

    // 检查工艺组合
    IF ValveNo = 1 AND Cmd = TRUE THEN  // 开水进水阀
        // 检查是否同时开了排水阀
        OtherValveState := "Global".Valves[(ZoneID-1)*5 + 2].Command;
        IF OtherValveState THEN
            Result := FALSE;  // 不允许同时开水和排水
        END_IF;
    END_IF;

    "FC_CheckValveInterlock" := Result;

END_FUNCTION
```

---

## 6. HMI显示

### 6.1 阀门控制画面

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  阀门控制                                                    [子画面]        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  区域选择: [1区▼] [2区▼] [3区▼] [4区▼] [5区▼] [公用▼]    [全开] [全关]     │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  1区阀门控制                                                            │   │
│  │                                                                         │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐     │   │
│  │  │ V-101   │  │ V-102   │  │ V-103   │  │ V-104   │  │ V-105   │     │   │
│  │  │ 进水阀  │  │ 排水阀  │  │ 介质阀A │  │ 介质阀B │  │ 应急排放│     │   │
│  │  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤  ├─────────┤     │   │
│  │  │    ○    │  │    ●    │  │    ○    │  │    ○    │  │    ○    │     │   │
│  │  │  关/开  │  │  关/开  │  │  关/开  │  │  关/开  │  │  关/开  │     │   │
│  │  │  ●自动  │  │  ○手动  │  │  ●自动  │  │  ●自动  │  │  ○手动  │     │   │
│  │  │ [开] [关]│  │ [开] [关]│  │ [开] [关]│  │ [开] [关]│  │ [开] [关]│     │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘     │   │
│  │                                                                         │   │
│  │  状态: ●运行中  反馈: ●到位  故障: ○无                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [返回主画面]                                                                │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 阀门状态图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         1区阀门状态示意图                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│                          ┌─────┐                                                 │
│                    ┌────►│ V101│────► (纯水)                                    │
│                    │     └─────┘                                                 │
│                    │                                                             │
│     ┌─────────┐    │     ┌─────┐     ┌─────────┐     ┌─────────┐               │
│     │  换热器  │◄───┴────│ V104│◄────│ 清洗区  │────►│ V102   │────► (排放)   │
│     └─────────┘          └─────┘     └─────────┘     └─────────┘               │
│          ▲                                                                  │
│          │     ┌─────┐                                                 │
│          └─────│ V103│────► (碱/酸)                                          │
│                └─────┘                                                 │
│                                                                                 │
│  图例: ───► 流向  ● 阀门开  ○ 阀门关                                         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 6.3 阀门操作日志

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  阀门操作日志                                            [子画面]              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │ 时间              │ 阀门  │ 区域 │ 操作   │ 用户   │ 结果              │   │
│  ├───────────────────┼───────┼──────┼────────┼────────┼───────────────────┤   │
│  │ 2026-05-13 14:32 │ V-101 │ 1区  │ 开     │ 张三   │ 成功              │   │
│  │ 2026-05-13 14:30 │ V-102 │ 1区  │ 关     │ 张三   │ 成功              │   │
│  │ 2026-05-13 14:25 │ V-201 │ 2区  │ 开     │ 李四   │ 成功              │   │
│  │ 2026-05-13 14:20 │ V-103 │ 1区  │ 开     │ 张三   │ 失败-无反馈       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  [导出] [筛选] [时间范围: 今天▼]                                               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. 权限管理

| 操作 | 操作员 | 技术员 | 工程师 | 管理员 |
|------|--------|--------|--------|--------|
| 查看阀门状态 | ✅ | ✅ | ✅ | ✅ |
| 手动开关阀门 | ❌ | ✅ | ✅ | ✅ |
| 批量开关 | ❌ | ❌ | ✅ | ✅ |
| 模式切换 | ❌ | ✅ | ✅ | ✅ |
| 故障复位 | ❌ | ✅ | ✅ | ✅ |

---

**文档状态**: ✅ 已完成
**版本**: v1.0
**依赖**: 子任务10 (Profinet通讯) ✅
