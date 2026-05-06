# 配置驱动文档生成系统

> 文档版本: v1.0
> 创建日期: 2026-04-30
> 用途: 说明如何使用配置驱动文档生成系统

---

## 1. 系统概述

### 1.1 设计理念

**单一真相源 (Single Source of Truth)**：所有核心配置数据存储在 `configs/system_config.yaml` 中，其他文档（如PLC架构、位号编码规则、设备参数表）由此配置文件自动生成。

### 1.2 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    configs/system_config.yaml                     │
│                    (单一真相源 - 核心配置文件)                    │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐      ┌───────────────────┐      ┌─────────────────┐
│ PLC_Arch_     │      │  TagCode_         │      │ DeviceParam_    │
│ generator.py  │      │  generator.py     │      │ generator.py    │
└───────┬───────┘      └─────────┬─────────┘      └───────┬─────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────────┐      ┌─────────────────┐
│ PLC_Arch...   │      │ 位号编码规则_      │      │ 设备参数表_      │
│ _auto.md      │      │ auto.md           │      │ auto.md         │
└───────────────┘      └───────────────────┘      └─────────────────┘
```

### 1.3 配置文件清单

| 文件路径 | 说明 | 维护方式 |
|----------|------|----------|
| `configs/system_config.yaml` | 核心配置（单一真相源） | **手动编辑** |
| `configs/generators/*.py` | 文档生成器脚本 | 自动生成 |

### 1.4 生成文档清单

| 文档 | 生成器 | 输入 | 说明 |
|------|--------|------|------|
| `02_Arch/PLC_Architecture_auto.md` | PLC_Arch_generator.py | system_config.yaml | PLC架构文档 |
| `03_Device/位号编码规则_auto.md` | TagCode_generator.py | system_config.yaml | 位号编码规则 |
| `03_Device/设备参数表_auto.md` | DeviceParam_generator.py | system_config.yaml | 设备参数表 |

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
cd d:\TRAE_Project\ScadaDemo\.trae\docs\configs\generators
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
│    vi configs/system_config.yaml                            │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. 运行生成器                                                 │
│    python run_all_generators.py                             │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. 检查生成的文档                                             │
│    - 02_Arch/PLC_Architecture_auto.md                       │
│    - 03_Device/位号编码规则_auto.md                          │
│    - 03_Device/设备参数表_auto.md                            │
└──────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. 提交配置和生成器（不提交auto文件）                           │
│    git add configs/                                          │
│    git commit -m "更新系统配置"                               │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 注意事项

| 事项 | 说明 |
|------|------|
| **不要手动编辑auto文件** | 自动生成的文件每次运行会覆盖 |
| **修改入口是配置文件** | 要改内容，先改 system_config.yaml |
| **提交时不提交auto文件** | auto文件由生成器自动产生 |

---

## 4. system_config.yaml 结构

```yaml
meta:
  version: "v1.0"
  project_name: "茶饮料生产线SCADA系统"
  base_ip_subnet: "192.168.2.x"

plcs:                    # PLC定义
  PLC-1:
    name: "WT水处理"
    section: "WT"
    ip: "192.168.2.11"
    ...

sections:                # 工段定义
  WT:
    name: "水处理系统"
    prefix: "WT"
    number_range: [101, 199]
    plc: "PLC-1"
    ...

process_flow:            # 工艺流程
  liquid_line:
    sections: ["WT", "TH", "EX", ...]

high_speed_sync:         # 高速同步
  - from: "PLC-8"
    to: "PLC-9"
    period_ms: 10
    ...

plc_comm_matrix:         # PLC通讯矩阵
  - from: "PLC-1"
    to: "PLC-3"
    method: "PROFINET I-Device"
    ...
```

---

## 5. 扩展新生成器

如果要添加新的生成器，步骤如下：

1. **创建生成器脚本**

```python
# configs/generators/NewDoc_generator.py
import yaml
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "system_config.yaml"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "XX_NewDoc_auto.md"

def generate(config):
    # 从config生成文档
    return doc_content

if __name__ == "__main__":
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(generate(config))
```

2. **注册到 run_all_generators.py**

```python
GENERATORS = {
    # ... existing ...
    "NewDoc": {
        "script": "NewDoc_generator.py",
        "desc": "新文档",
        "output": "XX_NewDoc_auto.md",
        "input": "configs/system_config.yaml"
    },
}
```

---

## 6. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-04-30 | 初始版本 |

---

**维护说明**: 本文档本身是手动维护的，不受生成器影响。
