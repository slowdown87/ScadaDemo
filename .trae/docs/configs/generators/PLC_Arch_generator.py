#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC_Architecture_generator.py
茶饮料生产线SCADA系统 - PLC架构文档生成器

功能: 从 system_config.yaml 读取核心配置，自动生成 PLC_Architecture.md

使用方法:
    python PLC_Arch_generator.py

输入:
    configs/system_config.yaml - 核心配置文件（单一真相源）

输出:
    02_Arch/PLC_Architecture_auto.md - PLC架构文档

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
OUTPUT_FILE = PROJECT_ROOT / "02_Arch" / "auto" / "PLC_Architecture_auto.md"

# 颜色定义（用于终端输出）
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg):
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")

def log_success(msg):
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")

def log_warning(msg):
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")

def log_error(msg):
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")

# ============================================================================
# YAML加载器
# ============================================================================
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
# 文档生成
# ============================================================================
def generate_plc_architecture(config):
    """生成PLC架构文档"""

    meta = config['meta']
    plcs = config['plcs']
    sections = config['sections']
    process_flow = config['process_flow']
    high_speed_sync = config['high_speed_sync']
    plc_comm_matrix = config['plc_comm_matrix']
    scada_components = config['scada_components']
    ob_config = config['ob_config']
    io_summary = config['io_summary']

    # 按process_order排序PLC
    sorted_plcs = sorted(plcs.values(), key=lambda x: x.get('process_order', 0))

    # 生成文档
    doc = f"""# 茶饮料生产线PLC架构设计

> 文档版本: {meta['version']}
> 创建日期: {meta['created'][:10]}
> 更新日期: {datetime.now().strftime('%Y-%m-%d')}
> 架构: **{len(plcs)}个独立PLC分布式架构**（FL与HM分开）
> **本文件由系统配置自动生成 - 请勿手动修改**

---

## ⚠️ 重要声明

**本文档为茶饮料生产线的基准架构文档**，所有其他文档（通讯接口规格书、设备参数表、位号编码规则等）必须以此为准。

**生成机制**: 本文件由 `configs/system_config.yaml` 自动生成。
**修改流程**: 编辑 `configs/system_config.yaml` 后，重新运行生成器。

---

## 1. 系统架构

### 1.1 架构概述

| 项目 | 参数 |
|------|------|
| PLC数量 | **{len(plcs)}个**（液料线{len(process_flow['liquid_line']['sections'])}个+包装线{len(process_flow['packaging_line']['sections'])}个+CIP {len(process_flow['independent_systems']['sections'])}个+备1个） |
| 控制系统 | 西门子S7-1500系列 |
| 通讯网络 | PROFINET（100Mbps）+ Industrial Ethernet |
| 冗余方式 | PLC冗余（CPU mirroring）+ 网络冗余（HRP环网） |
| 拓扑结构 | 设备层 → 车间层 → 监控层 |
| 产品类型 | {meta['product_type']} |
| 产能 | {meta['capacity']} |

### 1.2 网络架构图

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                 监控层                                                          │
│                                    ┌──────────────────┐    ┌──────────────────┐                              │
│                                    │   SCADA主站     │◀──▶│   SCADA备站      │                              │
│                                    │  {scada_components['scada_primary']['ip']}  │    │  {scada_components['scada_backup']['ip']}  │                              │
│                                    └────────┬─────────┘    └────────┬─────────┘                              │
└─────────────────────────────────────────────┼──────────────────────────┼────────────────────────────────────┘
                                              │                          │
                                              │ PROFINET                 │
┌─────────────────────────────────────────────┼──────────────────────────┼────────────────────────────────────┐
│                                            │    车间层（控制层）       │                                    │
│    ┌───────────────────────────────────────┼──────────────────────────┼───────────────────────────────┐    │
│    │                                ┌──────┴──────┐    ┌──────┴──────┐                               │    │
│    │                                │  核心交换机   │◀──▶│  核心交换机   │                               │    │
│    │                                │  {scada_components['core_switch_1']['ip']} │    │  {scada_components['core_switch_2']['ip']} │                               │    │
│    │                                └──────┬──────┘    └──────┬──────┘                               │    │
│    │                                      │                  │                                         │    │
│    │     ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │    │
"""

    # 添加液料线PLC (PLC-1 到 PLC-7)
    liquid_plcs = [p for p in sorted_plcs if p['section'] in process_flow['liquid_line']['sections']]
    for plc in liquid_plcs:
        doc += f"""│    │     │ {plc['name'].split()[0]:<6} │  │ {plc['section']:<3}   │  │ {plc['ip']} │         │    │
"""

    doc += """│    │           │            │            │            │            │            │                  │    │
│    │     ┌─────┴────────────┴────────────┴────────────┴────────────┴────────────┘                  │    │
│    │     │                         H-Sync光纤环网                                                │    │
│    │     └─────┬────────────┬────────────┬────────────┬────────────┬────────────┘                  │    │
│    │           │            │            │            │            │                                │    │
│    │     ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐         │    │
"""

    # 添加包装线前半段 (PLC-8 到 PLC-12)
    packaging_plcs = [p for p in sorted_plcs if p['section'] in process_flow['packaging_line']['sections']]
    for plc in packaging_plcs[:5]:
        doc += f"""│    │     │ {plc['name'].split()[0]:<6} │  │ {plc['section']:<3}   │  │ {plc['ip']} │         │    │
"""

    doc += """│    │           │            │            │            │            │            │                  │    │
│    │           └────────────┴────────────┴────────────┴────────────┴────────────┘                  │    │
│    │                                    H-Sync光纤环网                                                │    │
│    │                          ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                    │    │
"""

    # 添加包装线后半段和CIP (PLC-13 到 PLC-16)
    for plc in packaging_plcs[5:] + [p for p in sorted_plcs if p['section'] in process_flow['independent_systems']['sections']]:
        doc += f"""│    │                          │ {plc['name'].split()[0]:<6} │  │ {plc['section']:<3}   │  │ {plc['ip']} │                    │    │
"""

    doc += """│    └───────────────────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 工艺流程顺序与PLC分配

```
液料生产线:                          包装生产线:
┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐
"""

    # 液料线
    for i, section in enumerate(process_flow['liquid_line']['sections']):
        plc = next(p for p in sorted_plcs if p['section'] == section)
        arrow = "──▶" if i < len(process_flow['liquid_line']['sections']) - 1 else ""
        doc += f"│ {section:<3} │{arrow}"
    doc += """
└─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘
"""

    # PLC编号行
    for i, section in enumerate(process_flow['liquid_line']['sections']):
        plc = next(p for p in sorted_plcs if p['section'] == section)
        arrow = "   " if i < len(process_flow['liquid_line']['sections']) - 1 else ""
        doc += f"│{plc['name']:<4}│{arrow}"
    doc += """
                                                        │         │
                                                        │         ▼
                                                     ┌─────┐   ┌─────┐
"""

    # 包装线
    for i, section in enumerate(process_flow['packaging_line']['sections']):
        plc = next(p for p in sorted_plcs if p['section'] == section)
        arrow = "──▶" if i < len(process_flow['packaging_line']['sections']) - 1 and i != 3 else ""
        if i == 3:
            arrow = "──▶"
        doc += f"│ {section:<3} │{arrow}"
    doc += """
└─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘
"""

    # 包装线PLC编号行（分行显示）
    for i in range(0, len(process_flow['packaging_line']['sections']), 4):
        group = process_flow['packaging_line']['sections'][i:i+4]
        for j, section in enumerate(group):
            plc = next(p for p in sorted_plcs if p['section'] == section)
            if j == 0:
                doc += f"│{plc['name']:<4}│"
            else:
                doc += f"{plc['name']:<4}│"
        if i + 4 < len(process_flow['packaging_line']['sections']):
            doc += "\n                                                     │         │\n                                                     ▼         ▼\n                                                     ┌─────┐   ┌─────┐\n"
        else:
            doc += """

独立系统:
┌─────┐
│ CP  │
└─────┘
"""

    doc += """
---

## 2. PLC配置

### 2.1 PLC配置表

| PLC编号 | 控制工段 | CPU型号 | 通讯接口 | 冗余方式 | I/O估算 | 备注 |
| ------ | --------- | ------------- | ---- | ---------- | ------ | --------- |
"""

    for plc in sorted_plcs:
        remark = plc.get('role', '')
        if plc.get('is_ccp'):
            remark = f"**CCP关键**"
        if plc.get('is_high_speed'):
            remark = f"**{remark}**" if remark else "**超高速**"
        doc += f"| {plc['name']} | {plc['name_en']} | {plc['cpu']} | {plc['通讯接口']} | {plc['冗余方式']} | {plc['io_estimate']} | {remark} |\n"

    doc += f"""
**I/O总计**: 约{io_summary['total_estimated']}点（液料线{io_summary['liquid_line']}点 + 包装线{io_summary['packaging_line']}点 + CIP{io_summary['independent']}点）

### 2.2 IP地址规划表 (基于{config['meta']['base_ip_subnet']})

> **IP段**: {config['meta']['base_ip_subnet']}（备选段，避免与办公网络冲突）
> **网关**: {config['meta']['gateway']}
> **子网掩码**: {config['meta']['subnet_mask']}

| PLC编号 | 控制工段 | IP地址 | 备注 |
|---------|----------|--------|------|
"""

    for plc in sorted_plcs:
        remark = plc.get('role', '')
        if plc.get('is_ccp'):
            remark = "CCP关键"
        doc += f"| {plc['name']} | {plc['name_en']} | {plc['ip']} | {remark} |\n"

    doc += f"""| SCADA主服务器 | - | {scada_components['scada_primary']['ip']} | |
| SCADA备服务器 | - | {scada_components['scada_backup']['ip']} | |
| 工程师站 | - | {scada_components['engineer_station']['ip']} | |
| 核心交换机1 | - | {scada_components['core_switch_1']['ip']} | {scada_components['core_switch_1']['role']} |
| 核心交换机2 | - | {scada_components['core_switch_2']['ip']} | {scada_components['core_switch_2']['role']} |

### 2.3 控制系统职责划分

| PLC | 工段名称 | 主要控制任务 | 上游接口 | 下游接口 | 关键控制点 |
| ------ | --------- | ----------------- | ------- | ------ | --------------- |
"""

    for plc in sorted_plcs:
        section = sections[plc['section']]
        upstream = ", ".join(section.get('upstream', [])) or "-"
        downstream = ", ".join(section.get('downstream', [])) or "-"
        ctrl_level = "CCP" if plc.get('is_ccp') else "P1"
        doc += f"| {plc['name']} | {plc['name']} | {plc['role']} | {upstream} | {downstream} | {ctrl_level} |\n"

    doc += """
### 2.4 PLC选型说明

| CPU型号 | 应用PLC | 选型理由 |
| ------------- | ------------------------------ | --------------------- |
"""

    # 按CPU型号分组
    cpu_groups = {}
    for plc in sorted_plcs:
        cpu = plc['cpu']
        if cpu not in cpu_groups:
            cpu_groups[cpu] = []
        cpu_groups[cpu].append(plc['name'])

    for cpu, plc_list in cpu_groups.items():
        if "1517" in cpu:
            reason = "高性能处理能力，满足批次控制和高速同步需求"
        elif "1215C" in cpu:
            reason = "入门级，喷码机通常自带PLC，仅需通讯对接"
        else:
            reason = "标准性能，满足一般控制需求"
        doc += f"| {cpu} | {', '.join(plc_list)} | {reason} |\n"

    doc += """
---

## 3. 程序架构

### 3.1 项目总体结构

```
SCADA_Project
"""

    for plc in sorted_plcs:
        section = sections[plc['section']]
        doc += f"""| {'_'*30}
│   └── PLC_{plc['name'].split('-')[0].replace('PLC-', '')}_{section['prefix']}_{section['name_en'].replace(' ', '')}
│       ├── PLC_{plc['name'].split('-')[0].replace('PLC-', '')}_{section['prefix']}.config
│       └── Program_{plc['name'].split('-')[0].replace('PLC-', '')}
│           ├── OB1_Main
│           ├── OB100_StartUp
│           └── Functions
"""

    doc += """
└── SCADA_Project.db
```

---

## 4. 高速同步与通讯

### 4.1 同步需求分析

| 高速同步对 | 同步周期 | 同步内容 | 精度要求 |
| ---------- | -------- | -------- | -------- |
"""

    for sync in high_speed_sync:
        doc += f"| {sync['from_section']} → {sync['to_section']} | **{sync['period_ms']}ms** | {sync['content']} | ±{sync['precision_ms']}ms |\n"

    doc += """
### 4.2 PLC间通讯矩阵

| 发送方 | 接收方 | 通讯方式 | 数据内容 | 周期 | 说明 |
| ---------- | ---------- | -------------- | -------- | -------- | -------- |
"""

    for comm in plc_comm_matrix:
        receivers = comm['to'] if isinstance(comm['to'], list) else [comm['to']]
        receiver_str = ", ".join(receivers)
        doc += f"| {comm['from']} | {receiver_str} | {comm['method']} | {comm['data']} | {comm['period_ms']}ms | {comm['desc']} |\n"

    doc += """
---

## 5. 中断与时间控制

### 5.1 中断组织块配置

| OB | 类型 | 循环时间 | 应用PLC | 说明 |
| --- | -------------- | -------- | -------------- | ------------ |
"""

    for ob_name, ob_info in ob_config.items():
        cycle = f"{ob_info.get('cycle_ms', '-')}ms" if 'cycle_ms' in ob_info else "-"
        applies_to = ", ".join(ob_info['applies_to']) if isinstance(ob_info['applies_to'], list) else ob_info['applies_to']
        doc += f"| {ob_name} | {ob_info['type']} | {cycle} | {applies_to} | {ob_info['desc']} |\n"

    doc += """
### 5.2 关键时序要求

| 工段 | 时间要求 | 说明 |
| ---- | -------- | ---- |
| UHT杀菌温度 | <10ms响应 | CCP关键控制点 |
| 灌装同步 | <1ms精度 | 72ms周期要求 |
| 旋盖扭矩 | <5ms响应 | 品质控制 |
| 瓶位同步 | <1ms精度 | 高速线同步 |

---

## 6. 版本记录

| 版本 | 日期 | 变更内容 |
| ------ | ------ | ---------- |
| v1.0 | 2026-04-30 | 初始版本，从system_config.yaml自动生成 |

---

**文档状态**: 自动生成
**生成时间**: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
**审核状态**: 待审核
**批准人**: -
"""

    return doc

# ============================================================================
# 主函数
# ============================================================================
def main():
    log_info("=" * 60)
    log_info("PLC_Architecture_generator.py - PLC架构文档生成器")
    log_info("=" * 60)

    # 检查配置文件
    if not CONFIG_FILE.exists():
        log_error(f"配置文件未找到: {CONFIG_FILE}")
        log_info("请确保 configs/system_config.yaml 存在")
        sys.exit(1)

    log_info(f"读取配置文件: {CONFIG_FILE}")

    # 加载配置
    config = load_yaml(CONFIG_FILE)
    log_success(f"配置加载成功: {config['meta']['version']}")

    # 生成文档
    log_info("生成PLC架构文档...")
    doc = generate_plc_architecture(config)

    # 确保输出目录存在
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(doc)

    log_success(f"文档生成成功: {OUTPUT_FILE}")
    log_info("=" * 60)

if __name__ == "__main__":
    main()
