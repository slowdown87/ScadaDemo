# CIP SCADA PLC完整教程

## 目录

1. [PLC是什么？](#1-plc是什么)
2. [SCL语言入门](#2-scl语言入门)
3. [项目结构总览](#3-项目结构总览)
4. [数据类型详解](#4-数据类型详解)
5. [组织块说明](#5-组织块说明)
6. [核心控制逻辑](#6-核心控制逻辑)
7. [工具函数库](#7-工具函数库)
8. [TIA Portal导入](#8-tia-portal导入)
9. [项目实战练习](#9-项目实战练习)
10. [调试方法](#10-调试方法)
11. [常见问题](#11-常见问题)
12. [术语表](#12-术语表)
13. [学习路径建议](#13-学习路径建议)

---

## 1. PLC是什么？

### 1.1 生活中的比喻

想象你家里的空调遥控器：

```
你（操作员）→ 遥控器（PLC）→ 空调（设备）
```

- **你** → 发出指令："制冷26度"
- **遥控器** → 接收指令，判断温度，决定开关
- **空调** → 真正执行制冷/制热

**PLC就是工业界的"遥控器"，负责接收指令、控制设备、监控系统状态。**

### 1.2 PLC在CIP系统中的角色

```
┌─────────────────────────────────────────────────────────┐
│                     Web前端/SCADA界面                     │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/WebSocket
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Python后端 (FastAPI)                    │
│                   - 数据转发                              │
│                   - 协议转换                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ S7协议 (通过Snap7库)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      西门子 S7-1500 PLC                   │
│                                                         │
│   ┌─────────────────────────────────────────────────┐  │
│   │                  CIP清洗控制程序                   │  │
│   │  - 读取传感器数据 (温度/流量/压力/液位)             │  │
│   │  - 控制阀门和泵                                    │  │
│   │  - 执行清洗步骤                                    │  │
│   │  - 报警检测与处理                                  │  │
│   └─────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         ▼                ▼                ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   阀门      │   │    泵       │   │   传感器    │
│  (开关控制) │   │  (启停控制)  │   │  (数据采集) │
└─────────────┘   └─────────────┘   └─────────────┘
```

### 1.3 PLC能做什么？

| 功能 | 示例 |
|------|------|
| 读取数据 | 获取当前水温、流量、压力、液位 |
| 控制输出 | 开关阀门、启停泵、调节加热器 |
| 逻辑运算 | 根据条件自动执行清洗步骤 |
| 报警管理 | 检测异常、触发报警、记录故障 |
| 通信交互 | 与SCADA系统交换数据 |

### 1.4 为什么选择西门子S7-1500？

| 特性 | S7-1500优势 |
|------|-------------|
| 处理速度 | 纳秒级指令执行，胜任复杂控制 |
| 通信能力 | 内置Profinet，支持高速数据交换 |
| 编程语言 | 支持SCL高级语言，代码可读性强 |
| 诊断功能 | 内置Web服务器，远程诊断方便 |
| 扩展性 | 模块化设计，灵活扩展I/O |

### 1.5 系统架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CIP SCADA 系统架构                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                                    ▲
                                    │ HTTP/WebSocket
┌───────────────────────────────────┴───────────────────────────────────────┐
│                                  前端层                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Web浏览器 / HMI界面                             │  │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │    │ 仪表盘    │  │ 趋势图   │  │ 报警列表  │  │    配方管理      │  │  │
│  │    └──────────┘  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
                    HTTP/REST API ◄────► WebSocket
                                    │
┌────────────────────────────────────┴─────────────────────────────────────┐
│                                  后端层 (FastAPI)                            │
│                                                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │  PLC Service │  │ Data Service │  │Recipe Service│  │ Alarm Svc   │  │
│   │  (读写PLC)   │  │  (数据库)     │  │  (配方管理)  │  │  (报警)     │  │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└──────────┼─────────────────┼─────────────────┼─────────────────┼───────────┘
           │                 │                 │                 │
           ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PLC层 (西门子 S7-1500)                              │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │                         程序组织单元                                │  │
│   │                                                                      │  │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  │  │
│   │   │   OB组织块   │  │   FC函数    │  │   FB函数块  │  │   DB数据块 │  │  │
│   │   │  (程序入口)  │  │ (功能调用)  │  │ (带状态函数) │  │ (数据存储) │  │  │
│   │   └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘  │  │
│   │                                                                      │  │
│   │   ┌─────────────────────────────────────────────────────────────┐  │  │
│   │   │                        类型定义                               │  │  │
│   │   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │  │  │
│   │   │   │  枚举类型  │  │ 结构体类型 │  │  UDT用户  │  │  DataBlock │  │  │
│   │   │   └──────────┘  └──────────┘  └──────────┘  └──────────┘   │  │  │
│   │   └─────────────────────────────────────────────────────────────┘  │  │
│   └────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │                        功能模块分层                                │  │
│   │                                                                      │  │
│   │   ┌────────────────────────────────────────────────────────────┐  │  │
│   │   │  控制层: FC100_CIP_System (主调度)                          │  │  │
│   │   │         FC101-105_ZoneControl (各区清洗控制)                │  │  │
│   │   │         FC_MediaControl (介质选择)                          │  │  │
│   │   │         FC_PIDControl (PID温控)                            │  │  │
│   │   └────────────────────────────────────────────────────────────┘  │  │
│   │   ┌────────────────────────────────────────────────────────────┐  │  │
│   │   │  工具层: FC_Alarm (报警) | FC_History (历史) | FC_Sensor   │  │  │
│   │   └────────────────────────────────────────────────────────────┘  │  │
│   │                                                                      │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              设备层                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  温度传感器 │  │  流量计   │  │  电导率仪  │  │   阀门   │  │   泵     │  │
│  │  PT100    │  │  Flow    │  │  Cond    │  │  Valve   │  │  Pump    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                          CIP清洗五区分布                              │  │
│  │                                                                      │  │
│  │   [1区:水处理] → [2区:茶叶] → [3区:调配] → [4区:UHT] → [5区:灌装]    │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SCL语言入门

### 2.1 SCL是什么？

SCL (Structured Control Language) 是一种高级编程语言，类似Pascal/Python，适合复杂逻辑编程。

**对比其他PLC语言**：

| 语言 | 特点 | 适用场景 |
|------|------|----------|
| **SCL** | 文本式，高级语法 | 复杂运算、数据处理、状态机 |
| **梯形图 (LAD)** | 图形化，易懂 | 简单逻辑、开关控制 |
| **功能块 (FBD)** | 图形化，模块化 | 过程控制、PID调节 |

### 2.2 基本语法

#### 2.2.1 变量声明

``` scl
FUNCTION_BLOCK "Example"
VAR
    // 静态变量 (保持值)
    Counter : Int := 0;
    Temperature : Real := 25.5;
    IsRunning : Bool := FALSE;
END_VAR

VAR_TEMP
    // 临时变量 (每次调用后清零)
    TempValue : Int;
END_VAR
```

#### 2.2.2 基本数据类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `BOOL` | 布尔值 | `TRUE / FALSE` |
| `INT` | 16位整数 | `-32768 ~ 32767` |
| `DINT` | 32位整数 | -21亿 ~ 21亿 |
| `REAL` | 浮点数 | `3.14159` |
| `STRING` | 字符串 | `'Hello'` |
| `TIME` | 时间 | `T#5S` |

#### 2.2.3 赋值与运算

``` scl
// 赋值
Temperature := 85.5;

// 算术运算
Result := (A + B) * C / D;

// 比较运算
IF Temperature > 80 THEN
    Heating := FALSE;
END_IF;

// 逻辑运算
IF (A > 0) AND (B < 100) THEN
    IsValid := TRUE;
END_IF;
```

#### 2.2.4 条件判断 (IF语句)

``` scl
IF 条件1 THEN
    // 满足条件1时执行
    语句1;
ELSIF 条件2 THEN
    // 满足条件2时执行
    语句2;
ELSE
    // 都不满足时执行
    语句3;
END_IF;
```

**实际示例**：

``` scl
// 根据清洗状态执行不同逻辑
IF "Zone1".Status.State = "Enum_CleanState".IDLE THEN
    // 待机状态，等待启动命令
    "Zone1".Status.IsActive := FALSE;
    
ELSIF "Zone1".Status.State = "Enum_CleanState".STEP_EXEC THEN
    // 执行清洗步骤
    "Zone1".Status.IsActive := TRUE;
    
ELSIF "Zone1".Status.State = "Enum_CleanState".FAULT THEN
    // 故障状态，停止输出
    "FC_StopAllOutputs"(1);
END_IF;
```

#### 2.2.5 循环 (FOR语句)

``` scl
// 循环遍历5个清洗区
FOR i := 1 TO 5 DO
    "FC_UpdateZoneData"(i);
END_FOR;

// 倒序循环
FOR i := 5 TO 1 BY -1 DO
    "FC_StopZone"(i);
END_FOR;
```

**实际示例**：

``` scl
// OB100启动时初始化各区数据
FOR i := 1 TO 5 DO
    "FC_InitZoneData"(i);
END_FOR;
```

#### 2.2.6 选择 (CASE语句)

``` scl
CASE 变量 OF
    值1: 语句1;
    值2: 语句2;
    值3, 值4: 语句3;  // 多个值
ELSE
    语句4;  // 默认
END_CASE;
```

**实际示例**：

``` scl
// 根据区域ID调用对应的控制函数
CASE i OF
    1: "FC101_ZoneControl"();  // 1区清洗控制
    2: "FC102_ZoneControl"();  // 2区清洗控制
    3: "FC103_ZoneControl"();  // 3区清洗控制
    4: "FC104_ZoneControl"();  // 4区清洗控制
    5: "FC105_ZoneControl"();  // 5区清洗控制
END_CASE;
```

### 2.3 函数 (FC) vs 函数块 (FB)

| 特性 | FC (Function) | FB (Function Block) |
|------|---------------|---------------------|
| 是否有背景数据块 | 无 | 有 (实例IDB) |
| 内部变量保持 | 否 | 是 |
| 调用方式 | `CALL FCxxx()` | `CALL FBxxx.DBxxx()` |
| 适用场景 | 纯计算、无状态 | 有状态的控制逻辑 |

**本项目使用FC**，通过全局DB存储状态。

### 2.4 SCL代码模板

``` scl
// ============================================================================
// 功能说明
// ============================================================================
// 适用于: S7-1500 (TIA Portal V17)
// 版本: v1.0
// ============================================================================

FUNCTION "FCXXX_功能名" : Void
TITLE = "功能标题"
AUTHOR : "SCADA"
VERSION : "1.0"
VAR_TEMP
    // 临时变量
    i : Int;
END_VAR

    // ========================================================================
    // 1. 步骤说明
    // ========================================================================

    // 代码实现

END_FUNCTION
```

---

## 3. 项目结构总览

### 3.1 目录结构

```
project/plc/
├── control/              # 控制逻辑层
│   ├── CIP_Main.scl      # 主调度程序
│   ├── CIP_ZoneControl.scl  # 各区清洗控制
│   ├── CIP_MediaControl.scl # 介质选择控制
│   └── CIP_PIDControl.scl   # PID温度控制
├── ob/                   # 组织块
│   └── CIP_OB.scl        # OB1/OB100/OB35定义
├── types/                # 数据类型定义
│   ├── CIP_EnumTypes.scl     # 枚举类型
│   ├── CIP_StructTypes.scl   # 结构体类型
│   └── CIP_DataBlockDefs.scl # 数据块定义
├── utility/              # 工具函数
│   ├── CIP_Alarm.scl     # 报警管理
│   ├── CIP_History.scl   # 历史记录
│   ├── CIP_System.scl    # 系统函数
│   ├── CIP_Sensor.scl     # 传感器处理
│   └── CIP_Queue.scl      # 清洗队列管理
└── docs/
    └── README.md         # PLC文档索引
```

### 3.2 架构分层图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           程序架构分层                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              组织块层 (OB)                                    │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │  OB1  │   主程序循环 (每个扫描周期执行)                               │  │
│   ├────────────────────────────────────────────────────────────────────┤  │
│   │  OB100│   启动初始化 (CPU上电/重启时执行一次)                          │  │
│   ├────────────────────────────────────────────────────────────────────┤  │
│   │  OB35 │   周期性中断 (每100ms执行，快速响应)                           │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              控制逻辑层 (FC)                                  │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │                     FC100_CIP_System (主调度)                        │  │
│   │                                                                      │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│   │   │ FC101-105   │  │ FC_MediaCtrl │  │ FC_PIDCtrl   │               │  │
│   │   │ 各区清洗控制 │  │  介质选择    │  │  PID温控    │               │  │
│   │   └──────────────┘  └──────────────┘  └──────────────┘               │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              工具函数层 (FC)                                   │
│                                                                             │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│   │ Alarm  │  │History  │  │ Sensor  │  │ System  │  │ Queue  │        │
│   │ 报警   │  │ 历史   │  │ 传感器  │  │ 系统   │  │ 队列   │        │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据存储层 (DB)                                   │
│                                                                             │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                       │
│   │ Global  │  │ Zone1   │  │ Zone2   │  │ ... Zone5                      │
│   │ 全局数据 │  │ 1区数据  │  │ 2区数据  │  │ 5区数据                        │
│   └─────────┘  └─────────┘  └─────────┘  └─────────┘                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 五区同时清洗架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CIP清洗五区同时控制                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────────────┐
                    │      FC100_CIP_System           │
                    │           主调度                  │
                    └───────────────┬─────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ FC_Media  │   │FC_Queue   │   │FC_Alarm   │
            │ 介质控制   │   │ 队列管理   │   │ 报警处理   │
            └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
                  │               │               │
                  └───────┬───────┘               │
                          │                       │
        ┌─────────┬─────────┼─────────┬─────────┐   │
        │         │         │         │         │   │
        ▼         ▼         ▼         ▼         ▼
┌───────────┐┌───────────┐┌───────────┐┌───────────┐┌───────────┐
│  Zone1    ││  Zone2    ││  Zone3    ││  Zone4    ││  Zone5    │
│ 水处理区   ││ 茶叶区    ││ 调配区    ││ UHT区     ││ 灌装区    │
│           ││           ││           ││           ││           │
│ ┌───────┐ ││ ┌───────┐ ││ ┌───────┐ ││ ┌───────┐ ││ ┌───────┐ │
│ │PID温度│ ││ │PID温度│ ││ │PID温度│ ││ │PID温度│ ││ │PID温度│ │
│ │控制   │ ││ │控制   │ ││ │控制   │ ││ │控制   │ ││ │控制   │ │
│ └───────┘ ││ └───────┘ ││ └───────┘ ││ └───────┘ ││ └───────┘ │
│           ││           ││           ││           ││           │
│ ┌───────┐ ││ ┌───────┐ ││ ┌───────┐ ││ ┌───────┐ ││ ┌───────┐ │
│ │7状态  │ ││ │7状态  │ ││ │7状态  │ ││ │7状态  │ ││ │7状态  │ │
│ │状态机 │ ││ │状态机 │ ││ │状态机 │ ││ │状态机 │ ││ │状态机 │ │
│ └───────┘ ││ └───────┘ ││ └───────┘ ││ └───────┘ ││ └───────┘ │
└───────────┘└───────────┘└───────────┘└───────────┘└───────────┘
```

---

## 4. 数据类型详解

### 4.1 枚举类型 (Enum)

枚举定义一组有序的命名常量，代码可读性更强。

#### 4.1.1 清洗介质类型

``` scl
TYPE "Enum_MediaType"
    PURE_WATER := 0,    // 纯水冲洗
    ALKALI     := 1,    // 碱洗 (2% NaOH, 85℃)
    ACID       := 2,    // 酸洗 (1% HNO3, 60℃)
    HOT_WATER  := 3,    // 热水洗 (85℃)
    DISINFECT  := 4,    // 消毒液 (0.5%)
END_TYPE
```

**使用示例**：

``` scl
// 判断当前介质类型
IF "Zone1".Step.CurrentMedia = "Enum_MediaType".ALKALI THEN
    // 碱洗逻辑，设置目标温度85℃
    "Zone1".Config.TargetTemp := 85.0;
END_IF;
```

#### 4.1.2 清洗状态

``` scl
TYPE "Enum_CleanState"
    IDLE             := 0,   // 待机
    READY            := 1,   // 准备就绪
    STEP_EXEC        := 2,   // 步骤执行中
    STEP_TRANSITION  := 3,   // 步骤切换中
    COMPLETE         := 4,   // 清洗完成
    PAUSE            := 5,   // 暂停
    FAULT            := 6,   // 故障
END_TYPE
```

**状态转换图**：

```
                    ┌──────────┐
                    │   IDLE   │
                    │   待机    │
                    └────┬─────┘
                         │ 启动命令
                         ▼
                    ┌──────────┐
                    │  READY   │
                    │  准备就绪 │
                    └────┬─────┘
                         │ 条件满足
                         ▼
              ┌─────────────────────┐
              │     STEP_EXEC      │
              │    步骤执行中        │
              └──────────┬──────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  步骤完成│    │   暂停   │    │   故障   │
    │(下一步或)│    │  PAUSE  │    │  FAULT  │
    │  COMPLETE   │         │    │         │
    └─────────┘    └────┬────┘    └─────────┘
                        │               │
                        │ 恢复命令       │ 复位
                        ▼               ▼
                   回到STEP_EXEC    回到IDLE
```

#### 4.1.3 报警等级

``` scl
TYPE "Enum_AlarmLevel"
    L0_CRITICAL := 0,    // 严重 - 急停、泵过载
    L1_WARNING  := 1,    // 警告 - 温度不达标、无流量
    L2_INFO     := 2,    // 提示 - 液位低
END_TYPE
```

#### 4.1.4 其他枚举

``` scl
// 就地/远程模式
TYPE "Enum_HandsMode"
    LOCAL  := 0,    // 就地 (本地操作)
    REMOTE := 1,    // 远程 (SCADA控制)
END_TYPE

// 阀门状态
TYPE "Enum_ValveState"
    VALVE_CLOSED := 0,
    VALVE_OPEN   := 1,
    VALVE_FAULT  := 2,
END_TYPE

// 泵状态
TYPE "Enum_PumpState"
    PUMP_STOP    := 0,
    PUMP_RUN     := 1,
    PUMP_FAULT   := 2,
    PUMP_WARNING := 3,
END_TYPE

// 控制命令
TYPE "Enum_ControlCmd"
    CMD_NONE     := 0,   // 无命令
    CMD_START    := 1,   // 启动清洗
    CMD_STOP     := 2,   // 停止清洗
    CMD_PAUSE    := 3,   // 暂停
    CMD_RESUME   := 4,   // 恢复
    CMD_RESET    := 5,   // 复位/清除故障
END_TYPE
```

### 4.2 结构体类型 (Struct)

结构体将多个相关变量组合成一个整体。

#### 4.2.1 配方步骤结构

``` scl
TYPE "Struct_RecipeStep"
    // 清洗介质
    MediaType    : "Enum_MediaType";  // 介质类型
    // 温度设置
    TargetTemp   : Real;              // 目标温度 ℃
    MinTemp      : Real;              // 最低温度 ℃
    TempHoldTime : Int;               // 保温时间 秒
    // 流量设置
    TargetFlow   : Real;              // 目标流量 L/h
    MinFlow      : Real;              // 最低流量 L/h
    // 时间设置
    StepTime     : Int;               // 步骤总时间 秒
END_STRUCT
```

**使用示例**：

``` scl
// 从配方中读取当前步骤
"Zone1".Step.CurrentMedia := "RecipeDefault".Steps[1].MediaType;
"Zone1".Config.TargetTemp := "RecipeDefault".Steps[1].TargetTemp;
```

#### 4.2.2 区域状态结构

``` scl
TYPE "Struct_ZoneStatus"
    State         : "Enum_CleanState";  // 当前状态
    CurrentStep   : Int;                 // 当前步骤号
    StepTimer     : Int;                 // 步骤计时器
    IsActive      : Bool;                // 是否激活
    StepCompleted : Bool;                // 步骤是否完成
END_STRUCT
```

#### 4.2.3 传感器数据结构

``` scl
TYPE "Struct_SensorData"
    // 模拟量
    Temperature  : Real;   // 温度 ℃
    Flow         : Real;   // 流量 L/h
    Conductivity : Real;   // 电导率 μS/cm
    Pressure     : Real;   // 压力 bar
    Level        : Real;   // 液位 %
    // 数字量
    FlowSwitch   : Bool;   // 流量开关
    LevelSwitch  : Bool;   // 液位开关
END_STRUCT
```

### 4.3 数据块 (DB) 定义

数据块是存储实际数据的区域，每个清洗区有独立的数据块。

``` scl
DATA_BLOCK "DB100_Zone1"
TITLE = "1区数据块"
STRUCT
    // 状态数据
    Status : "Struct_ZoneStatus";
    
    // 配置数据
    Config : "Struct_ZoneConfig";
    
    // 步骤数据
    Step : "Struct_ZoneStep";
    
    // 传感器数据
    Sensor : "Struct_SensorData";
    
    // 执行数据
    Execute : "Struct_ZoneExecute";
END_STRUCT

BEGIN
    // 初始值
    Status.State := "Enum_CleanState".IDLE;
    Config.TargetTemp := 85.0;
END_DATA_BLOCK
```

### 4.4 全局数据块

``` scl
DATA_BLOCK "Global"
TITLE = "全局数据块"
STRUCT
    // 系统状态
    System : "Struct_SystemStatus";
    
    // 各区引用
    Zone : ARRAY[1..5] OF "Struct_ZoneRef";
    
    // 配方
    Recipe : "Struct_RecipeHeader";
END_STRUCT
BEGIN
END_DATA_BLOCK
```

---

## 5. 组织块说明

### 5.1 OB1 - 主程序循环

OB1是PLC的主入口，每个扫描周期自动执行一次。

``` scl
ORGANIZATION_BLOCK "OB1"
TITLE = "主程序循环"
AUTHOR : "SCADA"
VERSION : "1.0"
VAR_TEMP
    i : Int;
END_VAR

    // 1. 急停检查
    IF "Global".System.EStop THEN
        "FC_EmergencyStop"();
        RETURN;  // 退出本次扫描
    END_IF;

    // 2. 就地/远程模式检查
    IF "Global".System.HandsMode = "Enum_HandsMode".LOCAL THEN
        RETURN;  // 就地模式，PLC不控制
    END_IF;

    // 3. CIP系统主调度
    "FC100_CIP_System"();

    // 4. 系统状态更新
    "FC_UpdateSystemStatus"();

END_ORGANIZATION_BLOCK
```

**执行流程图**：

```
┌─────────────────────────────────────┐
│           OB1 开始                   │
└─────────────────┬───────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   急停检查       │
        │ EStop = TRUE?   │
        └────────┬────────┘
                 │
       ┌─────────┴─────────┐
       │YES                │NO
       ▼                   ▼
┌─────────────┐    ┌─────────────────┐
│ 急停处理    │    │ 就地/远程检查    │
│ 返回退出    │    │ HandsMode = ?   │
└─────────────┘    └────────┬────────┘
                             │
                   ┌─────────┴─────────┐
                   │LOCAL              │REMOTE
                   ▼                   ▼
           ┌─────────────┐    ┌─────────────────┐
           │ 本地操作     │    │ 执行CIP主调度    │
           │ 不做自动控制 │    │ FC100_CIP_System │
           └─────────────┘    └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │ 更新系统状态     │
                               │ FC_UpdateStatus  │
                               └────────┬────────┘
                                        │
                                        ▼
                               ┌─────────────────┐
                               │    OB1 结束      │
                               └─────────────────┘
```

### 5.2 OB100 - 启动初始化

OB100在CPU上电或重启时执行一次，用于初始化系统。

``` scl
ORGANIZATION_BLOCK "OB100"
TITLE = "启动初始化"
AUTHOR : "SCADA"
VERSION : "1.0"
VAR_TEMP
    i : Int;
END_VAR

    // 1. 初始化全局数据
    "FC_InitGlobalData"();

    // 2. 初始化各区数据
    FOR i := 1 TO 5 DO
        "FC_InitZoneData"(i);
    END_FOR;

    // 3. 初始化配方数据
    "FC_InitRecipeData"();

    // 4. 复位急停状态
    "Global".System.EStop := FALSE;
    "Global".System.SystemReady := TRUE;

END_ORGANIZATION_BLOCK
```

**初始化流程图**：

```
┌─────────────────────────────────────┐
│     OB100 启动 (CPU上电/重启)        │
└─────────────────┬───────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │  初始化全局数据   │
        │ FC_InitGlobal   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  FOR i=1 TO 5   │
        │  初始化各区数据   │
        │ FC_InitZone(i)  │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  初始化配方数据   │
        │ FC_InitRecipe   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │  复位急停标志   │
        │  设置系统就绪   │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │    OB100 结束    │
        └─────────────────┘
```

### 5.3 OB35 - 周期性中断

OB35以固定时间间隔执行，用于快速响应任务（如PID控制、传感器采集）。

``` scl
ORGANIZATION_BLOCK "OB35"
TITLE = "周期性中断"
AUTHOR : "SCADA"
VERSION : "1.0"
VAR_TEMP
    i : Int;
END_VAR
VAR
    OB35_TickCounter : Int := 0;  // 静态变量
END_VAR

    // 100ms计时累加
    OB35_TickCounter := OB35_TickCounter + 1;

    // 1. 传感器数据采集
    "FC_ReadSensorData"();

    // 2. 温度PID控制
    "FC_TempPIDControl"();

    // 3. 流量PID控制 (5区)
    FOR i := 1 TO 5 DO
        "FC_FlowPIDControl"(i);
    END_FOR;

    // 4. 报警检测
    "FC_CheckAlarms"();

    // 5. 秒级计时更新 (每10个100ms = 1秒)
    IF OB35_TickCounter >= 10 THEN
        OB35_TickCounter := 0;
        "FC_UpdateSecondTimers"();
    END_IF;

END_ORGANIZATION_BLOCK
```

**任务优先级**：

| 组织块 | 触发条件 | 周期 | 用途 |
|--------|----------|------|------|
| OB1 | 扫描周期 | 不固定 | 主程序逻辑 |
| OB35 | 时间中断 | 100ms | 快速响应任务 |
| OB100 | CPU启动 | 一次 | 初始化 |

---

## 6. 核心控制逻辑

### 6.1 主调度程序 (FC100)

主调度是系统的核心，负责协调各区清洗和资源管理。

``` scl
FUNCTION "FC100_CIP_System" : Void
VAR_TEMP
    i : Int;
END_VAR

    // 1. 更新传感器数据到区域状态
    FOR i := 1 TO 5 DO
        "FC_UpdateZoneData"(i);
    END_FOR;

    // 2. 处理清洗队列
    "FC400_QueueManager"();

    // 3. 执行各区清洗控制
    FOR i := 1 TO 5 DO
        CASE i OF
            1: "FC101_ZoneControl"();
            2: "FC102_ZoneControl"();
            3: "FC103_ZoneControl"();
            4: "FC104_ZoneControl"();
            5: "FC105_ZoneControl"();
        END_CASE;
    END_FOR;

    // 4. 介质资源管理
    "FC_ManageMediaResources"();

    // 5. 报警处理
    "FC300_AlarmHandler"();

END_FUNCTION
```

### 6.2 各区清洗控制

每个区封装为独立函数，内部调用通用控制逻辑。

``` scl
// FC101: 1区清洗控制 (示例)
FUNCTION "FC101_ZoneControl" : Void
VAR_TEMP
    ZoneID : Int := 1;
END_VAR
    "FC_ZoneControl"(ZoneID);
END_FUNCTION

// FC102-105 类似结构
```

### 6.3 7状态状态机

每个清洗区使用7状态状态机控制：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            7状态状态机                                        │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────────────┐
    │                                                                      │
    │                     ┌─────────────┐                                │
    │                     │   IDLE      │                                │
    │                     │   待机      │                                │
    │                     └──────┬──────┘                                │
    │                            │                                        │
    │              启动命令+条件满足│                                        │
    │                            ▼                                        │
    │                     ┌─────────────┐                                │
    │                     │   READY    │                                │
    │                     │   准备就绪  │                                │
    │                     └──────┬──────┘                                │
    │                            │                                        │
    │                      条件满足│                                        │
    │                            ▼                                        │
    │   ┌──────────────────────────────────────────────────────────────┐  │
    │   │                        STEP_EXEC                            │  │
    │   │                      步骤执行中                              │  │
    │   │                                                               │  │
    │   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │  │
    │   │   │  温度控制    │  │  流量控制    │  │  时间控制    │        │  │
    │   │   │ PID调节     │  │ PID调节     │  │ 计时中...    │        │  │
    │   │   └─────────────┘  └─────────────┘  └─────────────┘        │  │
    │   │                                                               │  │
    │   └──────────────────────────────────────────────────────────────┘  │
    │                            │                                        │
    │              ┌─────────────┼─────────────┐                          │
    │              │             │             │                          │
    │              ▼             ▼             ▼                          │
    │     ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                 │
    │     │ STEP_COMPLETE│ │   PAUSE    │ │   FAULT     │                 │
    │     │  步骤完成    │ │    暂停     │ │    故障     │                 │
    │     └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                 │
    │            │               │               │                        │
    │     下一步或│        恢复命令│         复位命令│                        │
    │     完成   │               │               │                        │
    │            └───────┬───────┘               │                        │
    │                    ▼                       ▼                        │
    │           ┌─────────────────┐     ┌─────────────┐                  │
    │           │    COMPLETE      │     │    IDLE     │                  │
    │           │    清洗完成       │     │    待机     │                  │
    │           └─────────────────┘     └─────────────┘                  │
    │                                                                  │
    └──────────────────────────────────────────────────────────────────────┘
```

### 6.4 PID温度控制

PID控制实现精确的温度调节：

``` scl
// PID控制参数结构
TYPE "Struct_PIDConfig"
    SetPoint    : Real;   // 设定值 (目标温度)
    Kp          : Real;   // 比例系数
    Ki          : Real;   // 积分系数
    Kd          : Real;   // 微分系数
END_STRUCT

// PID控制逻辑
FUNCTION "FC_TempPIDControl" : Void
VAR_TEMP
    Error     : Real;
    Output    : Real;
END_VAR

    FOR i := 1 TO 5 DO
        // 计算温度偏差
        Error := "Zone".Config.TargetTemp - "Zone".Sensor.Temperature;
        
        // PID计算 (简化)
        Output := "PID".Kp * Error 
                + "PID".Ki * "PID".Integral 
                + "PID".Kd * (Error - "PID".LastError);
        
        // 输出限制 (0-100%)
        Output := LIMIT(0.0, Output, 100.0);
        
        // 输出到加热阀
        "Zone".Execute.HeatingOutput := Output;
    END_FOR;

END_FUNCTION
```

**PID控制原理**：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PID控制原理                                      │
└─────────────────────────────────────────────────────────────────────────────┘

    设定值                                      加热器
    (Target)      ┌───────┐       ┌───────┐      │
       ──────────►│  PID  │──────►│ 限幅  │──────┤
                 └───────┘       └───────┘      │
       │             ▲                            │
       │             │                            ▼
       │      ┌──────┴───────┐              ┌──────────┐
       │      │   反馈        │              │  设备    │
       │      │  (当前温度)   │              │  (加热)  │
       │      └──────┬───────┘              └──────────┘
       │             │                            │
       │             │      ┌──────────┐          │
       └─────────────┴─────►│  温度    │◄─────────┘
                            │  传感器  │
                            └──────────┘
                                 ▲
                                 │
                            测量值反馈
                            
┌─────────────────────────────────────────────────────────────────────────────┐
│  P (比例)  │ 响应速度  │ 当前误差直接乘系数                                 │
│  I (积分)  │ 消除稳态误差 │ 累积误差乘系数                                  │
│  D (微分)  │ 预测趋势  │ 误差变化率乘系数                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.5 介质资源管理

``` scl
// 介质类型
TYPE "Enum_MediaType"
    PURE_WATER := 0,    // 纯水冲洗
    ALKALI     := 1,    // 碱洗
    ACID       := 2,    // 酸洗
    HOT_WATER  := 3,    // 热水
    DISINFECT  := 4,    // 消毒
END_TYPE

// 介质选择逻辑
FUNCTION "FC_ManageMediaResources" : Void

    // 遍历所有区
    FOR i := 1 TO 5 DO
        // 根据介质类型打开对应阀门
        CASE "Zone".Step.CurrentMedia OF
            "Enum_MediaType".ALKALI:
                "Valve_Alkali" := TRUE;
            "Enum_MediaType".ACID:
                "Valve_Acid" := TRUE;
            "Enum_MediaType".HOT_WATER:
                "Valve_HotWater" := TRUE;
        ELSE
            // 默认纯水
            "Valve_PureWater" := TRUE;
        END_CASE;
    END_FOR;

END_FUNCTION
```

---

## 7. 工具函数库

### 7.1 报警管理 (FC_Alarm)

``` scl
// 报警结构
TYPE "Struct_Alarm"
    ID       : Int;          // 报警ID
    Code     : Int;          // 报警代码
    Level    : "Enum_AlarmLevel";  // 报警等级
    Message  : String[50];   // 报警消息
    OccurTime: Date_And_Time; // 发生时间
    Acked    : Bool;         // 是否确认
END_STRUCT

// 报警检测
FUNCTION "FC_CheckAlarms" : Void

    FOR i := 1 TO 5 DO
        // 温度超限检测
        IF "Zone".Sensor.Temperature > 95.0 THEN
            "FC_TriggerAlarm"(i, 101, "Enum_AlarmLevel".L0_CRITICAL, 
                            'Temperature exceeds 95°C');
        END_IF;
        
        // 流量异常检测
        IF "Zone".Sensor.Flow < "Zone".Config.MinFlow THEN
            "FC_TriggerAlarm"(i, 201, "Enum_AlarmLevel".L1_WARNING,
                            'Flow rate below minimum');
        END_IF;
    END_FOR;

END_FUNCTION
```

**报警等级与响应**：

| 等级 | 说明 | 响应动作 |
|------|------|----------|
| L0_CRITICAL | 严重 | 立即停止、触发急停 |
| L1_WARNING | 警告 | 记录报警、继续运行 |
| L2_INFO | 提示 | 记录日志、显示信息 |

### 7.2 历史记录 (FC_History)

``` scl
// 历史记录结构
TYPE "Struct_HistoryEntry"
    Timestamp : Date_And_Time;
    EventType : Int;
    ZoneID    : Int;
    Data      : Array[1..10] of Real;
END_STRUCT

// 记录清洗数据
FUNCTION "FC_SaveHistory" : Void
VAR_TEMP
    Index : Int;
END_VAR

    // 获取下一个写入位置
    Index := "History".WriteIndex MOD 1000 + 1;
    
    // 写入历史记录
    "History".Entries[Index].Timestamp := CURRENT_DATE;
    "History".Entries[Index].EventType := 1;
    "History".Entries[Index].ZoneID := ZoneID;
    
    // 更新写指针
    "History".WriteIndex := Index;

END_FUNCTION
```

### 7.3 传感器处理 (FC_Sensor)

``` scl
// 读取传感器数据
FUNCTION "FC_ReadSensorData" : Void

    FOR i := 1 TO 5 DO
        // 读取温度 (PT100)
        "Zone".Sensor.Temperature := READ_IF("AI_Temp_Zone%i", i);
        
        // 读取流量
        "Zone".Sensor.Flow := READ_IF("AI_Flow_Zone%i", i);
        
        // 读取流量开关
        "Zone".Sensor.FlowSwitch := READ_DI("DI_FlowSwitch_Zone%i", i);
    END_FOR;

END_FUNCTION
```

### 7.4 系统函数 (FC_System)

``` scl
// 初始化全局数据
FUNCTION "FC_InitGlobalData" : Void
BEGIN
    "Global".System.EStop := FALSE;
    "Global".System.SystemReady := FALSE;
    "Global".System.HandsMode := "Enum_HandsMode".REMOTE;
    "Global".System.OperationMode := 0;
END_FUNCTION

// 急停处理
FUNCTION "FC_EmergencyStop" : Void
BEGIN
    // 关闭所有泵
    FOR i := 1 TO 5 DO
        "FC_StopAllOutputs"(i);
    END_FOR;
    
    // 设置急停标志
    "Global".System.EStop := TRUE;
END_FUNCTION
```

### 7.5 队列管理 (FC_Queue)

``` scl
// 清洗队列结构
TYPE "Struct_CleanQueue"
    Entries    : Array[1..10] of Int;  // 排队的区域ID
    Count      : Int;                  // 队列长度
    Front      : Int;                  // 队首
    Rear       : Int;                  // 队尾
END_STRUCT

// 添加到队列
FUNCTION "FC_AddToQueue" : Void
    IF "Queue".Count < 10 THEN
        "Queue".Rear := "Queue".Rear" MOD 10 + 1;
        "Queue".Entries["Queue".Rear] := ZoneID;
        "Queue".Count := "Queue".Count + 1;
    END_IF;
END_FUNCTION

// 从队列取出
FUNCTION "FC_GetFromQueue" : Int
    IF "Queue".Count > 0 THEN
        "FC_GetFromQueue" := "Queue".Entries["Queue".Front];
        "Queue".Front" := "Queue".Front" MOD 10 + 1;
        "Queue".Count := "Queue".Count - 1;
    END_IF;
END_FUNCTION
```

---

## 8. TIA Portal导入

### 8.1 文件导入顺序

正确的导入顺序很重要，否则会出现依赖错误：

```
1. 枚举类型     → CIP_EnumTypes.scl
   ↓
2. 结构体类型   → CIP_StructTypes.scl
   ↓
3. 数据块定义   → CIP_DataBlockDefs.scl
   ↓
4. 组织块       → CIP_OB.scl
   ↓
5. 工具函数     → utility/*.scl
   ↓
6. 控制函数     → control/*.scl
```

### 8.2 导入步骤

**步骤1：创建新项目**

1. 打开 TIA Portal V17
2. 点击"创建新项目"
3. 选择CPU类型 S7-1500
4. 进入项目视图

**步骤2：添加设备**

1. 在项目树中右键"添加设备"
2. 选择"PC系统" → Simulated PLC
3. 或选择实际PLC硬件

**步骤3：导入SCL源文件**

1. 右键"PLC_1" → "添加新对象" → "程序模块"
2. 选择类型：组织块(OB)、函数(FC)、函数块(FB)、数据类型(UDT)
3. 从源文件导入

**步骤4：编译检查**

1. 点击"编译"按钮
2. 检查错误列表
3. 修复所有错误

### 8.3 配置Profinet通信

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TIA Portal Profinet配置                               │
└─────────────────────────────────────────────────────────────────────────────┘

1. 添加PLC设备
   └─ 设备配置
       └─ PROFINET接口 [X1]
           └─ 以太网地址: 192.168.0.1

2. 配置通信模块
   └─ 分布式I/O
       └─ 添加ET200SP站
           └─ 配置I/O地址

3. 设置连接参数
   └─ 连接机制
       └─ √ 允许PUT/GET访问
       └─ √ 允许远程HMI访问
```

### 8.4 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+S | 保存 |
| Ctrl+B | 编译 |
| Ctrl+D | 下载到设备 |
| F1 | 帮助 |
| F5 | 在线连接 |
| Ctrl+Shift+X | 离线模式 |

---

## 9. 项目实战练习

### 练习1：添加新清洗介质

**目标**：添加"最终冲洗"介质类型

**步骤**：

1. 在 `CIP_EnumTypes.scl` 中添加枚举值：

``` scl
TYPE "Enum_MediaType"
    PURE_WATER := 0,    // 纯水冲洗
    ALKALI     := 1,    // 碱洗
    ACID       := 2,    // 酸洗
    HOT_WATER  := 3,    // 热水
    DISINFECT  := 4,    // 消毒
    FINAL_RINSE := 5,   // 最终冲洗 (新增)
END_TYPE
```

2. 在配方结构中添加对应参数：

``` scl
TYPE "Struct_RecipeStep"
    MediaType    : "Enum_MediaType";
    TargetTemp   : Real;
    MinTemp      : Real;
    TempHoldTime : Int;
    TargetFlow   : Real;
    MinFlow      : Real;
    StepTime     : Int;
    RinseCycles  : Int := 3;  // 新增：冲洗循环次数
END_STRUCT
```

3. 在介质控制中添加处理逻辑：

``` scl
FUNCTION "FC_ManageMediaResources" : Void
    // ... 现有代码 ...
    
    "Enum_MediaType".FINAL_RINSE:
        // 最终冲洗：纯水循环3次
        "Valve_PureWater" := TRUE;
        "Valve_Drain" := ("Zone".Step.RinseCount MOD 2 = 0);
END_FUNCTION
```

### 练习2：实现清洗步骤跳过

**目标**：添加跳过当前步骤的功能

**步骤**：

1. 添加命令枚举：

``` scl
TYPE "Enum_ControlCmd"
    CMD_NONE     := 0,
    CMD_START    := 1,
    CMD_STOP     := 2,
    CMD_PAUSE    := 3,
    CMD_RESUME   := 4,
    CMD_RESET    := 5,
    CMD_SKIP     := 6,  // 新增：跳过
END_TYPE
```

2. 在控制逻辑中处理：

``` scl
FUNCTION "FC_ZoneControl" : Void
VAR_INPUT
    ZoneID : Int;
END_VAR

    // 处理命令
    CASE "Zone".Command OF
        "Enum_ControlCmd".CMD_SKIP:
            // 标记步骤完成
            "Zone".Status.StepCompleted := TRUE;
            // 转到下一步
            "Zone".Status.CurrentStep := "Zone".Status.CurrentStep + 1;
            // 复位命令
            "Zone".Command := "Enum_ControlCmd".CMD_NONE;
    END_CASE;
    
END_FUNCTION
```

### 练习3：添加新的报警类型

**目标**：添加"电导率超标"报警

**步骤**：

1. 定义报警代码：

``` scl
// 报警代码定义
// 100-199: 温度相关
// 200-299: 流量相关
// 300-399: 电导率相关  (新增)
#define ALARM_COND_HIGH   301
#define ALARM_COND_LOW    302
```

2. 实现报警检测：

``` scl
FUNCTION "FC_CheckAlarms" : Void
    // ... 现有代码 ...
    
    // 电导率检测 (新增)
    IF "Zone".Sensor.Conductivity > "Zone".Config.MaxConductivity THEN
        "FC_TriggerAlarm"(
            ZoneID,
            ALARM_COND_HIGH,
            "Enum_AlarmLevel".L1_WARNING,
            'Conductivity exceeds limit'
        );
    END_IF;
END_FUNCTION
```

### 练习4：多语言报警消息

**目标**：支持中英文报警消息

**步骤**：

1. 创建消息表：

``` scl
DATA_BLOCK "AlarmMessages"
STRUCT
    MsgTable : ARRAY[1..500] OF "Struct_AlarmMessage";
END_STRUCT
BEGIN
    // 格式: [代码] = {英文, 中文}
    MsgTable[101] := ('Temp High', '温度过高');
    MsgTable[201] := ('Flow Low', '流量过低');
    MsgTable[301] := ('Cond High', '电导率超标');
END_DATA_BLOCK
```

2. 使用消息表：

``` scl
FUNCTION "FC_TriggerAlarm" : Void
VAR_INPUT
    ZoneID  : Int;
    Code    : Int;
    Level   : "Enum_AlarmLevel";
END_VAR
    "Alarm".Code := Code;
    "Alarm".Message := "AlarmMessages".MsgTable[Code].CN;  // 中文
END_FUNCTION
```

---

## 10. 调试方法

### 10.1 监视模式

在TIA Portal中进入在线监视：

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              调试工具                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   监视表         │     │   强制表         │     │   调用环境        │
│   (Watch Table)   │     │   (Force Table)   │     │   (Call Stack)   │
│                  │     │                  │     │                  │
│  - 查看变量值     │     │  - 强制赋值       │     │  - 查看调用路径   │
│  - 监视表达式     │     │  - 强制输出       │     │  - 定位错误       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### 10.2 使用监视表

1. 创建监视表：

```
右键 "添加新对象" → "监视表"
```

2. 添加监视变量：

```
名称              │ 格式     │ 地址        │ 监视值
──────────────────┼──────────┼────────────┼──────────
Zone1.State       | Int      | DB100.DBD0  | 0
Zone1.TargetTemp  | Real     | DB100.DBD4  | 85.0
Zone1.Sensor.Temp | Real     | DB100.DBD8  | 78.5
```

3. 触发监视：

```
点击 "监视" 按钮 (眼镜图标)
```

### 10.3 常见问题排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 变量显示 `#` | 数据类型不匹配 | 检查变量类型定义 |
| 值不更新 | 未触发读取 | 检查扫描周期 |
| 写入失败 | 访问权限不足 | 检查保护级别 |
| 通信失败 | IP地址错误 | 检查Profinet配置 |

### 10.4 强制变量

⚠️ **注意**：强制操作会覆盖实际值，可能导致设备动作！

``` scl
// 强制变量示例 (TIA Portal)
1. 打开强制表
2. 添加变量: "Zone1".Command = 1 (启动)
3. 点击 "强制" 按钮
4. 观察设备响应
```

### 10.5 调用环境检查

当程序报错时，使用调用环境查看调用路径：

```
1. 双击错误信息
2. 点击 "显示调用环境"
3. 逐级查看调用栈
4. 定位具体位置
```

---

## 11. 常见问题

### Q1: 如何查看PLC的IP地址？

**解答**：

1. TIA Portal中双击设备
2. 选择"属性" → "常规" → "PROFINET接口"
3. 查看"以太网地址"

**命令行查询**：

``` bash
# 使用Ping查找
ping 192.168.0.1

# 使用Snap7工具
snap7-library → plcInfo 192.168.0.1
```

### Q2: 为什么变量值一直是0？

**常见原因**：

| 原因 | 检查方法 |
|------|----------|
| 地址错误 | 检查DB块偏移量 |
| 未编译 | 重新编译下载 |
| 离线模式 | 检查在线连接 |
| 变量未映射 | 检查I/O映射 |

**解决方法**：

```
1. 确认PLC在线 (状态栏绿色)
2. 检查变量地址是否正确
3. 重新编译整个项目
4. 重新下载到PLC
```

### Q3: 如何恢复出厂设置？

**操作步骤**：

```
TIA Portal:
1. 在线连接PLC
2. 右键PLC → "重置为出厂设置"
3. 选择"保留IP设置" (可选)
4. 确认重置

注意：这会删除所有程序和数据！
```

### Q4: OB35中断不执行？

**检查项**：

| 检查项 | 方法 |
|--------|------|
| OB35是否存在 | 查看项目树 |
| 硬件配置 | 检查"常规"→"组态"→"时间中断" |
| 优先级 | 检查中断优先级设置 |
| 扫描时间 | 确认扫描周期 |

### Q5: 如何添加新的I/O点？

**步骤**：

```
1. 硬件目录拖拽模块到机架
2. 自动分配地址
3. 在变量表中创建变量
4. 地址自动关联
5. 编译下载
```

### Q6: 程序下载失败怎么办？

**常见原因与解决**：

| 原因 | 解决 |
|------|------|
| IP不匹配 | 检查PC和PLC IP在同一网段 |
| 防火墙拦截 | 关闭防火墙或开放102端口 |
| 另一个连接 | 断开其他连接 |
| CPU运行中 | 切换到STOP模式 |

### Q7: SCL编译错误如何排查？

**常见错误**：

``` scl
// 错误1: 缺少 END_IF
IF A > B THEN
    X := 1;
    // 忘记 END_IF

// 错误2: 变量未声明
TempValue := 100;  // TempValue 未声明

// 错误3: 类型不匹配
IntVar := RealVar;  // 需要转换
IntVar := DINT_TO_INT(RealVar);

// 错误4: 数组越界
ArrayVar[11] := 1;  // 数组大小为10
```

### Q8: 如何优化扫描周期？

**方法**：

1. 减少OB1中的计算
2. 将复杂计算移到OB35
3. 使用间接寻址减少代码量
4. 优化循环结构

``` scl
// 优化前
FOR i := 1 TO 5 DO
    "FC_SomeFunction"(i);
END_FOR;

// 优化后 (减少函数调用)
FOR i := 1 TO 5 DO
    // 直接内联简单逻辑
    "Zone".TempValue := i * 10;
END_FOR;
```

---

## 12. 术语表

### 12.1 PLC相关

| 术语 | 全称 | 说明 |
|------|------|------|
| PLC | Programmable Logic Controller | 可编程逻辑控制器 |
| CPU | Central Processing Unit | 中央处理器 |
| OB | Organization Block | 组织块，程序入口 |
| FC | Function | 函数，无状态 |
| FB | Function Block | 函数块，有状态 |
| DB | Data Block | 数据块，存储数据 |
| UD | User-defined Type | 用户定义类型 |
| SCL | Structured Control Language | 结构化控制语言 |
| LAD | Ladder Diagram | 梯形图 |
| FBD | Function Block Diagram | 功能块图 |

### 12.2 通信相关

| 术语 | 说明 |
|------|------|
| Profinet | 西门子工业以太网协议 |
| S7 Protocol | 西门子S7通信协议 |
| OPC UA | 工业通信标准 |
| MPI | 多点接口通信 |
| Modbus | 通用工业协议 |

### 12.3 控制系统相关

| 术语 | 说明 |
|------|------|
| PID | 比例-积分-微分控制器 |
| HMI | 人机界面 |
| SCADA | 数据采集与监控系统 |
| I/O | 输入/输出 |
| AI | 模拟量输入 |
| AO | 模拟量输出 |
| DI | 数字量输入 |
| DO | 数字量输出 |

### 12.4 CIP系统相关

| 术语 | 说明 |
|------|------|
| CIP | 就地清洗 (Clean-In-Place) |
| UHT | 超高温瞬时杀菌 |
| HTST | 高温短时巴氏杀菌 |
| NaOH | 氢氧化钠 (碱) |
| HNO3 | 硝酸 (酸) |
| Conductivity | 电导率 |

### 12.5 数据类型

| 类型 | 范围 | 说明 |
|------|------|------|
| BOOL | TRUE/FALSE | 布尔 |
| INT | -32768~32767 | 16位整数 |
| DINT | -21亿~21亿 | 32位整数 |
| REAL | ±1.18E-38~±3.4E38 | 浮点数 |
| TIME | T# | 时间类型 |
| STRING | 字符串 | 字符数组 |

---

## 13. 学习路径建议

### 13.1 学习阶段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PLC学习路线                                        │
└─────────────────────────────────────────────────────────────────────────────┘

阶段1: 入门 (1-2周)
├── 理解PLC基本原理
├── 学习SCL基础语法
├── 熟悉TIA Portal操作
└── 完成练习1-2

阶段2: 进阶 (2-4周)
├── 掌握数据结构和类型
├── 理解组织块机制
├── 学习状态机编程
└── 完成练习3-4

阶段3: 实战 (4-8周)
├── 理解CIP清洗工艺
├── 分析本项目代码
├── 独立完成功能修改
└── 调试与优化

阶段4: 精通 (持续)
├── 学习高级特性
├── 性能优化
├── 故障诊断
└── 项目管理
```

### 13.2 推荐学习资源

| 资源类型 | 推荐内容 |
|----------|----------|
| 官方文档 | 西门子 S7-1500 系统手册 |
| 在线教程 | TIA Portal 入门指南 |
| 视频课程 | Siemens SITRAIN |
| 实践项目 | 本CIP清洗系统 |

### 13.3 进阶主题

| 主题 | 说明 | 推荐深入 |
|------|------|----------|
| 高级PID | 串级PID、自适应PID | 控制理论 |
| 运动控制 | 高速计数、定位 | 运动控制器 |
| 通信 | Profinet IO、OPC UA | 工业网络 |
| 安全 | 安全PLC、功能安全 | 安全系统 |
| 冗余 | CPU冗余、通信冗余 | 高可用系统 |

### 13.4 项目实践建议

1. **从修改开始**：先修改现有代码，不要从头编写
2. **小步快跑**：每次只改一个功能，测试通过再继续
3. **善用仿真**：用PLCSIM仿真测试，不用真实设备
4. **记录问题**：遇到问题记录下来，形成知识库
5. **代码审查**：写完后检查自己的代码

---

## 附录：快速参考

### A. 常用代码片段

``` scl
// 延时
TON_Inst(IN := Start, PT := T#5S);
IF TON_Inst.Q THEN
    // 5秒后执行
END_IF;

// 定时器
TP_Inst(CLK := Trigger, PT := T#1S);
PulseOut := TP_Inst.Q;

// 计数器
CTU_Inst(CU := CountUp, PV := 10);
IF CTU_Inst.Q THEN
    // 计数达到10
END_IF;
```

### B. 数据转换

``` scl
// Int to Real
RealVal := INT_TO_REAL(IntVal);

// Real to Int (取整)
IntVal := REAL_TO_INT(RealVal);

// BCD to Int
IntVal := BCD_TO_INT(BCDVal);

// 字节数组到字符串
StringVal := BYTE_TO_STRING(ByteArray);
```

### C. 地址格式

```
DB块地址:
- DB100.DBD0   → Data Double Word (4字节)
- DB100.DBW0   → Data Word (2字节)
- DB100.DBB0   → Data Byte (1字节)
- DB100.DBX0.0 → Data Bit (1位)

I/O地址:
- IW100        → Input Word
- QW100        → Output Word
- IB100        → Input Byte
- QB100        → Output Byte
```

---

**文档信息**：

- 版本: v1.0
- 适用: 西门子 S7-1500 (TIA Portal V17)
- 最后更新: 2025-05-15
