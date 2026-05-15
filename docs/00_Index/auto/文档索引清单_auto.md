# 文档索引清单
> 文档版本: vv4.1> 创建日期: 2026-04-30> 更新日期: 2026-05-14> 项目名称: 茶饮料生产线文档体系> **自动生成**: 本文档由 index_generator.py 自动生成
---
## 📁 文档目录结构

```
docs/
│
├── 00_Index/                          ← 索引文档
│   └── auto/
│       └── 文档索引清单_auto.md
├── 01_Spec/                          ← 规格文档
│   └── auto/
│       ├── 茶饮料_HMI画面规格_auto.md
│       ├── 茶饮料_SCADA功能规格_auto.md
│   └── manual/
│       ├── Batch_Control_Spec.md
│       ├── P&ID管道仪表流程图规范.md
│       ├── Section_Control_Template.md
│       ├── Section_Process_Template.md
│       ├── 工程计算模板.md
│   └── configs/
│       ├── cabinet_bom.yaml
│       ├── cable_list.yaml
│       ├── comm_templates.yaml
│       ├── fb_spec_config.yaml
│       ├── hmi_config.yaml
│       ├── index_config.yaml
│       ├── instrument_list.yaml
│       ├── interlock_templates.yaml
│       ├── process_recipe_templates.yaml
│       ├── product_recipe_templates.yaml
│       ├── system_config.yaml
│       └── terminal_assignments.yaml
├── 02_Arch/                          ← 架构文档
│   └── auto/
│       ├── 茶饮料_PLC功能块规格_auto.md
│       ├── 茶饮料_PLC架构_auto.md
│       ├── 茶饮料_生产线工艺配置_auto.md
│   └── manual/
│       └── 茶饮料_工艺设计说明.md
├── 03_Device/                          ← 设备文档
│   └── auto/
│       ├── 茶饮料_位号编码规则_auto.md
│       ├── 茶饮料_监控点表_auto.md
│       ├── 茶饮料_设备参数表_auto.md
│   └── manual/
│       ├── 茶饮料_设备控制参数表.md
│       └── 茶饮料_设备清单.md
├── 04_Process/                          ← 工艺文档
│   └── auto/
│       ├── 茶饮料_CIP清洗程序规格书_auto.md
│       ├── 茶饮料_工艺配方_auto.md
│       ├── 茶饮料_联锁逻辑说明书_auto.md
│       ├── 茶饮料_通讯接口规格书_auto.md
│   └── manual/
│       ├── BF_制瓶工段工艺说明.md
│       ├── BF_制瓶控制规格.md
│       ├── BL_调配工段工艺说明.md
│       ├── BL_调配控制规格.md
│       ├── CA_装箱工段工艺说明.md
│       ├── CA_装箱控制规格.md
│       ├── CG_旋盖工段工艺说明.md
│       ├── CG_旋盖控制规格.md
│       ├── CI_喷码工段工艺说明.md
│       ├── CI_喷码控制规格.md
│       ├── CP_CIP清洗工段工艺说明.md
│       ├── CP_控制规格.md
│       ├── EX_萃取工段工艺说明.md
│       ├── EX_萃取控制规格.md
│       ├── FL_过滤工段工艺说明.md
│       ├── FL_过滤控制规格.md
│       ├── HM_均质工段工艺说明.md
│       ├── HM_均质控制规格.md
│       ├── LB_贴标工段工艺说明.md
│       ├── LB_贴标控制规格.md
│       ├── LI_灯检工段工艺说明.md
│       ├── LI_灯检控制规格.md
│       ├── PF_灌装工段工艺说明.md
│       ├── PF_灌装控制规格.md
│       ├── PK_膜包码垛工段工艺说明.md
│       ├── PK_膜包码垛控制规格.md
│       ├── TH_茶叶前处理工段工艺说明.md
│       ├── TH_茶叶前处理控制规格.md
│       ├── UH_UHT工段工艺说明.md
│       ├── UH_UHT控制规格.md
│       ├── WT_水处理工段工艺说明.md
│       └── WT_水处理控制规格.md
├── 05_Product/                          ← 产品文档
│   └── auto/
│       ├── 茶饮料_CIP配方表_auto.md
│       └── 茶饮料_产品配方表_auto.md
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
│       ├── 茶饮料_仪表清单_auto.xlsx
│       ├── 茶饮料_电控柜BOM清单_auto.xlsx
│       ├── 茶饮料_电缆清单_auto.xlsx
│       └── 茶饮料_端子定义表_auto.xlsx
├── 08_project_tutorial/                          ← 教程文档
│   └── manual/
│       └── backend_tutorial.md
│
├── _generators/                        ← ★统一生成器目录
│   ├── cip_recipe_generator.py
│   ├── cip_spec_generator.py
│   ├── comm_spec_generator.py
│   ├── device_param_generator.py
│   ├── engineering_generator.py
│   ├── fb_spec_generator.py
│   ├── hmi_generator.py
│   ├── index_generator.py
│   ├── interlock_generator.py
│   ├── monitor_point_generator.py
│   ├── plc_arch_generator.py
│   ├── process_flow_generator.py
│   ├── process_recipe_generator.py
│   ├── product_recipe_generator.py
│   ├── run_all_generators.py
│   ├── scada_spec_generator.py
│   ├── tag_code_generator.py
│   └── template_validator.py
│
└── README.md
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
| 08_project_tutorial | 教程文档 | 项目开发教程、学习指南 | 手动 |

## 📄 文档清单（按编辑方式分类）

### 00_Index 索引文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 文档索引清单_auto.md | v- | 2026-05-14 |  |

---

### 01_Spec 规格文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_HMI画面规格_auto.md | v2.0 | 2026-05-12 |  |
| 茶饮料_SCADA功能规格_auto.md | v1.0 | 2026-05-12 |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| Batch_Control_Spec.md | v1.0 | - |  |
| P&ID管道仪表流程图规范.md | v1.0 | - |  |
| Section_Control_Template.md | v1.0 | - |  |
| Section_Process_Template.md | v1.0 | - |  |
| 工程计算模板.md | v1.0 | - |  |

---

### 02_Arch 架构文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_PLC功能块规格_auto.md | v1.0 | 2026-05-06 |  |
| 茶饮料_PLC架构_auto.md | v1.0 | 2026-05-12 |  |
| 茶饮料_生产线工艺配置_auto.md | v1.0 | 2026-05-12 |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_工艺设计说明.md | v2.0 | 2026-04-30 |  |

---

### 03_Device 设备文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_位号编码规则_auto.md | v3.0 | 2026-05-12 |  |
| 茶饮料_监控点表_auto.md | v1.0 | 2026-05-12 |  |
| 茶饮料_设备参数表_auto.md | v1.0 | 2026-05-12 |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_设备控制参数表.md | v1.0 | - |  |
| 茶饮料_设备清单.md | v3.0 | 2026-05-06 |  |

---

### 04_Process 工艺文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_CIP清洗程序规格书_auto.md | v1.0 | 2026-05-12 |  |
| 茶饮料_工艺配方_auto.md | v1.0 | 2026-05-12 |  |
| 茶饮料_联锁逻辑说明书_auto.md | v1.0 | 2026-05-12 |  |
| 茶饮料_通讯接口规格书_auto.md | v2.0 | 2026-05-12 |  |

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| BF_制瓶工段工艺说明.md | v1.0 | - |  |
| BF_制瓶控制规格.md | v1.0 | - |  |
| BL_调配工段工艺说明.md | v1.0 | - |  |
| BL_调配控制规格.md | v1.0 | - |  |
| CA_装箱工段工艺说明.md | v1.0 | - |  |
| CA_装箱控制规格.md | v1.0 | - |  |
| CG_旋盖工段工艺说明.md | v1.0 | - |  |
| CG_旋盖控制规格.md | v1.0 | - |  |
| CI_喷码工段工艺说明.md | v1.0 | - |  |
| CI_喷码控制规格.md | v1.0 | - |  |
| CP_CIP清洗工段工艺说明.md | v1.1 | 2026-05-13 |  |
| CP_控制规格.md | v1.0 | - |  |
| EX_萃取工段工艺说明.md | v1.0 | - |  |
| EX_萃取控制规格.md | v1.0 | - |  |
| FL_过滤工段工艺说明.md | v1.0 | - |  |
| FL_过滤控制规格.md | v1.0 | - |  |
| HM_均质工段工艺说明.md | v1.0 | - |  |
| HM_均质控制规格.md | v1.0 | - |  |
| LB_贴标工段工艺说明.md | v1.0 | - |  |
| LB_贴标控制规格.md | v1.0 | - |  |
| LI_灯检工段工艺说明.md | v1.0 | - |  |
| LI_灯检控制规格.md | v1.0 | - |  |
| PF_灌装工段工艺说明.md | v1.0 | - |  |
| PF_灌装控制规格.md | v1.0 | - |  |
| PK_膜包码垛工段工艺说明.md | v1.0 | - |  |
| PK_膜包码垛控制规格.md | v1.0 | - |  |
| TH_茶叶前处理工段工艺说明.md | v1.0 | - |  |
| TH_茶叶前处理控制规格.md | v2.0 | - |  |
| UH_UHT工段工艺说明.md | v1.0 | - |  |
| UH_UHT控制规格.md | v1.0 | - |  |
| WT_水处理工段工艺说明.md | v1.0 | - |  |
| WT_水处理控制规格.md | v2.0 | - |  |

---

### 05_Product 产品文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_CIP配方表_auto.md | v1.0 | 2026-05-12 |  |
| 茶饮料_产品配方表_auto.md | v1.0 | 2026-05-12 |  |

---

### 06_OM 运维文档

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 备件清单.md | v1.1 | 2026-05-12 |  |
| 应急预案.md | v1.0 | - |  |
| 操作手册.md | v1.1 | 2026-05-12 |  |
| 竣工文档清单.md | v1.1 | 2026-05-12 |  |
| 维护手册.md | v1.1 | 2026-05-12 |  |
| 调试大纲.md | v1.0 | - |  |
| 验收标准.md | v1.1 | 2026-05-12 |  |

---

### 07_Engineering 工程文档

#### 🔧 自动生成文档 (auto/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| 茶饮料_仪表清单_auto.xlsx | v- | - |  |
| 茶饮料_电控柜BOM清单_auto.xlsx | v- | - |  |
| 茶饮料_电缆清单_auto.xlsx | v- | - |  |
| 茶饮料_端子定义表_auto.xlsx | v- | - |  |

---

### 08_project_tutorial 教程文档

#### ✏️ 手动编辑文档 (manual/)

| 文档 | 版本 | 更新日期 | 说明 |
| ---- | ---- | -------- | ---- |
| backend_tutorial.md | v- | - |  |

---
## 📊 文档依赖关系矩阵

| 文档 | 依赖文档 | 说明 |
| ---- | -------- | ---- |
| **02_Arch/auto/PLC_Architecture_auto.md** | 01_Spec/configs/system_config.yaml | 设备基础数据真相源 |
| **03_Device/auto/位号编码规则_auto.md** | 01_Spec/configs/system_config.yaml | 设备基础数据真相源 |
| **03_Device/auto/设备参数表_auto.md** | 01_Spec/configs/system_config.yaml | 设备基础数据真相源 |
| **03_Device/auto/茶饮料生产线监控点表_auto.md** | 03_Device/configs/devices_*.yaml | 设备清单 |
| <br /> | 03_Device/configs/sensor_templates.yaml | 传感器定义 |
| **04_Process/auto/茶饮料_通讯接口规格书_auto.md** | 01_Spec/configs/comm_templates.yaml | 通讯配置真相源 |
| <br /> | 01_Spec/configs/system_config.yaml | PLC定义 |
| **04_Process/auto/茶饮料_CIP清洗程序规格书_auto.md** | 01_Spec/configs/process_recipe_templates.yaml | 工艺详细数据真相源 |
| **工段控制规格 (各工段)** | 01_Spec/configs/system_config.yaml | PLC/工段定义 |
| <br /> | 03_Device/configs/devices_*.yaml | 设备定义 |
| <br /> | 03_Device/auto/位号编码规则_auto.md | 位号命名 |

## 🔗 生成器与输出文件对照表

| 生成器 | 输入 | 输出 | 用途 |
| ------ | ---- | ---- | ---- |
| _generators/plc_arch_generator.py | 01_Spec/configs/system_config.yaml | 02_Arch/auto/PLC_Architecture_auto.md | PLC架构文档 |
| _generators/tag_code_generator.py | 01_Spec/configs/system_config.yaml | 03_Device/auto/位号编码规则_auto.md | 位号编码规则 |
| _generators/device_param_generator.py | 01_Spec/configs/system_config.yaml | 03_Device/auto/设备参数表_auto.md | 设备参数表 |
| _generators/run_all_generators.py | 01_Spec/configs/system_config.yaml<br>01_Spec/configs/comm_templates.yaml<br>01_Spec/configs/process_recipe_templates.yaml | 多个auto文档 | 一键运行所有核心生成器 |
| _generators/monitor_point_generator.py | 01_Spec/configs/system_config.yaml | 03_Device/auto/茶饮料_监控点表_auto.md | SCADA点位配置 |
| _generators/comm_spec_generator.py | 01_Spec/configs/comm_templates.yaml | 04_Process/auto/茶饮料_通讯接口规格书_auto.md | PLC通讯配置 |
| _generators/process_recipe_generator.py | 01_Spec/configs/process_recipe_templates.yaml | 04_Process/auto/茶饮料_工艺配方_auto.md | 工艺参数 |
| _generators/cip_spec_generator.py | 01_Spec/configs/process_recipe_templates.yaml | 04_Process/auto/茶饮料_CIP清洗程序规格书_auto.md | CIP清洗程序规格 |
| _generators/product_recipe_generator.py | 01_Spec/configs/product_recipe_templates.yaml | 05_Product/auto/茶饮料_产品配方表_auto.md | 产品规格 |
| _generators/cip_recipe_generator.py | 01_Spec/configs/process_recipe_templates.yaml | 05_Product/auto/茶饮料_CIP配方表_auto.md | CIP清洗剂配方 |
| _generators/engineering_generator.py | 01_Spec/configs/cabinet_bom.yaml<br>01_Spec/configs/instrument_list.yaml<br>01_Spec/configs/terminal_assignments.yaml<br>01_Spec/configs/cable_list.yaml<br>01_Spec/configs/system_config.yaml | 07_Engineering/auto/茶饮料_电控柜BOM清单_auto.xlsx<br>07_Engineering/auto/茶饮料_仪表清单_auto.xlsx<br>07_Engineering/auto/茶饮料_端子定义表_auto.xlsx<br>07_Engineering/auto/茶饮料_电缆清单_auto.xlsx | 工程BOM |
| _generators/index_generator.py | 01_Spec/configs/index_config.yaml | 00_Index/auto/文档索引清单_auto.md | 文档索引 |

## ⚙️ 维护规则

### 1. 核心配置修改流程

1. 编辑 01_Spec/configs/system_config.yaml (设备基础数据)

2. 编辑 01_Spec/configs/process_recipe_templates.yaml (工艺详细数据)

3. 运行 _generators/run_all_generators.py

4. 检查生成的 auto/ 目录文档

5. 提交 configs/ 目录



### 2. 设备配置修改流程

1. 编辑 01_Spec/configs/system_config.yaml (设备基础数据)

2. 运行 _generators/run_all_generators.py

3. 检查生成的 03_Device/auto/ 文档



### 3. 手动文档修改

工段控制规格文档 (*_控制规格.md) 在对应模块的 manual/ 目录

直接编辑对应文档即可

不要编辑 auto/ 目录下的文件，会被覆盖



### 4. 版本更新规则

| 文档类型 | 更新时机 | 版本号规则 |
| ---- | ------ | ----------- |
| system_config.yaml | 修改后 | v1.2 → v1.3 |
| process_recipe_templates.yaml | 修改后 | v1.1 → v1.2 |
| auto生成文档 | 重新生成后 | 自动更新日期 |
| 手动文档 | 内容重大变更 | v1.0 → v2.0 |
| 工段控制规格 | 控制逻辑变更 | v1.0 → v1.1 |

---

**文档状态**: 自动生成

**生成时间**: 2026-05-14

**版本历史**:

- vv1.0 (2026-04-29): 初始版本
- vv2.0 (2026-04-29): 补充新增工段控制规格文档，完善文档关系图和数据流向图
- vv2.1 (2026-04-29): 拆分devices.yaml为14个设备配置文件，更新设备清单
- vv2.2 (2026-04-30): 更新PLC_Architecture.md为基准架构文档，comm_templates.yaml IP段更新为192.168.2.x
- vv2.3 (2026-04-30): 索引清单改由index_generator.py自动生成
- vv3.0 (2026-05-06): 重大更新：新增核心配置系统(system_config.yaml)，实现单一真相源
- vv4.0 (2026-05-06): 新增 auto/manual 子目录分类，区分自动生成和手动编辑文档
- vv4.1 (2026-05-07): 配置文件重构：分离设备基础数据(system_config.yaml)和工艺详细数据(process_recipe_templates.yaml)，修复BL pH/Brix数据冲突
- vv4.2 (2026-05-14): 新增08_project_tutorial目录，支持项目教程文档索引