#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TagCode_generator.py
茶饮料生产线SCADA系统 - 位号编码规则文档生成器 (v2.0)

功能: 从 system_config.yaml 读取位号定义，自动生成位号编码规则文档
改进: v2.0 增强编码示例、命名规范、PLC数据区映射等内容

使用方法:
    python TagCode_generator.py

输入:
    configs/system_config.yaml - 核心配置文件（单一真相源）

输出:
    03_Device/auto/位号编码规则_auto.md - 位号编码规则文档

依赖:
    - PyYAML
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

# ============================================================================
# 配置
# ============================================================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONFIG_FILE = PROJECT_ROOT / "configs" / "system_config.yaml"
OUTPUT_FILE = PROJECT_ROOT / "03_Device" / "auto" / "位号编码规则_auto.md"

# ============================================================================
# 工具函数
# ============================================================================
def log_info(msg):
    print(f"[INFO] {msg}")

def log_success(msg):
    print(f"[SUCCESS] {msg}")

def load_yaml(file_path):
    """加载YAML配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        log_error(f"配置文件未找到: {file_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        log_error(f"YAML解析错误: {e}")
        sys.exit(1)

# ============================================================================
# 位号类型定义
# ============================================================================
TAG_TYPES = {
    "AI": {"name": "模拟量输入", "prefix": "AI", "desc": "4-20mA/0-10V连续信号"},
    "AO": {"name": "模拟量输出", "prefix": "AO", "desc": "4-20mA/0-10V控制输出"},
    "DI": {"name": "数字量输入", "prefix": "DI", "desc": "开关状态、限位开关"},
    "DO": {"name": "数字量输出", "prefix": "DO", "desc": "电磁阀、接触器控制"},
    "PI": {"name": "脉冲输入", "prefix": "PI", "desc": "流量计脉冲、编码器"},
    "LT": {"name": "液位传感器", "prefix": "LT", "desc": "储罐液位测量"},
    "TT": {"name": "温度传感器", "prefix": "TT", "desc": "温度测量"},
    "PT": {"name": "压力传感器", "prefix": "PT", "desc": "压力测量"},
    "FT": {"name": "流量传感器", "prefix": "FT", "desc": "流量测量"},
    "DT": {"name": "状态信号", "prefix": "DT", "desc": "设备运行状态"},
    "MT": {"name": "电机温度", "prefix": "MT", "desc": "电机温度监测"},
    "ST": {"name": "速度信号", "prefix": "ST", "desc": "速度传感器"},
    "VT": {"name": "振动信号", "prefix": "VT", "desc": "振动监测"},
    "BT": {"name": "批号追踪", "prefix": "BT", "desc": "批次追踪"},
    "AT": {"name": "分析仪表", "prefix": "AT", "desc": "pH、电导、Brix"},
    "CT": {"name": "计数信号", "prefix": "CT", "desc": "产品计数"},
    "PDT": {"name": "压差信号", "prefix": "PDT", "desc": "过滤器压差"},
    "F0": {"name": "灭菌值", "prefix": "F0", "desc": "F0值计算"},
    "QUAL": {"name": "品质信号", "prefix": "QUAL", "desc": "品质检测结果"},
    "MSG": {"name": "消息数据", "prefix": "MSG", "desc": "喷码内容数据"},
}

# ============================================================================
# 设备类型前缀
# ============================================================================
EQUIPMENT_TYPES = {
    "TK": {"name": "储罐", "example": "TK-101"},
    "P": {"name": "泵", "example": "P-101"},
    "V": {"name": "阀门", "example": "V-101"},
    "M": {"name": "电机", "example": "M-101"},
    "H": {"name": "加热器", "example": "H-101"},
    "C": {"name": "冷却器", "example": "C-101"},
    "F": {"name": "过滤器", "example": "F-101"},
    "CX": {"name": "换热器", "example": "CX-101"},
    "B": {"name": "投料仓", "example": "B-101"},
    "S": {"name": "分离器", "example": "S-101"},
}

# ============================================================================
# 报警后缀定义
# ============================================================================
ALARM_SUFFIXES = {
    "H": {"name": "高报警", "desc": "高高报警"},
    "HH": {"name": "高高报警", "desc": "严重高报警"},
    "L": {"name": "低报警", "desc": "低低报警"},
    "LL": {"name": "低低报警", "desc": "严重低报警"},
    "F": {"name": "故障", "desc": "设备故障"},
    "R": {"name": "运行", "desc": "运行状态"},
    "S": {"name": "停止", "desc": "停止状态"},
}

# ============================================================================
# 文档生成
# ============================================================================
def generate_tag_code_rules(config):
    """生成位号编码规则文档"""

    meta = config['meta']
    sections = config['sections']
    plcs = config['plcs']

    sorted_sections = sorted(sections.values(), key=lambda x: x.get('process_order', 0))

    doc = f"""# 茶饮料生产线SCADA系统位号编码规则

> 文档版本: v2.0
> 创建日期: {meta['created'][:10]}
> 更新日期: {datetime.now().strftime('%Y-%m-%d')}
> 架构: **{len(plcs)}个独立PLC分布式架构**（FL与HM分开）
> **本文件由系统配置自动生成 - 请勿手动修改**

---

## 1. 位号编码体系概述

### 1.1 编码原则

| 原则 | 说明 |
| ---- | ---- |
| **唯一性** | 每个位号唯一对应一个物理点或设备 |
| **可扩展性** | 序号编码留有余量，便于后续扩展 |
| **规律性** | 同类设备使用相同前缀和序号规则 |
| **可识别性** | 从位号可直观判断设备类型和工段 |
| **标准化** | 统一使用 `-` 作为分隔符 |

### 1.2 位号结构

本系统采用 **「工段前缀 + 类型代码 + 序号」** 三段式结构：

```
[工段前缀(2字符)] + [类型代码(2-4字符)] + [序号(3位数字)]
```

**增强结构（含设备前缀）**：

```
[工段前缀(2字符)] + [设备前缀(可选,1-2字符)] + [类型代码(2字符)] + [序号(3位数字)] + [-测量后缀(可选)]
```

### 1.3 编码规则汇总

| 规则 | 说明 |
| ---- | ---- |
| 工段前缀 | 2位大写字母，表示工段 |
| 设备前缀 | 1-2位字母，表示设备类型（可选） |
| 类型代码 | 2-4位字母，表示信号类型 |
| 序号 | 3位数字，从101开始（预留0-100给系统预留） |
| 分隔符 | 使用 `-` 连接各段 |
| 字母顺序 | 全部大写 |

---

## 2. 工段分配表

> **重要**: 本规则与 `configs/system_config.yaml` 保持一致
> - 共{len(plcs)}个独立PLC（FL与HM分开）
> - 流程顺序: WT→TH→EX→FL→BL→HM→UH→BF→PF→CG→LI→CI→LB→CA→PK→CP

| 工段 | 前缀 | 说明 | 序号范围 | PLC编号 | 上游 | 下游 |
|------|------|------|----------|---------|------|------|
"""

    for section in sorted_sections:
        plc = plcs.get(section['plc'])
        plc_name = plc['name'] if plc else 'N/A'
        upstream = ", ".join(section.get('upstream', [])) or "-"
        downstream = ", ".join(section.get('downstream', [])) or "-"
        doc += f"| {section['name']} | {section['prefix']} | {section['name_en']} | {section['number_range'][0]}-{section['number_range'][1]} | {section['plc']} | {upstream} | {downstream} |\n"

    doc += """
---

## 3. 信号类型定义

### 3.1 基础信号类型

| 类型代码 | 全称 | 说明 | 示例 |
|----------|------|------|------|
"""

    for code, info in TAG_TYPES.items():
        doc += f"| {code} | {info['name']} | {info['desc']} | {section['prefix']}-{code}-101 |\n"

    doc += """
### 3.2 设备类型前缀

| 前缀 | 设备类型 | 说明 | 示例 |
|------|----------|------|------|
"""

    for code, info in EQUIPMENT_TYPES.items():
        doc += f"| {code} | {info['name']} | {info.get('desc', '')} | {info['example']} |\n"

    doc += """
### 3.3 报警/状态后缀

| 后缀 | 名称 | 说明 | 组合示例 |
|------|------|------|----------|
"""

    for code, info in ALARM_SUFFIXES.items():
        doc += f"| {code} | {info['name']} | {info['desc']} | LT-{code}101, TT-{code}101 |\n"

    doc += """
### 3.4 复合信号类型

| 类型代码 | 全称 | 说明 | 组成 |
|----------|------|------|------|
| LSH | 液位高报警 | 储罐液位高 | LT + H |
| LSL | 液位低报警 | 储罐液位低 | LT + L |
| TSH | 温度高报警 | 温度高高报警 | TT + H |
| TSL | 温度低报警 | 温度低报警 | TT + L |
| PSH | 压力高报警 | 压力高报警 | PT + H |
| PSL | 压力低报警 | 压力低报警 | PT + L |
| FSH | 流量高报警 | 流量高报警 | FT + H |
| FSL | 流量低报警 | 流量低报警 | FT + L |
| RUN | 运行状态 | 设备运行中 | DT + RUN |
| STOP | 停止状态 | 设备停止 | DT + STOP |
| FALT | 故障状态 | 设备故障 | DT + FALT |

---

## 4. 位号命名规范

### 4.1 命名规则

1. **唯一性**: 每个位号在整个系统中唯一
2. **可读性**: 位号应反映设备类型和位置
3. **扩展性**: 序号预留足够空间便于扩展
4. **一致性**: 同一类型设备采用相同的命名模式
5. **完整性**: 包含工段、设备、测量类型、序号

### 4.2 禁止事项

| 禁止 | 说明 |
| ---- | ---- |
| 重复命名 | 同一工段内位号不能重复 |
| 中英文混用 | 位号必须全部大写英文 |
| 特殊字符 | 除 `-` 外不使用其他分隔符 |
| 超过长度 | 位号总长度不超过20字符 |

### 4.3 序号分配规则

| 序号范围 | 用途 | 说明 |
| -------- | ---- | ---- |
| 001-100 | 系统预留 | 关键联锁、安全回路 |
| 101-199 | 第一组设备 | 常规设备 |
| 201-299 | 第二组设备 | 扩展设备 |
| 301-399 | 第三组设备 | 备用 |
| 901-999 | 特殊用途 | 批次、配方、计算值 |

---

## 5. 常用位号模板

### 5.1 储罐类设备位号模板

| 序号 | 位号 | 说明 | 类型 |
| ---- | ---- | ---- | ---- |
| 1 | `[工段]-TK-101` | 1号储罐 | 设备 |
| 2 | `[工段]-LT-101` | 液位传感器 | LT |
| 3 | `[工段]-LT-102` | 液位传感器(备用) | LT |
| 4 | `[工段]-LSH-101` | 液位高报警 | DI |
| 5 | `[工段]-LSL-101` | 液位低报警 | DI |
| 6 | `[工段]-TT-101` | 温度传感器 | TT |
| 7 | `[工段]-PT-101` | 压力传感器 | PT |
| 8 | `[工段]-AT-101` | 分析仪表(pH/Brix) | AT |

### 5.2 泵类设备位号模板

| 序号 | 位号 | 说明 | 类型 |
| ---- | ---- | ---- | ---- |
| 1 | `[工段]-P-101` | 1号输送泵 | 设备 |
| 2 | `[工段]-DT-101` | 运行状态反馈 | DI |
| 3 | `[工段]-DT-102` | 故障状态反馈 | DI |
| 4 | `[工段]-DO-101` | 启动命令 | DO |
| 5 | `[工段]-DO-102` | 停止命令 | DO |
| 6 | `[工段]-ST-101` | 转速反馈 | ST |
| 7 | `[工段]-FT-101` | 出口流量 | FT |

### 5.3 阀门类设备位号模板

| 序号 | 位号 | 说明 | 类型 |
| ---- | ---- | ---- | ---- |
| 1 | `[工段]-V-101` | 1号调节阀 | 设备 |
| 2 | `[工段]-AO-101` | 开度设定 | AO |
| 3 | `[工段]-AI-101` | 开度反馈 | AI |
| 4 | `[工段]-DI-101` | 阀开到位反馈 | DI |
| 5 | `[工段]-DI-102` | 阀关到位反馈 | DI |
| 6 | `[工段]-DO-101` | 开阀命令 | DO |
| 7 | `[工段]-DO-102` | 关阀命令 | DO |

### 5.4 批次控制位号模板

| 序号 | 位号 | 说明 | 类型 |
| ---- | ---- | ---- | ---- |
| 1 | `[工段]-BT-101` | 当前批次号 | BT |
| 2 | `[工段]-BT-102` | 批次配方号 | BT |
| 3 | `[工段]-AT-101` | Brix值(浓度) | AT |
| 4 | `[工段]-AT-102` | pH值 | AT |
| 5 | `[工段]-FT-101` | 累计流量 | FT |
| 6 | `[工段]-QUAL-101` | 品质判定结果 | QUAL |

### 5.5 UHT杀菌专用位号模板

| 序号 | 位号 | 说明 | 类型 |
| ---- | ---- | ---- | ---- |
| 1 | `[UH]-TT-101` | 预热段温度 | TT |
| 2 | `[UH]-TT-102` | 杀菌段温度 ★CCP | TT |
| 3 | `[UH]-TT-103` | 保温段温度 | TT |
| 4 | `[UH]-PT-101` | 杀菌压力 | PT |
| 5 | `[UH]-F0-101` | F0灭菌值 ★CCP | F0 |
| 6 | `[UH]-FT-101` | 产品流量 | FT |
| 7 | `[UH]-DT-101` | 杀菌运行状态 | DT |

### 5.6 高速同步位号模板 (BF/PF/CG)

| 序号 | 位号 | 说明 | 类型 |
| ---- | ---- | ---- | ---- |
| 1 | `[工段]-ST-101` | 线速度 | ST |
| 2 | `[工段]-CT-101` | 瓶计数 | CT |
| 3 | `[工段]-CT-102` | 合格品计数 | CT |
| 4 | `[工段]-CT-103` | 不合格品计数 | CT |
| 5 | `[工段]-DT-101` | 同步信号状态 | DT |

---

## 6. PLC数据区映射

| PLC编号 | 工段 | 数据区 | 功能 | 起始位号 | 备注 |
| ---------- | ---- | ------ | ---- | -------- | ---- |
"""

    for section in sorted_sections:
        plc = plcs.get(section['plc'])
        if not plc:
            continue
        db_num = int(section['plc'].replace('PLC-', '')) + 1000
        first_tag = f"{section['prefix']}-LT-101"
        remark = "CCP关键" if plc.get('is_ccp') else ("高速同步" if plc.get('is_high_speed') else "")
        doc += f"| {section['plc']} | {section['name']} | DB{db_num} | {plc['role']} | {first_tag} | {remark} |\n"

    doc += """
---

## 7. 位号示例

### 7.1 水处理系统 (WT)

| 位号 | 说明 | 类型 |
| ---- | ---- | ---- |
| WT-TK-101 | 原水箱 | 设备 |
| WT-LT-101 | 原水箱液位 | LT |
| WT-LSH-101 | 原水箱液位高报警 | DI |
| WT-P-101 | 原水输送泵 | 设备 |
| WT-DT-101 | 原水泵运行状态 | DI |
| WT-DO-101 | 原水泵启动命令 | DO |
| WT-FT-101 | 产水流量 | FT |
| WT-CTT-101 | 产水电导率 | AT |
| WT-PT-101 | RO前压力 | PT |

### 7.2 UHT杀菌系统 (UH) ★CCP

| 位号 | 说明 | 类型 |
| ---- | ---- | ---- |
| UH-TK-101 | 无菌储罐 | 设备 |
| UH-TT-102 | 杀菌段温度 ★CCP | TT |
| UH-F0-101 | F0灭菌值 ★CCP | F0 |
| UH-PT-101 | 杀菌压力 | PT |
| UH-FT-101 | 产品流量 | FT |
| UH-DT-101 | 杀菌运行状态 | DT |

### 7.3 灌装系统 (PF) ★高速

| 位号 | 说明 | 类型 |
| ---- | ---- | ---- |
| PF-FT-101 | 灌装流量 | FT |
| PF-ST-101 | 灌装速度 | ST |
| PF-CT-101 | 灌装计数 | CT |
| PF-CT-102 | 合格品计数 | CT |
| PF-LT-101 | 料位 | LT |
| PF-DT-101 | 灌装阀状态 | DT |

---

## 8. 版本记录

| 版本 | 日期 | 变更内容 |
| ------ | ------ | ---------- |
| v1.0 | 2026-04-30 | 初始版本 |
| v2.0 | """ + datetime.now().strftime('%Y-%m-%d') + """ | 增强编码示例、命名规范、PLC数据区映射等内容 |

---

**文档状态**: 自动生成
**生成时间**: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
**审核状态**: 待审核
"""

    return doc

# ============================================================================
# 主函数
# ============================================================================
def main():
    log_info("=" * 60)
    log_info("TagCode_generator.py - 位号编码规则生成器 v2.0")
    log_info("=" * 60)

    if not CONFIG_FILE.exists():
        log_error(f"配置文件未找到: {CONFIG_FILE}")
        sys.exit(1)

    log_info(f"读取配置文件: {CONFIG_FILE}")

    config = load_yaml(CONFIG_FILE)
    log_success("配置加载成功")

    log_info("生成位号编码规则文档...")
    doc = generate_tag_code_rules(config)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(doc)

    log_success(f"文档生成成功: {OUTPUT_FILE}")
    log_info("=" * 60)

if __name__ == "__main__":
    main()
