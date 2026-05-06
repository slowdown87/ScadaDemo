# 茶饮料生产线PLC架构设计

> 文档版本: v1.0
> 创建日期: 2026-04-30
> 更新日期: 2026-05-06
> 架构: **16个独立PLC分布式架构**(FL与HM分开)
>
> **本文件由系统配置自动生成 - 请勿手动修改**

---

## 重要声明

**本文档为茶饮料生产线的基准架构文档**,所有其他文档(通讯接口规格书,设备参数表,位号编码规则等)必须以此为准。

### 生成信息

| 项目 | 内容 |
| ---- | ---- |
| **数据来源** | `01_Spec/configs/system_config.yaml` |
| **生成器脚本** | `docs/_generators/PLC_Arch_generator.py` |
| **重新生成命令** | `python docs/_generators/run_all_generators.py` |

### 修改流程

1. 编辑 `01_Spec/configs/system_config.yaml`
2. 运行 `python docs/_generators/run_all_generators.py`
3. 检查生成的 `02_Arch/auto/PLC_Architecture_auto.md`

---

## 1. 系统架构

### 1.1 架构概述

| 项目 | 参数 |
|------|------|
| PLC数量 | **16个**(液料线7个+包装线8个+CIP 1个+备1个) |
| 控制系统 | 西门子S7-1500系列 |
| 通讯网络 | PROFINET(100Mbps)+ Industrial Ethernet |
| 冗余方式 | PLC冗余(CPU mirroring)+ 网络冗余(HRP环网) |
| 拓扑结构 | 设备层 -> 车间层 -> 监控层 |
| 产品类型 | 纯茶饮料（绿茶/红茶/乌龙茶）- 共线生产 |
| 产能 | 50000B/H (额定) / 54000B/H (最大) |

### 1.2 网络架构图

```
三层架构:

[监控层] SCADA主站(192.168.2.100) <-> SCADA备站(192.168.2.101)
     |
     | PROFINET
     |
[控制层] 核心交换机1(192.168.2.1) <-> 核心交换机2(192.168.2.2)
     |
     | H-Sync光纤环网
     |
[设备层]
  液料线: 192.168.2.11 WT水处理, 192.168.2.12 TH茶叶前处理, 192.168.2.13 EX萃取
         192.168.2.14 FL过滤, 192.168.2.15 BL调配, 192.168.2.16 HM均质, 192.168.2.17 UH UHT杀菌
  包装线: 192.168.2.18 BF制瓶, 192.168.2.19 PF灌装, 192.168.2.20 CG旋盖, 192.168.2.21 LI灯检, 192.168.2.22 CI喷码
         192.168.2.23 LB贴标, 192.168.2.24 CA装箱, 192.168.2.25 PK膜包码垛
  独立系统: 192.168.2.26 CP CIP清洗
```

### 1.3 工艺流程顺序与PLC分配

```
液料生产线:
WT -> TH -> EX -> FL -> BL -> HM -> UH
WT水处理  TH茶叶前处理  EX萃取  FL过滤  BL调配  HM均质  UH UHT杀菌

包装生产线:
BF -> PF -> CG -> LI -> CI -> LB -> CA -> PK
BF制瓶  PF灌装  CG旋盖  LI灯检  CI喷码  LB贴标  CA装箱  PK膜包码垛

独立系统:
CP (CIP清洗)
```

---

## 2. PLC配置

### 2.1 PLC配置表

| PLC编号 | 控制工段 | CPU型号 | 通讯接口 | 冗余方式 | I/O估算 | 备注 |
| ------ | --------- | ------------- | ---- | ---------- | ------ | --------- |
| WT | WT水处理 | Water Treatment | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~200点 | 公用工程 |
| TH | TH茶叶前处理 | Tea Handling | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~100点 | 防爆区域 |
| EX | EX萃取 | Extraction | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~180点 | 批次控制 |
| FL | FL过滤 | Filtration | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~120点 | 连续流程 |
| BL | BL调配 | Blending | CPU 1517-2 PN | 2×PN | H-Sync光纤环网 | ~200点 | 核心批次 |
| HM | HM均质 | Homogenization | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~80点 | 均质处理 |
| UH | UH UHT杀菌 | UHT Processing | CPU 1517-2 PN | 2×PN | H-Sync光纤环网 | ~220点 | **CCP关键** |
| BF | BF制瓶 | Bottle Forming | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~150点 | 高速同步 |
| PF | PF灌装 | Packaging Fill | CPU 1517-2 PN | 2×PN | H-Sync光纤环网 | ~180点 | **超高速** |
| CG | CG旋盖 | Capping | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~80点 | 跟随灌装 |
| LI | LI灯检 | Light Inspection | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~60点 | 检测设备 |
| CI | CI喷码 | Coding | CPU 1215C | 1×PN | 无 | ~40点 | 产品追溯 |
| LB | LB贴标 | Labeling | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~60点 | 中等速度 |
| CA | CA装箱 | Cartoning | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~80点 | 批量控制 |
| PK | PK膜包码垛 | Packing | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~120点 | 末端设备 |
| CP | CP CIP清洗 | Cleaning In Place | CPU 1515-2 PN | 2×PN | H-Sync光纤环网 | ~140点 | 独立系统 |

**I/O总计**: 约2050点(液料线1180点 + 包装线730点 + CIP140点)

### 2.2 IP地址规划表 (基于192.168.2.x)

> **IP段**: 192.168.2.x(备选段,避免与办公网络冲突)
> **网关**: 192.168.2.1
> **子网掩码**: 255.255.255.0

| PLC编号 | 控制工段 | IP地址 | 备注 |
|---------|----------|--------|------|
| WT | Water Treatment | 192.168.2.11 | 公用工程 |
| TH | Tea Handling | 192.168.2.12 | 防爆区域 |
| EX | Extraction | 192.168.2.13 | 批次控制 |
| FL | Filtration | 192.168.2.14 | 连续流程 |
| BL | Blending | 192.168.2.15 | 核心批次 |
| HM | Homogenization | 192.168.2.16 | 均质处理 |
| UH | UHT Processing | 192.168.2.17 | CCP关键 |
| BF | Bottle Forming | 192.168.2.18 | 高速同步 |
| PF | Packaging Fill | 192.168.2.19 | 超高速 |
| CG | Capping | 192.168.2.20 | 跟随灌装 |
| LI | Light Inspection | 192.168.2.21 | 检测设备 |
| CI | Coding | 192.168.2.22 | 产品追溯 |
| LB | Labeling | 192.168.2.23 | 中等速度 |
| CA | Cartoning | 192.168.2.24 | 批量控制 |
| PK | Packing | 192.168.2.25 | 末端设备 |
| CP | Cleaning In Place | 192.168.2.26 | 独立系统 |
| SCADA主服务器 | - | 192.168.2.100 | |
| SCADA备服务器 | - | 192.168.2.101 | |
| 工程师站 | - | 192.168.2.110 | |
| 核心交换机1 | - | 192.168.2.1 | 网关 |
| 核心交换机2 | - | 192.168.2.2 | 冗余 |

### 2.3 控制系统职责划分

| PLC | 工段名称 | 主要控制任务 | 上游接口 | 下游接口 | 关键控制点 |
| ------ | --------- | ----------------- | ------- | ------ | --------------- |
| WT水处理 | WT水处理 | 公用工程 | - | TH, EX | P1 |
| TH茶叶前处理 | TH茶叶前处理 | 防爆区域 | WT | EX | P1 |
| EX萃取 | EX萃取 | 批次控制 | WT, TH | FL | P1 |
| FL过滤 | FL过滤 | 连续流程 | EX | BL | P1 |
| BL调配 | BL调配 | 核心批次 | FL | HM | P1 |
| HM均质 | HM均质 | 均质处理 | BL | UH | P1 |
| UH UHT杀菌 | UH UHT杀菌 | CCP关键 | HM | BF, PF | CCP |
| BF制瓶 | BF制瓶 | 高速同步 | UH | PF | P1 |
| PF灌装 | PF灌装 | 超高速 | UH, BF | CG | P1 |
| CG旋盖 | CG旋盖 | 跟随灌装 | PF | LI | P1 |
| LI灯检 | LI灯检 | 检测设备 | CG | CI | P1 |
| CI喷码 | CI喷码 | 产品追溯 | LI | LB | P1 |
| LB贴标 | LB贴标 | 中等速度 | CI | CA | P1 |
| CA装箱 | CA装箱 | 批量控制 | LB | PK | P1 |
| PK膜包码垛 | PK膜包码垛 | 末端设备 | CA | - | P1 |
| CP CIP清洗 | CP CIP清洗 | 独立系统 | - | WT, TH, EX, FL, BL, HM, UH, BF, PF | P1 |

### 2.4 PLC选型说明

| CPU型号 | 应用PLC | 选型理由 |
| ------------- | ------------------------------ | --------------------- |
| CPU 1515-2 PN | WT水处理, TH茶叶前处理, EX萃取, FL过滤, HM均质, BF制瓶, CG旋盖, LI灯检, LB贴标, CA装箱, PK膜包码垛, CP CIP清洗 | 标准性能,满足一般控制需求 |
| CPU 1517-2 PN | BL调配, UH UHT杀菌, PF灌装 | 高性能处理能力,满足批次控制和高速同步需求 |
| CPU 1215C | CI喷码 | 入门级,喷码机通常自带PLC,仅需通讯对接 |

---

## 3. 程序架构

### 3.1 项目总体结构

```
SCADA_Project
+______________________________
|  |__ PLC_WT水处理_WT_WaterTreatment
|      |-- PLC_WT水处理_WT.config
|      |__ Program_WT水处理
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_TH茶叶前处理_TH_TeaHandling
|      |-- PLC_TH茶叶前处理_TH.config
|      |__ Program_TH茶叶前处理
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_EX萃取_EX_Extraction
|      |-- PLC_EX萃取_EX.config
|      |__ Program_EX萃取
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_FL过滤_FL_Filtration
|      |-- PLC_FL过滤_FL.config
|      |__ Program_FL过滤
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_BL调配_BL_Blending
|      |-- PLC_BL调配_BL.config
|      |__ Program_BL调配
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_HM均质_HM_Homogenization
|      |-- PLC_HM均质_HM.config
|      |__ Program_HM均质
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_UH UHT杀菌_UH_UHTProcessing
|      |-- PLC_UH UHT杀菌_UH.config
|      |__ Program_UH UHT杀菌
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_BF制瓶_BF_BottleForming
|      |-- PLC_BF制瓶_BF.config
|      |__ Program_BF制瓶
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_PF灌装_PF_PackagingFill
|      |-- PLC_PF灌装_PF.config
|      |__ Program_PF灌装
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_CG旋盖_CG_Capping
|      |-- PLC_CG旋盖_CG.config
|      |__ Program_CG旋盖
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_LI灯检_LI_LightInspection
|      |-- PLC_LI灯检_LI.config
|      |__ Program_LI灯检
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_CI喷码_CI_Coding
|      |-- PLC_CI喷码_CI.config
|      |__ Program_CI喷码
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_LB贴标_LB_Labeling
|      |-- PLC_LB贴标_LB.config
|      |__ Program_LB贴标
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_CA装箱_CA_Cartoning
|      |-- PLC_CA装箱_CA.config
|      |__ Program_CA装箱
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_PK膜包码垛_PK_Packing
|      |-- PLC_PK膜包码垛_PK.config
|      |__ Program_PK膜包码垛
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+______________________________
|  |__ PLC_CP CIP清洗_CP_CleaningInPlace
|      |-- PLC_CP CIP清洗_CP.config
|      |__ Program_CP CIP清洗
|          |-- OB1_Main
|          |-- OB100_StartUp
|          |__ Functions
+-- SCADA_Project.db
```

---

## 4. 高速同步与通讯

### 4.1 同步需求分析

| 高速同步对 | 同步周期 | 同步内容 | 精度要求 |
| ---------- | -------- | -------- | -------- |
| BF -> PF | **10ms** | 瓶速、瓶位 | +/-1ms |
| PF -> CG | **10ms** | 灌装完成、旋盖触发 | +/-1ms |
| CG -> LI | **50ms** | 产品计数 | +/-5ms |
| LI -> CI | **50ms** | 剔除信号 | +/-5ms |
| UH -> PF | **20ms** | 无菌料信号、速度主令 | +/-2ms |

### 4.2 PLC间通讯矩阵

| 发送方 | 接收方 | 通讯方式 | 数据内容 | 周期 | 说明 |
| ---------- | ---------- | -------------- | -------- | -------- | -------- |
| PLC-1 | PLC-3 | PROFINET I-Device | 纯水产水量 | 100ms | 调配用水 |
| PLC-2 | PLC-3 | PROFINET I-Device | 茶叶原料量 | 100ms | 批次计量 |
| PLC-3 | PLC-4 | PROFINET I-Device | 茶汁流量、温度、批次完成 | 50ms | 批次信号 |
| PLC-4 | PLC-5 | PROFINET I-Device | 过滤后流量、批次完成 | 50ms | 批次信号 |
| PLC-5 | PLC-6 | PROFINET I-Device | 调配液流量、批次完成 | 50ms | 批次信号 |
| PLC-6 | PLC-7 | PROFINET I-Device | 流量、压力、温度 | 20ms | 连续信号 |
| PLC-7 | PLC-9 | PROFINET I-Device | 无菌料信号、速度主令 | 10ms | 超高速 |
| PLC-8 | PLC-9 | PROFINET I-Device | 瓶速、瓶位 | 10ms | 高速同步 |
| PLC-9 | PLC-10 | PROFINET I-Device | 旋盖速度、扭矩设定 | 10ms | 同步控制 |
| PLC-10 | PLC-11 | PROFINET I-Device | 产品计数、合格信号 | 50ms | 检测触发 |
| PLC-11 | PLC-12 | PROFINET I-Device | 剔除信号 | 50ms | 不合格跳过 |
| PLC-12 | PLC-13 | PROFINET I-Device | 喷码内容、打印完成 | 50ms | 标签信息 |
| PLC-13 | PLC-14 | PROFINET I-Device | 产品计数 | 100ms | 装箱触发 |
| PLC-14 | PLC-15 | PROFINET I-Device | 纸箱计数 | 100ms | 码垛触发 |
| PLC-9 | PLC-1, PLC-2, PLC-3, PLC-4, PLC-5, PLC-6, PLC-7 | PROFINET I-Device | 急停/清洗请求 | 10ms | 安全联锁 |
| PLC-16 | ALL | PROFINET I-Device | CIP程序启动/完成 | 200ms | 清洗信号 |

---

## 5. 中断与时间控制

### 5.1 中断组织块配置

| OB | 类型 | 循环时间 | 应用PLC | 说明 |
| --- | -------------- | -------- | -------------- | ------------ |
| OB1 | Free Cycle | 100ms | ALL | 主程序循环 |
| OB30 | Cyclic Interrupt | 50ms | PLC-5, PLC-7, PLC-9 | 快速液位/温度控制 |
| OB32 | Cyclic Interrupt | 50ms | PLC-3, PLC-4, PLC-6, PLC-15 | 快速液位/温度控制 |
| OB34 | Cyclic Interrupt | 10ms | PLC-8, PLC-9, PLC-10 | 高速同步控制 |
| OB35 | Cyclic Interrupt | 100ms | PLC-1, PLC-2, PLC-11, PLC-12, PLC-13, PLC-14 | 标准控制 |
| OB80 | Time Error | - | PLC-7, PLC-9 | 同步超时处理 |
| OB82 | Diagnostic Interrupt | - | ALL | 诊断中断 |
| OB100 | Startup | - | ALL | 启动组织块 |

### 5.2 关键时序要求

| 工段 | 时间要求 | 说明 |
| ---- | -------- | ---- |
| UHT杀菌温度 | 10ms响应 | CCP关键控制点 |
| 灌装同步 | 1ms精度 | 72ms周期要求 |
| 旋盖扭矩 | 5ms响应 | 品质控制 |
| 瓶位同步 | 1ms精度 | 高速线同步 |

---

## 6. 版本记录

| 版本 | 日期 | 变更内容 |
| ------ | ------ | ---------- |
| v1.0 | 2026-04-30 | 初始版本,从system_config.yaml自动生成 |

---

**文档状态**: 自动生成
**生成时间**: 2026-05-06 15:02:16
**审核状态**: 待审核
**批准人**: -
