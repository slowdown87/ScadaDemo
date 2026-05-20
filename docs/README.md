# 茶饮料生产线 - 文档体系总索引

> 文档版本: v1.0
> 更新日期: 2026-05-15
> 项目: 茶饮料生产线SCADA系统
> 架构: 配置驱动文档生成系统 (Single Source of Truth)

---

## 📁 文档目录结构

```
docs/
├── 00_Index/           # 索引文档
├── 01_Spec/            # 技术规格文档
├── 02_Arch/            # 架构文档
├── 03_Device/          # 设备文档
├── 04_Process/         # 工艺文档
├── 05_Product/         # 产品配方文档
├── 06_OM/              # 运维文档
├── 07_Engineering/     # 工程文档
├── 08_project_tutorial/ # 项目教程
├── 99_Reference/       # 参考资料
└── _generators/        # 文档生成器
```

---

## 🎯 核心概念：单一真相源

**设计理念**：所有核心配置数据存储在 YAML 配置文件中，文档由生成器自动产出。

```
┌─────────────────────────────────────────────────────────────────────┐
│              01_Spec/configs/*.yaml (配置真相源)                      │
│    system_config.yaml | process_recipe_templates.yaml | ...          │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    _generators/*.py (文档生成器)                      │
│    PLC架构生成器 | 监控点表生成器 | HMI规格生成器 | ...                │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    */auto/* (自动生成文档)                           │
│    *_auto.md | *_auto.xlsx | 文档索引清单_auto.md                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 文档分类

| 类型 | 目录 | 说明 | 编辑规则 |
|------|------|------|----------|
| **配置** | `*/configs/*.yaml` | 数据真相源 | 手动编辑，禁止自动覆盖 |
| **生成器** | `_generators/*.py` | 文档生成脚本 | 手动维护 |
| **自动文档** | `*/auto/*_auto.md` | 由生成器产出 | 不要手动编辑，会被覆盖 |
| **手动文档** | `*/manual/*.md` | 手动编写 | 直接编辑即可 |

---

## 📋 目录详细索引

### 00_Index - 索引文档

| 文件 | 说明 |
|------|------|
| [auto/文档索引清单_auto.md](./00_Index/auto/文档索引清单_auto.md) | 全项目文档索引（自动生成） |

### 01_Spec - 技术规格文档

**配置目录** (`configs/`)

| 配置文件 | 说明 | 真相源类型 |
|----------|------|-----------|
| [system_config.yaml](./01_Spec/configs/system_config.yaml) | 核心配置：设备、PLC、工段定义 | ★设备基础数据 |
| [process_recipe_templates.yaml](./01_Spec/configs/process_recipe_templates.yaml) | 工艺配方：清洗程序、CIP参数 | ★工艺详细数据 |
| [comm_templates.yaml](./01_Spec/configs/comm_templates.yaml) | 通讯配置：PLC通讯、网络设置 | ★通讯配置 |
| [hmi_config.yaml](./01_Spec/configs/hmi_config.yaml) | HMI配置：画面、控件定义 | HMI配置 |
| [fb_spec_config.yaml](./01_Spec/configs/fb_spec_config.yaml) | 功能块规格：FB/FC定义 | 功能块定义 |
| [product_recipe_templates.yaml](./01_Spec/configs/product_recipe_templates.yaml) | 产品配方模板 | 产品配方 |
| [cabinet_bom.yaml](./01_Spec/configs/cabinet_bom.yaml) | 电控柜BOM配置 | 工程BOM |
| [instrument_list.yaml](./01_Spec/configs/instrument_list.yaml) | 仪表清单配置 | 工程仪表 |
| [terminal_assignments.yaml](./01_Spec/configs/terminal_assignments.yaml) | 端子定义配置 | 工程端子 |
| [cable_list.yaml](./01_Spec/configs/cable_list.yaml) | 电缆清单配置 | 工程电缆 |
| [interlock_templates.yaml](./01_Spec/configs/interlock_templates.yaml) | 联锁模板 | 联锁逻辑 |

**自动生成** (`auto/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_SCADA功能规格_auto.md](./01_Spec/auto/茶饮料_SCADA功能规格_auto.md) | SCADA系统功能规格 |
| [茶饮料_HMI画面规格_auto.md](./01_Spec/auto/茶饮料_HMI画面规格_auto.md) | HMI画面规格 |

**手动文档** (`manual/`)

| 文件 | 说明 |
|------|------|
| [Section_Process_Template.md](./01_Spec/manual/Section_Process_Template.md) | 工段工艺模板 |
| [Section_Control_Template.md](./01_Spec/manual/Section_Control_Template.md) | 工段控制模板 |
| [Batch_Control_Spec.md](./01_Spec/manual/Batch_Control_Spec.md) | 批次控制规格 |
| [工程计算模板.md](./01_Spec/manual/工程计算模板.md) | 工程计算模板 |
| [P&ID管道仪表流程图规范.md](./01_Spec/manual/P&ID管道仪表流程图规范.md) | P&ID绘图规范 |

### 02_Arch - 架构文档

**自动生成** (`auto/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_PLC架构_auto.md](./02_Arch/auto/茶饮料_PLC架构_auto.md) | PLC系统架构 |
| [茶饮料_PLC功能块规格_auto.md](./02_Arch/auto/茶饮料_PLC功能块规格_auto.md) | PLC功能块规格 |
| [茶饮料_生产线工艺配置_auto.md](./02_Arch/auto/茶饮料_生产线工艺配置_auto.md) | 生产线工艺配置 |

**手动文档** (`manual/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_工艺设计说明.md](./02_Arch/manual/茶饮料_工艺设计说明.md) | 工艺设计说明 |

### 03_Device - 设备文档

**自动生成** (`auto/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_监控点表_auto.md](./03_Device/auto/茶饮料_监控点表_auto.md) | I/O监控点表 |
| [茶饮料_设备参数表_auto.md](./03_Device/auto/茶饮料_设备参数表_auto.md) | 设备参数表 |
| [茶饮料_位号编码规则_auto.md](./03_Device/auto/茶饮料_位号编码规则_auto.md) | 位号编码规则 |

**手动文档** (`manual/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_设备清单.md](./03_Device/manual/茶饮料_设备清单.md) | 设备清单 |
| [茶饮料_设备控制参数表.md](./03_Device/manual/茶饮料_设备控制参数表.md) | 设备控制参数 |

### 04_Process - 工艺文档

**自动生成** (`auto/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_通讯接口规格书_auto.md](./04_Process/auto/茶饮料_通讯接口规格书_auto.md) | 通讯接口规格 |
| [茶饮料_CIP清洗程序规格书_auto.md](./04_Process/auto/茶饮料_CIP清洗程序规格书_auto.md) | CIP清洗程序 |
| [茶饮料_联锁逻辑说明书_auto.md](./04_Process/auto/茶饮料_联锁逻辑说明书_auto.md) | 联锁逻辑 |
| [茶饮料_工艺配方_auto.md](./04_Process/auto/茶饮料_工艺配方_auto.md) | 工艺配方 |

**手动文档** (`manual/`) - 13个工段

| 工段 | 工艺说明 | 控制规格 |
|------|----------|----------|
| **CP** CIP清洗 | [CP_CIP清洗工段工艺说明.md](./04_Process/manual/CP_CIP清洗工段工艺说明.md) | [CP_控制规格.md](./04_Process/manual/CP_控制规格.md) |
| **WT** 水处理 | [WT_水处理工段工艺说明.md](./04_Process/manual/WT_水处理工段工艺说明.md) | [WT_水处理控制规格.md](./04_Process/manual/WT_水处理控制规格.md) |
| **TH** 茶叶前处理 | [TH_茶叶前处理工段工艺说明.md](./04_Process/manual/TH_茶叶前处理工段工艺说明.md) | [TH_茶叶前处理控制规格.md](./04_Process/manual/TH_茶叶前处理控制规格.md) |
| **EX** 萃取 | [EX_萃取工段工艺说明.md](./04_Process/manual/EX_萃取工段工艺说明.md) | [EX_萃取控制规格.md](./04_Process/manual/EX_萃取控制规格.md) |
| **BL** 调配 | [BL_调配工段工艺说明.md](./04_Process/manual/BL_调配工段工艺说明.md) | [BL_调配控制规格.md](./04_Process/manual/BL_调配控制规格.md) |
| **HM** 均质 | [HM_均质工段工艺说明.md](./04_Process/manual/HM_均质工段工艺说明.md) | [HM_均质控制规格.md](./04_Process/manual/HM_均质控制规格.md) |
| **FL** 过滤 | [FL_过滤工段工艺说明.md](./04_Process/manual/FL_过滤工段工艺说明.md) | [FL_过滤控制规格.md](./04_Process/manual/FL_过滤控制规格.md) |
| **UH** UHT杀菌 | [UH_UHT工段工艺说明.md](./04_Process/manual/UH_UHT工段工艺说明.md) | [UH_UHT控制规格.md](./04_Process/manual/UH_UHT控制规格.md) |
| **PF** 灌装 | [PF_灌装工段工艺说明.md](./04_Process/manual/PF_灌装工段工艺说明.md) | [PF_灌装控制规格.md](./04_Process/manual/PF_灌装控制规格.md) |
| **CG** 旋盖 | [CG_旋盖工段工艺说明.md](./04_Process/manual/CG_旋盖工段工艺说明.md) | [CG_旋盖控制规格.md](./04_Process/manual/CG_旋盖控制规格.md) |
| **LB** 贴标 | [LB_贴标工段工艺说明.md](./04_Process/manual/LB_贴标工段工艺说明.md) | [LB_贴标控制规格.md](./04_Process/manual/LB_贴标控制规格.md) |
| **PK** 膜包码垛 | [PK_膜包码垛工段工艺说明.md](./04_Process/manual/PK_膜包码垛工段工艺说明.md) | [PK_膜包码垛控制规格.md](./04_Process/manual/PK_膜包码垛控制规格.md) |
| **BF** 制瓶 | [BF_制瓶工段工艺说明.md](./04_Process/manual/BF_制瓶工段工艺说明.md) | [BF_制瓶控制规格.md](./04_Process/manual/BF_制瓶控制规格.md) |

**其他手动文档**

| 文件 | 说明 |
|------|------|
| [CI_喷码工段工艺说明.md](./04_Process/manual/CI_喷码工段工艺说明.md) | 喷码工艺 |
| [CI_喷码控制规格.md](./04_Process/manual/CI_喷码控制规格.md) | 喷码控制 |
| [CA_装箱工段工艺说明.md](./04_Process/manual/CA_装箱工段工艺说明.md) | 装箱工艺 |
| [CA_装箱控制规格.md](./04_Process/manual/CA_装箱控制规格.md) | 装箱控制 |
| [LI_灯检工段工艺说明.md](./04_Process/manual/LI_灯检工段工艺说明.md) | 灯检工艺 |
| [LI_灯检控制规格.md](./04_Process/manual/LI_灯检控制规格.md) | 灯检控制 |

### 05_Product - 产品配方文档

**自动生成** (`auto/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_产品配方表_auto.md](./05_Product/auto/茶饮料_产品配方表_auto.md) | 产品配方表 |
| [茶饮料_CIP配方表_auto.md](./05_Product/auto/茶饮料_CIP配方表_auto.md) | CIP清洗配方表 |

### 06_OM - 运维文档

**手动文档** (`manual/`)

| 文件 | 说明 |
|------|------|
| [操作手册.md](./06_OM/manual/操作手册.md) | 系统操作手册 |
| [调试大纲.md](./06_OM/manual/调试大纲.md) | 系统调试大纲 |
| [验收标准.md](./06_OM/manual/验收标准.md) | 系统验收标准 |
| [维护手册.md](./06_OM/manual/维护手册.md) | 系统维护手册 |
| [备件清单.md](./06_OM/manual/备件清单.md) | 备件清单 |
| [应急预案.md](./06_OM/manual/应急预案.md) | 应急预案 |
| [竣工文档清单.md](./06_OM/manual/竣工文档清单.md) | 竣工文档清单 |

### 07_Engineering - 工程文档

**自动生成** (`auto/`)

| 文件 | 说明 |
|------|------|
| [茶饮料_电控柜BOM清单_auto.xlsx](./07_Engineering/auto/茶饮料_电控柜BOM清单_auto.xlsx) | 电控柜BOM |
| [茶饮料_仪表清单_auto.xlsx](./07_Engineering/auto/茶饮料_仪表清单_auto.xlsx) | 仪表清单 |
| [茶饮料_端子定义表_auto.xlsx](./07_Engineering/auto/茶饮料_端子定义表_auto.xlsx) | 端子定义表 |
| [茶饮料_电缆清单_auto.xlsx](./07_Engineering/auto/茶饮料_电缆清单_auto.xlsx) | 电缆清单 |

### 08_project_tutorial - 项目教程

**手动文档** (`manual/`)

| 文件 | 说明 |
|------|------|
| [backend_tutorial.md](./08_project_tutorial/manual/backend_tutorial.md) | 后端开发教程 |
| [frontend_tutorial.md](./08_project_tutorial/manual/frontend_tutorial.md) | 前端开发教程 |
| [plc_tutorial.md](./08_project_tutorial/manual/plc_tutorial.md) | PLC编程零基础教程 |

### 99_Reference - 参考资料

| 目录 | 说明 |
|------|------|
| [PID_Reference/](./99_Reference/PID_Reference/) | P&ID管道仪表流程图参考资料 |

**参考文档**

| 文件 | 说明 |
|------|------|
| [ISA_5.1_符号速查表.md](./99_Reference/PID_Reference/ISA_5.1_符号速查表.md) | ISA-5.1仪表符号 |
| [P&ID_专业符号库.svg](./99_Reference/PID_Reference/P&ID_专业符号库.svg) | P&ID符号库 |
| [P&ID_专业标准对比分析.md](./99_Reference/PID_Reference/P&ID_专业标准对比分析.md) | P&ID标准对比 |
| [P&ID_流程图改进方案.md](./99_Reference/PID_Reference/P&ID_流程图改进方案.md) | P&ID改进方案 |
| [P&ID_对比分析图.svg](./99_Reference/PID_Reference/P&ID_对比分析图.svg) | P&ID对比图 |

### _generators - 文档生成器

| 生成器 | 输入配置 | 输出文档 |
|--------|----------|----------|
| [run_all_generators.py](./_generators/run_all_generators.py) | 所有配置 | 一键生成所有auto文档 |
| [plc_arch_generator.py](./_generators/plc_arch_generator.py) | system_config.yaml | PLC架构文档 |
| [fb_spec_generator.py](./_generators/fb_spec_generator.py) | fb_spec_config.yaml | PLC功能块规格 |
| [tag_code_generator.py](./_generators/tag_code_generator.py) | system_config.yaml | 位号编码规则 |
| [device_param_generator.py](./_generators/device_param_generator.py) | system_config.yaml | 设备参数表 |
| [monitor_point_generator.py](./_generators/monitor_point_generator.py) | system_config.yaml | 监控点表 |
| [scada_spec_generator.py](./_generators/scada_spec_generator.py) | system_config.yaml | SCADA功能规格 |
| [hmi_generator.py](./_generators/hmi_generator.py) | hmi_config.yaml | HMI画面规格 |
| [comm_spec_generator.py](./_generators/comm_spec_generator.py) | comm_templates.yaml | 通讯接口规格 |
| [process_recipe_generator.py](./_generators/process_recipe_generator.py) | process_recipe_templates.yaml | 工艺配方 |
| [cip_spec_generator.py](./_generators/cip_spec_generator.py) | process_recipe_templates.yaml | CIP清洗程序 |
| [cip_recipe_generator.py](./_generators/cip_recipe_generator.py) | process_recipe_templates.yaml | CIP配方表 |
| [product_recipe_generator.py](./_generators/product_recipe_generator.py) | product_recipe_templates.yaml | 产品配方表 |
| [interlock_generator.py](./_generators/interlock_generator.py) | system_config.yaml | 联锁逻辑 |
| [engineering_generator.py](./_generators/engineering_generator.py) | cabinet_bom.yaml等 | 工程BOM清单 |
| [index_generator.py](./_generators/index_generator.py) | index_config.yaml | 文档索引清单 |
| [process_flow_generator.py](./_generators/process_flow_generator.py) | system_config.yaml | 生产线工艺配置 |
| [template_validator.py](./_generators/template_validator.py) | - | 模板验证工具 |

---

## 🚀 快速使用指南

### 运行所有文档生成器

```bash
cd docs/_generators
python run_all_generators.py
```

### 运行指定生成器

```bash
python run_all_generators.py --gen=PLC_Arch    # PLC架构
python run_all_generators.py --gen=HMI_Spec     # HMI规格
python run_all_generators.py --gen=CIP_Spec     # CIP程序
```

### 列出所有生成器

```bash
python run_all_generators.py --list
```

### 修改配置后重新生成

```
1. 编辑配置: 01_Spec/configs/system_config.yaml
2. 运行生成: python run_all_generators.py
3. 检查结果: */auto/*_auto.md
4. 提交配置: 仅提交 configs/ 目录
```

---

## 📊 配置真相源层级

```
┌─────────────────────────────────────────────────────────────────┐
│                      核心真相源 (01_Spec/configs/)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ★ system_config.yaml           - 设备、PLC、工段定义             │
│  ★ process_recipe_templates.yaml - 工艺参数、CIP程序              │
│  ★ comm_templates.yaml          - 通讯配置                        │
│    hmi_config.yaml              - HMI画面配置                    │
│    fb_spec_config.yaml           - 功能块规格                     │
│    product_recipe_templates.yaml - 产品配方                       │
│    cabinet_bom.yaml             - 电控柜BOM                      │
│    instrument_list.yaml         - 仪表清单                       │
│    terminal_assignments.yaml    - 端子定义                       │
│    cable_list.yaml              - 电缆清单                       │
│    interlock_templates.yaml     - 联锁逻辑                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      自动生成文档 (*/auto/)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  02_Arch/auto/          PLC架构 | 功能块规格 | 工艺配置           │
│  03_Device/auto/        监控点表 | 设备参数 | 位号编码            │
│  04_Process/auto/       通讯接口 | CIP程序 | 联锁逻辑 | 工艺配方   │
│  05_Product/auto/       产品配方 | CIP配方                       │
│  07_Engineering/auto/   BOM清单 | 仪表清单 | 端子定义 | 电缆清单  │
│  00_Index/auto/         文档索引清单                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📈 文档统计

| 目录 | auto文档 | manual文档 | 配置文件 |
|------|----------|------------|----------|
| 00_Index | 1 | 0 | 1 |
| 01_Spec | 2 | 5 | 11 |
| 02_Arch | 3 | 1 | 0 |
| 03_Device | 3 | 2 | 0 |
| 04_Process | 4 | 26 | 0 |
| 05_Product | 2 | 0 | 0 |
| 06_OM | 0 | 7 | 0 |
| 07_Engineering | 4 | 0 | 0 |
| 08_project_tutorial | 0 | 3 | 0 |
| 99_Reference | 0 | 3 | 0 |
| **合计** | **19** | **45** | **12** |

---

## 🔧 维护规则

### 核心配置修改流程

1. 编辑 `01_Spec/configs/system_config.yaml`（设备基础数据）
2. 编辑 `01_Spec/configs/process_recipe_templates.yaml`（工艺详细数据）
3. 运行 `python _generators/run_all_generators.py`
4. 检查生成的 `*/auto/` 目录文档
5. **仅提交 `configs/` 目录**（auto文档由生成器产出）

### 手动文档修改

- 直接编辑 `*/manual/*.md` 文件
- 不要编辑 `*/auto/*_auto.md` 文件，会被覆盖

### 版本更新规则

| 文档类型 | 更新触发 | 版本规则 |
|----------|----------|----------|
| system_config.yaml | 修改后 | v1.2 → v1.3 |
| process_recipe_templates.yaml | 修改后 | v1.1 → v1.2 |
| auto生成文档 | 重新生成后 | 自动更新日期 |
| 手动文档 | 内容重大变更 | v1.0 → v2.0 |
| 工段控制规格 | 控制逻辑变更 | v1.0 → v1.1 |

---

**最后更新**: 2026-05-15
**维护者**: 项目组
**版本**: v1.0
