# 配置驱动文档生成系统

> 文档版本: v3.0
> 创建日期: 2026-04-30
> 更新日期: 2026-05-06
> 用途: 说明如何使用配置驱动文档生成系统

---

## 1. 系统概述

### 1.1 设计理念

**单一真相源 (Single Source of Truth)**：所有核心配置数据存储在 `01_Spec/configs/system_config.yaml` 中，其他文档（如PLC架构、位号编码规则、设备参数表）由此配置文件自动生成。

### 1.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│              01_Spec/configs/system_config.yaml                  │
│                    (单一真相源 - 核心配置文件)                       │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐      ┌───────────────────┐      ┌─────────────────┐
│ PLC_Arch_    │      │  TagCode_         │      │ DeviceParam_   │
│ generator.py  │      │  generator.py     │      │ generator.py   │
└───────┬───────┘      └─────────┬─────────┘      └───────┬─────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────────┐      ┌─────────────────┐
│ 02_Arch/     │      │ 03_Device/        │      │ 03_Device/     │
│ auto/         │      │ auto/             │      │ auto/          │
│ PLC_Arch...   │      │ 位号编码规则_      │      │ 设备参数表_     │
│ _auto.md      │      │ auto.md           │      │ auto.md        │
└───────────────┘      └───────────────────┘      └─────────────────┘
```

### 1.3 目录结构

```
docs/
├── 00_Index/                      ← 索引模块
│   ├── README.md                 ← 本文件
│   ├── configs/
│   │   └── index_config.yaml     ← 索引配置
│   ├── auto/                    ← ★自动生成文档
│   │   └── 文档索引清单_auto.md
│   └── _generators/
│       ├── index_generator.py
│       └── template_validator.py
│
├── 01_Spec/                       ← 技术规格模块
│   ├── configs/
│   │   └── system_config.yaml   ← ★核心配置（单一真相源）
│   ├── auto/                    ← ★自动生成文档
│   │   └── SCADA系统功能规格说明书_auto.md
│   └── _generators/             ← ★生成器目录
│       ├── PLC_Arch_generator.py
│       ├── TagCode_generator.py
│       ├── DeviceParam_generator.py
│       ├── SCADA_Spec_generator.py
│       └── run_all_generators.py
│
├── 02_Arch/
│   └── auto/                    ← 自动生成文档
│
├── 03_Device/
│   ├── configs/                 ← 设备配置
│   └── auto/                    ← 自动生成文档
│
└── ...
```

### 1.4 配置文件清单

| 文件路径 | 说明 | 维护方式 |
|----------|------|----------|
| `01_Spec/configs/system_config.yaml` | 核心配置（单一真相源） | **手动编辑** |
| `01_Spec/_generators/*.py` | 文档生成器脚本 | 自动维护 |
| `00_Index/configs/index_config.yaml` | 索引配置 | 手动编辑 |

---

## 2. 使用方法

### 2.1 运行环境

```bash
# 需要 Python 3.6+
python --version

# 需要 PyYAML
pip install pyyaml
```

### 2.2 运行所有生成器

```bash
cd docs/01_Spec/_generators
python run_all_generators.py
```

### 2.3 运行指定生成器

```bash
# 仅生成PLC架构文档
python run_all_generators.py --gen=PLC_Arch

# 仅生成位号编码规则
python run_all_generators.py --gen=TagCode

# 仅生成设备参数表
python run_all_generators.py --gen=DeviceParam
```

### 2.4 列出所有生成器

```bash
python run_all_generators.py --list
```

---

## 3. 修改流程

### 3.1 标准修改流程

```
┌──────────────────────────────────────────────────────────────┐
│ 1. 编辑配置文件                                              │
│    vi 01_Spec/configs/system_config.yaml                     │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. 运行生成器                                                │
│    python 01_Spec/_generators/run_all_generators.py         │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. 检查生成的文档                                            │
│    - 00_Index/auto/文档索引清单_auto.md                    │
│    - 01_Spec/auto/SCADA系统功能规格说明书_auto.md           │
│    - 02_Arch/auto/PLC_Architecture_auto.md                   │
│    - 03_Device/auto/位号编码规则_auto.md                    │
│    - 03_Device/auto/设备参数表_auto.md                      │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 注意事项

| 事项 | 说明 |
|------|------|
| **不要手动编辑auto文件** | 自动生成的文件每次运行会覆盖 |
| **修改入口是配置文件** | 要改内容，先改 system_config.yaml |
| **提交时不提交auto文件** | auto文件由生成器自动产生 |

---

## 4. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-04-30 | 初始版本 |
| v2.0 | 2026-05-06 | 目录重组，将configs移入00_Index/下 |
| v3.0 | 2026-05-06 | system_config.yaml移至01_Spec/，生成器统一放01_Spec/_generators/ |

---

**维护说明**: 本文档本身是手动维护的，不受生成器影响。
