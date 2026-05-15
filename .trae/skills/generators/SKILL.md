---
name: "generators"
description: "SCADA文档生成器技能。管理茶饮料生产线的文档自动生成，包括PLC架构、功能块规格、HMI画面、设备参数表、监控点表、配方、CIP程序等。激活场景：批量生成文档、生成特定模块文档、查看生成器状态。"
---

# SCADA 文档生成器技能

管理茶饮料生产线的文档自动生成系统。

## 生成器清单

| 生成器 | 脚本 | 输入配置 | 输出文档 |
|--------|------|----------|----------|
| **PLC架构** | `plc_arch_generator.py` | system_config.yaml | 02_Arch/茶饮料_PLC架构_auto.md |
| **功能块规格** | `fb_spec_generator.py` | fb_spec_config.yaml | 02_Arch/auto/茶饮料_PLC功能块规格_auto.md |
| **HMI画面规格** | `hmi_generator.py` | hmi_config.yaml | 01_Spec/auto/茶饮料_HMI画面规格_auto.md |
| **SCADA功能规格** | `scada_spec_generator.py` | system_config.yaml | 01_Spec/auto/茶饮料_SCADA功能规格_auto.md |
| **位号编码规则** | `tag_code_generator.py` | system_config.yaml | 03_Device/茶饮料_位号编码规则_auto.md |
| **设备参数表** | `device_param_generator.py` | system_config.yaml | 03_Device/茶饮料_设备参数表_auto.md |
| **监控点表** | `monitor_point_generator.py` | system_config.yaml | 03_Device/茶饮料_监控点表_auto.md |
| **联锁逻辑** | `interlock_generator.py` | system_config.yaml | 04_Process/auto/茶饮料_联锁逻辑说明书_auto.md |
| **通讯接口** | `comm_spec_generator.py` | comm_templates.yaml | 04_Process/auto/茶饮料_通讯接口规格书_auto.md |
| **工艺配方** | `process_recipe_generator.py` | process_recipe_templates.yaml | 04_Process/auto/茶饮料_工艺配方_auto.md |
| **CIP清洗程序** | `cip_spec_generator.py` | process_recipe_templates.yaml | 04_Process/auto/茶饮料_CIP清洗程序规格书_auto.md |
| **CIP配方表** | `cip_recipe_generator.py` | process_recipe_templates.yaml | 05_Product/auto/茶饮料_CIP配方表_auto.md |
| **产品配方** | `product_recipe_generator.py` | product_recipe_templates.yaml | 05_Product/auto/茶饮料_产品配方表_auto.md |
| **生产线工艺** | `process_flow_generator.py` | system_config.yaml | 02_Arch/auto/茶饮料_生产线工艺配置_auto.md |
| **文档索引** | `index_generator.py` | index_config.yaml | 00_Index/auto/文档索引清单_auto.md |
| **工程清单** | `engineering_generator.py` | cabinet_bom.yaml | 07_Engineering/auto/茶饮料_电控柜BOM清单_auto.xlsx |
| **仪表清单** | `engineering_generator.py` | instrument_list.yaml | 07_Engineering/auto/茶饮料_仪表清单_auto.xlsx |
| **端子定义表** | `engineering_generator.py` | terminal_assignments.yaml | 07_Engineering/auto/茶饮料_端子定义表_auto.xlsx |
| **电缆清单** | `engineering_generator.py` | cable_list.yaml | 07_Engineering/auto/茶饮料_电缆清单_auto.xlsx |

## 使用方式

### 1. 批量生成所有文档

```bash
cd docs/_generators
python run_all_generators.py
```

### 2. 生成单个模块文档

```bash
# 功能块规格
python fb_spec_generator.py

# HMI画面规格
python hmi_generator.py

# 设备参数表
python device_param_generator.py
```

### 3. 验证配置模板

```bash
python template_validator.py
```

## 配置目录

所有YAML配置文件位于 `docs/01_Spec/configs/`：

| 配置文件 | 用途 |
|----------|------|
| system_config.yaml | 系统总体配置 |
| fb_spec_config.yaml | 功能块规格配置 |
| hmi_config.yaml | HMI画面配置 |
| process_recipe_templates.yaml | 工艺配方模板 |
| product_recipe_templates.yaml | 产品配方模板 |
| comm_templates.yaml | 通讯接口模板 |
| interlock_templates.yaml | 联锁逻辑模板 |
| index_config.yaml | 文档索引配置 |
| cabinet_bom.yaml | 电控柜BOM配置 |
| instrument_list.yaml | 仪表清单配置 |
| terminal_assignments.yaml | 端子定义配置 |
| cable_list.yaml | 电缆清单配置 |

## 输出规范

### Markdown文档 (auto目录)
- 文件名格式：`茶饮料_[模块名]_auto.md`
- 包含生成时间戳
- 自动覆盖已有文件

### Excel文档 (07_Engineering/auto目录)
- 文件名格式：`茶饮料_[模块名]_auto.xlsx`
- 使用 openpyxl 生成
- 自动覆盖已有文件

## 生成器开发规范

新增生成器时：

1. 脚本命名：`[模块]_generator.py`
2. 放置于 `docs/_generators/` 目录
3. 输入配置放置于 `docs/01_Spec/configs/`
4. 输出文档放置于对应 `auto/` 目录
5. 在 `run_all_generators.py` 的 GENERATORS 字典中注册

### 基础模板

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[模块名]生成器
"""

import os
import yaml
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "01_Spec" / "configs"
OUTPUT_DIR = SCRIPT_DIR.parent / "XX_Module" / "auto"

def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_[module](config):
    """生成文档内容"""
    pass

def main():
    config = load_yaml(CONFIG_DIR / "[module]_config.yaml")
    output = generate_[module](config)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "茶饮料_[模块名]_auto.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

if __name__ == '__main__':
    main()
```

## 自检清单

生成文档前：
```
[ ] 配置文件是否存在且格式正确？
[ ] 目标目录是否存在？
[ ] 是否有足够的写入权限？
```

生成文档后：
```
[ ] 输出文件是否生成？
[ ] 文件内容是否符合预期？
[ ] 是否需要更新索引文件？
```

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| YAML解析错误 | 配置文件格式错误 | 使用 template_validator.py 验证 |
| 文件未生成 | 输出目录不存在 | 检查并创建目录 |
| 内容为空 | 配置数据为空 | 检查YAML配置内容 |
| 中文乱码 | 文件编码问题 | 确保使用 utf-8 编码 |
