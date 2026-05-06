# 文档索引清单
> 文档版本: vv4.0> 创建日期: 2026-04-30> 更新日期: 2026-05-06> 项目名称: 茶饮料生产线文档体系> **自动生成**: 本文档由 index_generator.py 自动生成
---
## 📁 文档目录结构

```
docs/
│
├── 00_Index/
│   ├── 文档索引清单.md              ← 本文档
│   ├── _generators/
│   │   └── index_generator.py
│   └── configs/
│       └── index_config.yaml
│
├── 项目文档综合改进规划方案.md      ← 项目规划
├── 状态快照.json
│
├── 00_Index/                          ← 索引文档
│   └── auto/
│       ├── 文档索引清单_auto.md
│   └── configs/
│       └── index_config.yaml
├── 01_Spec/                          ← 规格文档
│   └── auto/
│       ├── HMI_Screens_auto.md
│       ├── SCADA系统功能规格说明书_auto.md
│   └── configs/
│       ├── hmi_screens_config.yaml
│       └── system_config.yaml
├── 02_Arch/                          ← 架构文档
│   └── auto/
│       ├── PLC_Architecture_auto.md
│       ├── PLC功能块规格说明书_auto.md
│       ├── 生产线工艺配置_auto.md
│   └── manual/
│       ├── 工艺设计说明.md
│       ├── 茶饮料生产线工艺流程设计.md
│   └── configs/
│       └── FB_Spec_Template.yaml
├── 03_Device/                          ← 设备文档
│   └── auto/
│       ├── 位号编码规则_auto.md
│       ├── 茶饮料生产线监控点表_auto.md
│       ├── 设备参数表_auto.md
│   └── manual/
│       ├── 位号编码规则.md
│       ├── 茶饮料生产线设备清单.md
│       ├── 设备控制参数表.md
│   └── configs/
│       ├── devices_bf.yaml
│       ├── devices_bl.yaml
│       ├── devices_ci.yaml
│       ├── devices_cp.yaml
│       ├── devices_ex.yaml
│       ├── devices_fl.yaml
│       ├── devices_hm.yaml
│       ├── devices_index.yaml
│       ├── devices_lb_ca.yaml
│       ├── devices_li.yaml
│       ├── devices_meta.yaml
│       ├── devices_pf_cg.yaml
│       ├── devices_pk.yaml
│       ├── devices_th.yaml
│       ├── devices_uh.yaml
│       ├── devices_wt.yaml
│       └── sensor_templates.yaml
├── 04_Process/                          ← 工艺文档
│   └── BF_制瓶控制规格.md
│   └── BL_调配工段工艺说明.md
│   └── BL_调配控制规格.md
│   └── CA_装箱控制规格.md
│   └── CG_旋盖控制规格.md
│   └── CI_喷码控制规格.md
│   └── EX_萃取工段工艺说明.md
│   └── EX_萃取控制规格.md
│   └── FL_过滤控制规格.md
│   └── HM_均质控制规格.md
│   └── LB_贴标控制规格.md
│   └── LI_灯检控制规格.md
│   └── PF_灌装控制规格.md
│   └── PK_膜包码垛控制规格.md
│   └── TH_茶叶前处理工段工艺说明.md
│   └── TH_茶叶前处理控制规格.md
│   └── UH_UHT控制规格.md
│   └── WT_水处理工段工艺说明.md
│   └── WT_水处理控制规格.md
│   └── auto/
│       ├── CIP清洗程序规格书_auto.md
│       ├── 工艺配方_auto.md
│       ├── 联锁逻辑说明书_auto.md
│       ├── 通讯接口规格书_auto.md
│   └── manual/
│       ├── Batch_Control_Spec.md
│       ├── CP_控制规格.md
│       ├── P&ID管道仪表流程图规范.md
│       ├── Section_Process_Template.md
│   └── configs/
│       ├── Section_Control_Template.md
│       ├── cip_templates.yaml
│       ├── comm_templates.yaml
│       ├── interlock_templates.yaml
│       └── process_recipe_templates.yaml
├── 05_Product/                          ← 产品文档
│   └── CIP配方_auto.md
│   └── auto/
│       ├── CIP配方_auto.md
│       ├── 产品配方_auto.md
│   └── configs/
│       ├── cip_recipe_templates.yaml
│       └── product_recipe_templates.yaml
├── 06_OM/                          ← 运维文档
│   └── manual/
│       ├── 备件清单.md
│       ├── 应急预案.md
│       ├── 操作手册.md
│       ├── 竣工文档清单.md
│       ├── 维护手册.md
│       ├── 调试大纲.md
│       └── 验收标准.md
├── 07_Engineering/                          ← 工程文档
│   └── auto/
│       ├── Cabinet_BOM_auto.xlsx
│       ├── Cable_List_auto.xlsx
│       ├── Instrument_List_auto.xlsx
│       ├── Terminal_Assignments_auto.xlsx
│   └── manual/
│       ├── 工程计算模板.md
│   └── configs/
│       ├── cabinet_bom.yaml
│       ├── cable_list.yaml
│       ├── instrument_list.yaml
│       └── terminal_assignments.yaml
│
└── configs/                              ← ★核心配置系统
    ├── system_config.yaml           ← ★单一真相源
    ├── README.md
    └── generators/
        ├── PLC_Arch_generator.py
        ├── TagCode_generator.py
        ├── DeviceParam_generator.py
        └── run_all_generators.py
```
## 📋 文档分类说明

| 目录 | 文档类型 | 说明 | 编辑方式 |
| ---- | ---- | ------------------- | ------------ |
| 00_Index | 索引文档 | 文档清单、版本追踪 | 手动 |
| 01_Spec | 规格文档 | 系统/软件需求规格 | 手动（需求驱动） |
| 02_Arch | 架构文档 | 技术架构设计 | 手动+自动生成 |
| 03_Device | 设备文档 | 设备清单、位号定义 | 模板生成+手动 |
| 04_Process | 工艺文档 | 工艺参数、CIP、联锁、通讯、工段控制 | 工段控制手动，其他模板生成 |
| 05_Product | 产品文档 | 产品配方、CIP配方 | 模板生成 |
| 06_OM | 运维文档 | 调试、验收，维护、应急 | 手动 |
| 07_Engineering | 工程文档 | BOM、端子、电缆、仪表清单 | 模板生成+手动 |

## 📄 文档清单（按编辑方式分类）

### 00_Index 索引文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 文档索引清单_auto.md | v- | 2026-05-06 |  |

---

### 01_Spec 规格文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| HMI_Screens_auto.md | v2.0 | 2026-05-06 |  |
| SCADA系统功能规格说明书_auto.md | v1.0 | 2026-05-06 |  |

---

### 02_Arch 架构文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| PLC_Architecture_auto.md | v1.0 | 2026-05-06 |  |
| PLC功能块规格说明书_auto.md | v1.0 | 2026-05-06 |  |
| 生产线工艺配置_auto.md | v1.0 | 2026-05-06 |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 工艺设计说明.md | v2.0 | 2026-04-30 |  |
| 茶饮料生产线工艺流程设计.md | v2.0 | 2026-04-30 |  |

---

### 03_Device 设备文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 位号编码规则_auto.md | v3.0 | 2026-05-06 |  |
| 茶饮料生产线监控点表_auto.md | v1.0 | 2026-05-06 |  |
| 设备参数表_auto.md | v1.0 | 2026-05-06 |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 位号编码规则.md | v1.1 | 2026-04-30 |  |
| 茶饮料生产线设备清单.md | v2.0 | 2026-04-28 |  |
| 设备控制参数表.md | v1.0 | - |  |

---

### 04_Process 工艺文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| CIP清洗程序规格书_auto.md | v1.0 | 2026-04-28 |  |
| 工艺配方_auto.md | v1.0 | 2026-05-06 |  |
| 联锁逻辑说明书_auto.md | v1.1 | 2026-04-28 |  |
| 通讯接口规格书_auto.md | v2.0 | 2026-05-06 |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| Batch_Control_Spec.md | v1.0 | - |  |
| CP_控制规格.md | v1.0 | - |  |
| P&ID管道仪表流程图规范.md | v1.0 | - |  |
| Section_Process_Template.md | v1.0 | - |  |

| 其他文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| BF_制瓶控制规格.md | v1.0 | - |  |
| BL_调配工段工艺说明.md | v1.0 | - |  |
| BL_调配控制规格.md | v1.0 | - |  |
| CA_装箱控制规格.md | v1.0 | - |  |
| CG_旋盖控制规格.md | v1.0 | - |  |
| CI_喷码控制规格.md | v1.0 | - |  |
| EX_萃取工段工艺说明.md | v1.0 | - |  |
| EX_萃取控制规格.md | v1.0 | - |  |
| FL_过滤控制规格.md | v1.0 | - |  |
| HM_均质控制规格.md | v1.0 | - |  |
| LB_贴标控制规格.md | v1.0 | - |  |
| LI_灯检控制规格.md | v1.0 | - |  |
| PF_灌装控制规格.md | v1.0 | - |  |
| PK_膜包码垛控制规格.md | v1.0 | - |  |
| TH_茶叶前处理工段工艺说明.md | v1.0 | - |  |
| TH_茶叶前处理控制规格.md | v2.0 | - |  |
| UH_UHT控制规格.md | v1.0 | - |  |
| WT_水处理工段工艺说明.md | v1.0 | - |  |
| WT_水处理控制规格.md | v2.0 | - |  |

---

### 05_Product 产品文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| CIP配方_auto.md | v1.0 | 2026-04-30 |  |
| 产品配方_auto.md | v1.0 | 2026-05-06 |  |

| 其他文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| CIP配方_auto.md | v1.0 | 2026-05-06 |  |

---

### 06_OM 运维文档

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 备件清单.md | v1.0 | - |  |
| 应急预案.md | v1.0 | - |  |
| 操作手册.md | v1.0 | - |  |
| 竣工文档清单.md | v1.0 | - |  |
| 维护手册.md | v1.0 | - |  |
| 调试大纲.md | v1.0 | - |  |
| 验收标准.md | v1.0 | - |  |

---

### 07_Engineering 工程文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| Cabinet_BOM_auto.xlsx | v- | - |  |
| Cable_List_auto.xlsx | v- | - |  |
| Instrument_List_auto.xlsx | v- | - |  |
| Terminal_Assignments_auto.xlsx | v- | - |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 工程计算模板.md | v1.0 | - |  |

---
## 📊 文档依赖关系矩阵

| 文档 | 依赖文档 | 说明 |
| ---- | -------- | ---- |
| **02_Arch/auto/PLC_Architecture_auto.md** | configs/system_config.yaml | 单一真相源 |
| **03_Device/auto/位号编码规则_auto.md** | configs/system_config.yaml | 单一真相源 |
| **03_Device/auto/设备参数表_auto.md** | configs/system_config.yaml | 单一真相源 |
| **03_Device/auto/茶饮料生产线监控点表_auto.md** | 03_Device/configs/devices_*.yaml | 设备清单 |
| <br /> | 03_Device/configs/sensor_templates.yaml | 传感器定义 |
| **04_Process/auto/通讯接口规格书_auto.md** | 04_Process/configs/comm_templates.yaml | 通讯配置 |
| <br /> | configs/system_config.yaml | PLC定义 |
| **工段控制规格 (各工段)** | configs/system_config.yaml | PLC/工段定义 |
| <br /> | 03_Device/configs/devices_*.yaml | 设备定义 |
| <br /> | 03_Device/auto/位号编码规则_auto.md | 位号命名 |

## 🔗 生成器与输出文件对照表

| 生成器 | 输入 | 输出 | 用途 |
| ------ | ---- | ---- | ---- |
| configs/generators/PLC_Arch_generator.py | configs/system_config.yaml | 02_Arch/auto/PLC_Architecture_auto.md | PLC架构文档 |
| configs/generators/TagCode_generator.py | configs/system_config.yaml | 03_Device/auto/位号编码规则_auto.md | 位号编码规则 |
| configs/generators/DeviceParam_generator.py | configs/system_config.yaml | 03_Device/auto/设备参数表_auto.md | 设备参数表 |
| configs/generators/run_all_generators.py | configs/system_config.yaml | 多个auto文档 | 一键运行所有核心生成器 |
| 03_Device/_generators/monitor_point_generator.py | 03_Device/configs/devices_*.yaml<br>03_Device/configs/sensor_templates.yaml | 03_Device/auto/茶饮料生产线监控点表_auto.md | SCADA点位配置 |
| 04_Process/_generators/comm_spec_generator.py | 04_Process/configs/comm_templates.yaml | 04_Process/auto/通讯接口规格书_auto.md | PLC通讯配置 |
| 04_Process/_generators/process_recipe_generator.py | 04_Process/configs/process_recipe_templates.yaml | 04_Process/auto/工艺配方_auto.md | 工艺参数 |
| 05_Product/_generators/product_recipe_generator.py | 05_Product/configs/product_recipe_templates.yaml | 05_Product/auto/产品配方_auto.md | 产品规格 |
| 05_Product/_generators/cip_recipe_generator.py | 05_Product/configs/cip_recipe_templates.yaml | 05_Product/auto/CIP配方_auto.md | CIP清洗剂配方 |
| 07_Engineering/_generators/engineering_generator.py | 07_Engineering/configs/*.yaml | 07_Engineering/auto/Cabinet_BOM_auto.xlsx<br>07_Engineering/auto/Instrument_List_auto.xlsx<br>07_Engineering/auto/Terminal_Assignments_auto.xlsx<br>07_Engineering/auto/Cable_List_auto.xlsx | 工程BOM |
| 00_Index/_generators/index_generator.py | 00_Index/configs/index_config.yaml | 00_Index/文档索引清单.md | 文档索引 |

## ⚙️ 维护规则

### 1. 核心配置修改流程 (system_config.yaml)

1. 编辑 configs/system_config.yaml

2. 运行 configs/generators/run_all_generators.py

3. 检查生成的 02_Arch/auto/*.md 文档

4. 提交 configs/ 目录



### 2. 设备配置修改流程

1. 编辑 03_Device/configs/devices_*.yaml

2. 运行 03_Device/_generators/monitor_point_generator.py

3. 检查生成的 03_Device/auto/茶饮料生产线监控点表_auto.md



### 3. 手动文档修改

工段控制规格文档 (*_控制规格.md) 在对应模块的 manual/ 目录

直接编辑对应文档即可

不要编辑 auto/ 目录下的文件，会被覆盖



### 4. 版本更新规则

| 文档类型 | 更新时机 | 版本号规则 |
| ---- | ------ | ----------- |
| system_config.yaml | 修改后 | v1.0 → v1.1 |
| auto生成文档 | 重新生成后 | 自动更新日期 |
| 手动文档 | 内容重大变更 | v1.0 → v2.0 |
| 工段控制规格 | 控制逻辑变更 | v1.0 → v1.1 |

---

**文档状态**: 自动生成

**生成时间**: 2026-05-06

**版本历史**:

- vv1.0 (2026-04-29): 初始版本
- vv2.0 (2026-04-29): 补充新增工段控制规格文档，完善文档关系图和数据流向图
- vv2.1 (2026-04-29): 拆分devices.yaml为14个设备配置文件，更新设备清单
- vv2.2 (2026-04-30): 更新PLC_Architecture.md为基准架构文档，comm_templates.yaml IP段更新为192.168.2.x
- vv2.3 (2026-04-30): 索引清单改由index_generator.py自动生成
- vv3.0 (2026-05-06): 重大更新：新增核心配置系统(system_config.yaml)，实现单一真相源
- vv4.0 (2026-05-06): 新增 auto/manual 子目录分类，区分自动生成和手动编辑文档