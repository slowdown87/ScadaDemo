#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process_Flow_generator.py
茶饮料生产线 - 生产线工艺配置生成器

功能: 从 system_config.yaml 读取配置，自动生成生产线工艺配置文档

使用方法:
    python Process_Flow_generator.py

输入:
    01_Spec/configs/system_config.yaml - 核心配置文件

输出:
    02_Arch/auto/生产线工艺配置_auto.md

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
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "01_Spec" / "configs" / "system_config.yaml"
OUTPUT_FILE = PROJECT_ROOT / "02_Arch" / "auto" / "茶饮料_生产线工艺配置_auto.md"

# ============================================================================
# 工具函数
# ============================================================================
def log_info(msg):
    print(f"[INFO] {msg}")

def log_success(msg):
    print(f"[SUCCESS] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}")

def load_yaml(file_path):
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
# 文档生成函数
# ============================================================================
def generate_header(config):
    meta = config.get('meta', {})
    io_sum = config.get('io_summary', {})

    return f"""# 生产线工艺配置

> 文档版本: v1.0
> 创建日期: {meta.get('created', datetime.now().strftime('%Y-%m-%d'))}
> 更新日期: {datetime.now().strftime('%Y-%m-%d')}
> 数据来源: system_config.yaml
> 产品类型: {meta.get('product_type', '纯茶饮料')}
> 产能: {meta.get('capacity', '50000B/H')}

---

## 文档说明

本文档为**生产线工艺配置清单**，由 system_config.yaml 自动生成。
内容包括工段顺序、设备配置、工艺参数等基础数据。

**工艺路线**: UHT无菌灌装
**杀菌方式**: UHT超高温瞬时杀菌（135℃/15s）
**灌装温度**: 室温（25-30℃）

---

"""

def generate_sections_overview(config):
    sections = config.get('sections', {})
    plcs = config.get('plcs', {})

    lines = ["## 1. 工段配置概览\n"]
    lines.append("| 工段ID | 工段名称 | PLC | 控制设备 | I/O估算 |")
    lines.append("|--------|----------|-----|----------|---------|")

    section_order = ['WT', 'TH', 'EX', 'FL', 'BL', 'HM', 'UH', 'BF', 'PF', 'CG', 'LI', 'CI', 'LB', 'CA', 'PK', 'CP']

    for sec_id in section_order:
        if sec_id in sections:
            sec = sections[sec_id]
            plc_id = sec.get('plc', '')
            plc = plcs.get(plc_id, {})
            lines.append(f"| {sec_id} | {sec.get('name', sec_id)} | {plc_id} | {plc.get('name', '')} | {plc.get('io_estimate', 'N/A')} |")

    lines.append("")
    return "\n".join(lines) + "\n"

def generate_process_flow(config):
    sections = config.get('sections', {})
    plcs = config.get('plcs', {})

    flow_diagram = """## 2. 工艺流程概览

### 2.1 生产线工艺流程

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    茶饮料生产线 (UHT无菌灌装)                                   │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                                      公用工程                                         │   │
│  │  纯水系统(WT) ──▶ 调配用水、设备清洗                                                    │   │
│  │  CIP清洗系统(CP) ──▶ 各设备循环清洗                                                     │   │
│  │  压缩空气系统 ──▶ 气动元件                                                              │   │
│  └─────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                             │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│  ║                                    液料生产线                                           ║   │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│                                                                                             │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐         │
│  │ 水处理 │ → │茶叶前 │ → │ 萃取  │ → │ 过滤  │ → │ 调配  │ → │ 均质  │ → │UHT  │ → 无菌 │
│  │  WT  │   │  TH  │   │  EX  │   │  FL  │   │  BL  │   │  HM  │   │  UH  │   储罐  │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘         │
│                                                                                             │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│  ║                                    制瓶生产线                                           ║   │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│                                                                                             │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                                       │
│  │ 瓶坯  │ → │瓶坯  │ → │瓶胚  │ → │加热  │ → │ 吹瓶  │ → 空瓶                               │
│  │ 原料  │   │ 储存  │   │提升  │   │ 炉   │   │  BF  │                                 │
│  └─────┘   └─────┘   └─────┘   └─────┘   └─────┘                                       │
│                                                                                             │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│  ║                                    无菌灌装线                                           ║   │
│  ═══════════════════════════════════════════════════════════════════════════════════════   │
│                                                                                             │
│  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐               │
│  │ 无菌  │ → │ 旋盖  │ → │ 灯检  │ → │ 喷码  │ → │ 贴标  │ → │ 装箱  │ → 膜包 │
│  │ 灌装  │   │  CG  │   │  LI  │   │  CI  │   │  LB  │   │  CA  │   码垛   │
│  │  PF  │   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘   └─────┘               │
│  └─────┘                                                                           │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```
"""

    return flow_diagram + """

"""

def generate_plc_config(config):
    plcs = config.get('plcs', {})

    lines = ["## 3. PLC控制配置\n"]
    lines.append("| PLC ID | IP地址 | 工段 | 冗余方式 | 通讯协议 |")
    lines.append("|--------|--------|------|----------|----------|")

    for pid in sorted(plcs.keys()):
        p = plcs[pid]
        lines.append(f"| {pid} | {p.get('ip', 'N/A')} | {p.get('name', '')} | {p.get('冗余方式', '无')} | Ethernet/IP |")

    lines.append("")
    return "\n".join(lines) + "\n"

def safe_int(value, default=0):
    try:
        import re
        match = re.search(r'\d+', str(value))
        return int(match.group()) if match else default
    except:
        return default

def generate_io_summary(config):
    io_sum = config.get('io_summary', {})
    plcs = config.get('plcs', {})

    total_est = io_sum.get('total_estimated', 0)
    total_plc = sum(safe_int(plc.get('io_estimate', 0)) for plc in plcs.values())

    lines = ["## 4. I/O配置汇总\n"]
    lines.append("| 项目 | 数量 |")
    lines.append("|------|------|")
    lines.append(f"| 总I/O估算 | 约{total_est}点 |")
    lines.append(f"| PLC数量 | {len(plcs)}个 |")
    lines.append(f"| 各PLC I/O合计 | 约{total_plc}点 |")

    lines.append("")
    lines.append("### 4.1 各工段I/O分布")
    lines.append("")
    lines.append("| 工段 | I/O估算 | 主要控制内容 |")
    lines.append("|------|---------|--------------|")

    io_by_section = {
        'WT': ('水处理', '原水、多介质过滤、活性炭、RO、离子交换'),
        'TH': ('茶叶前处理', '投料、粉碎、磁选、输送'),
        'EX': ('萃取', '三级逆流萃取、温度控制、时间控制'),
        'FL': ('过滤', '碟式离心、超滤膜'),
        'BL': ('调配', '糖浆、酸液、香精调配、Brix/pH控制'),
        'HM': ('均质', '均质压力、温度'),
        'UH': ('UHT杀菌', '预热、杀菌、保温、冷却、CCP监控'),
        'BF': ('制瓶', '瓶坯、加热、吹瓶'),
        'PF': ('灌装', '灌装、液位'),
        'CG': ('旋盖', '扭矩控制'),
        'LI': ('灯检', '视觉检测'),
        'CI': ('喷码', '日期、批次码'),
        'LB': ('贴标', '标签贴合'),
        'CA': ('装箱', '纸箱成型、计数'),
        'PK': ('膜包码垛', '膜包、机器人码垛'),
        'CP': ('CIP清洗', '清洗配方、步骤控制'),
    }

    for sec_id, (name, desc) in io_by_section.items():
        if sec_id in plcs:
            plc = plcs[sec_id]
            lines.append(f"| {sec_id} | {plc.get('io_estimate', 'N/A')} | {desc} |")

    lines.append("")
    return "\n".join(lines) + "\n"

def generate_capacity_info(config):
    meta = config.get('meta', {})

    lines = ["## 5. 产能配置\n"]
    lines.append("| 项目 | 参数 |")
    lines.append("|------|------|")
    lines.append(f"| 设计产能 | {meta.get('capacity', '50000B/H')} |")
    lines.append(f"| 最大产能 | 54000B/H |")
    lines.append(f"| 包装形式 | PET瓶（500ml，可选200ml-2000ml） |")
    lines.append(f"| 灌装方式 | UHT无菌灌装 |")
    lines.append(f"| 杀菌方式 | UHT超高温瞬时杀菌（135℃/15s） |")
    lines.append(f"| 灌装温度 | 室温（25-30℃） |")
    lines.append(f"| 保质期 | 6-12个月（常温储存） |")
    lines.append(f"| 生产班次 | 3班/天，每班8小时 |")

    lines.append("")
    lines.append("### 5.1 产能换算")
    lines.append("")
    lines.append("| 单位 | 产量 | 计算依据 |")
    lines.append("|------|------|----------|")
    lines.append("| 每秒 | 15瓶 | 54000÷3600 |")
    lines.append("| 每分钟 | 900瓶 | 54000÷60 |")
    lines.append("| 每小时 | 54000瓶 | 设计产能 |")
    lines.append("| 每日(24h) | 129.6万瓶 | 54000×24 |")

    lines.append("")
    return "\n".join(lines) + "\n"

def generate_product_config(config):
    product_recipe = config.get('product_recipe', {})

    lines = ["## 6. 产品配置\n"]

    tea_types = product_recipe.get('tea_types', {})
    if tea_types:
        lines.append("### 6.1 茶类产品参数")
        lines.append("")
        lines.append("| 茶类 | 水温 | 茶水比 | 萃取时间 | 茶多酚要求 |")
        lines.append("|------|------|--------|----------|------------|")
        for tea_id, tea in tea_types.items():
            lines.append(f"| {tea.get('name', tea_id)} | {tea.get('water_temp', '-')} | {tea.get('tea_water_ratio', '-')} | {tea.get('extraction_time', '-')} | {tea.get('tea_polyphenol', '-')} |")

    unified = product_recipe.get('unified_quality', {})
    if unified:
        lines.append("")
        lines.append("### 6.2 产品统一质量指标")
        lines.append("")
        lines.append("| 参数 | 目标值 | 控制范围 |")
        lines.append("|------|--------|----------|")
        lines.append(f"| 最终pH | {unified.get('final_ph', '-')} | {unified.get('ph_range', '-')} |")
        lines.append(f"| 最终Brix | {unified.get('final_brix', '-')}°Bx | {unified.get('brix_range', '-')} |")
        lines.append(f"| 灌装温度 | {unified.get('fill_temp', '-')} | {unified.get('fill_temp_range', '-')} |")
        lines.append(f"| 灌装容量 | {unified.get('fill_capacity', '-')} | ±{unified.get('fill_tolerance', '-')} |")

    lines.append("")
    return "\n".join(lines) + "\n"


def generate_process_params(config):
    process_params = config.get('process_params', {})
    sections = config.get('sections', {})

    if not process_params:
        return ""

    section_order = ['WT', 'TH', 'EX', 'FL', 'BL', 'HM', 'UH', 'PF', 'CG']
    lines = ["## 7. 各工段工艺参数\n"]

    idx = 1
    for sec_id in section_order:
        if sec_id not in process_params:
            continue

        params = process_params[sec_id]
        lines.append(f"### 7.{idx} {params.get('name', sec_id)}({sec_id})")
        idx += 1
        lines.append("")
        lines.append(f"**设备**: {params.get('equipment', '-')}")
        if 'batch_size' in params:
            lines.append(f"**批次容量**: {params.get('batch_size', '-')}")
        if 'capacity' in params:
            lines.append(f"**处理能力**: {params.get('capacity', '-')}")
        lines.append("")
        lines.append("| 参数 | 设定值 | 控制范围 | 控制方式 |")
        lines.append("|------|--------|----------|----------|")

        for p in params.get('params', []):
            name = p.get('name', '-')
            value = p.get('value', '-')
            range_val = p.get('range', '-') if p.get('range') else '-'
            control = p.get('control', '-')
            lines.append(f"| {name} | {value} | {range_val} | {control} |")

        if sec_id == 'UH' and 'backwash' in params:
            lines.append("")
            lines.append("**自动反洗触发条件**:")
            for filter_name, filter_info in params['backwash'].items():
                lines.append(f"- {filter_name}: {filter_info.get('trigger', '-')}")

        lines.append("")

    return "\n".join(lines) + "\n"


def generate_ccp_config(config):
    ccp_config = config.get('ccp_config', {})

    if not ccp_config:
        return ""

    lines = ["## 8. 关键控制点(CCP)配置\n"]
    lines.append("| CCP点 | 工段 | 监控参数 | 设定值 | 临界值 | 响应时间 | 纠偏措施 |")
    lines.append("|-------|------|----------|--------|--------|----------|----------|")

    for ccp_id, ccp in ccp_config.items():
        lines.append(f"| {ccp_id} | {ccp.get('section', '-')} | {ccp.get('parameter', '-')} | {ccp.get('setpoint', '-')} | {ccp.get('critical_limit', '-')} | {ccp.get('response_time_ms', '-')}ms | {ccp.get('action', '-')} |")

    lines.append("")
    return "\n".join(lines) + "\n"


def generate_cip_config(config):
    cip = config.get('cip_program', {})

    if not cip:
        return ""

    lines = ["## 9. CIP清洗程序\n"]
    lines.append("### 9.1 标准5步法")
    lines.append("")
    lines.append("| 步骤 | 名称 | 介质 | 温度 | 时间 | 浓度 | 目的 |")
    lines.append("|------|------|------|------|------|------|------|")

    for step in cip.get('standard_5step', []):
        lines.append(f"| {step.get('step', '-')} | {step.get('name', '-')} | {step.get('medium', '-')} | {step.get('temp', '-')} | {step.get('time', '-')} | {step.get('concentration', '-')} | {step.get('purpose', '-')} |")

    env = cip.get('environment_requirements', {})
    if env:
        lines.append("")
        lines.append("### 9.2 生产环境要求")
        lines.append("")
        lines.append("| 区域 | 洁净度 | 温度 | 湿度 | 压差 |")
        lines.append("|------|--------|------|------|------|")

        area_names = {'aseptic_area': '无菌灌装间', 'blending_area': '调配间', 'extraction_area': '萃取间', 'general_area': '一般区'}
        for area_id, area_info in env.items():
            name = area_names.get(area_id, area_id)
            lines.append(f"| {name} | {area_info.get('cleanliness', '-')} | {area_info.get('temp', '-')} | {area_info.get('humidity', '-')} | {area_info.get('pressure', '-')} |")

    lines.append("")
    return "\n".join(lines) + "\n"


def generate_material_balance(config):
    mat_bal = config.get('material_balance', {})
    cap_calc = config.get('capacity_calc', {})

    if not mat_bal and not cap_calc:
        return ""

    lines = ["## 10. 物料平衡与产能\n"]

    if cap_calc:
        lines.append("### 10.1 产能换算")
        lines.append("")
        lines.append("| 单位 | 产量 |")
        lines.append("|------|------|")
        lines.append(f"| 每秒 | {cap_calc.get('per_second', '-')}瓶 |")
        lines.append(f"| 每分钟 | {cap_calc.get('per_minute', '-')}瓶 |")
        lines.append(f"| 每小时 | {cap_calc.get('per_hour', '-')}瓶 |")
        lines.append(f"| 每日(24h) | {cap_calc.get('per_day', '-')}瓶 |")
        lines.append("")
        for note in cap_calc.get('notes', []):
            lines.append(f"> {note}")
        lines.append("")

    if mat_bal:
        batch = mat_bal.get('batch_base', {})
        if batch:
            lines.append("### 10.2 批处理基准")
            lines.append("")
            lines.append(f"**批次容量**: {batch.get('batch_size', '-')}")
            lines.append(f"**批次周期**: {batch.get('batch_duration', '-')}")
            lines.append("")

        consumption = mat_bal.get('consumption_per_batch', {})
        if consumption:
            lines.append("### 10.3 批处理物料消耗")
            lines.append("")
            lines.append("| 原料 | 用量 | 说明 |")
            lines.append("|------|------|------|")
            lines.append(f"| 茶浓缩汁 | {consumption.get('tea_concentrate', '-')} | {consumption.get('tea_concentrate_note', '-')} |")
            lines.append(f"| 糖浆(65°Bx) | {consumption.get('syrup_65bx', '-')} | - |")
            lines.append(f"| 纯水 | {consumption.get('pure_water', '-')} | - |")
            lines.append(f"| 柠檬酸(2%) | {consumption.get('citric_acid_2pct', '-')} | - |")
            lines.append(f"| 茶香精 | {consumption.get('tea_flavor', '-')} | - |")
            lines.append(f"| **合计** | {consumption.get('total', '-')} | - |")
            lines.append("")

        daily = mat_bal.get('daily_consumption', {})
        if daily:
            lines.append("### 10.4 日物料消耗(54000B/H, 24h)")
            lines.append("")
            lines.append("| 物料 | 日消耗量 |")
            lines.append("|------|----------|")
            lines.append(f"| 茶叶(绿茶) | {daily.get('tea_green', '-')} |")
            lines.append(f"| 白砂糖 | {daily.get('sugar', '-')} |")
            lines.append(f"| 柠檬酸 | {daily.get('citric_acid', '-')} |")
            lines.append(f"| PET瓶(500ml) | {daily.get('pet_bottle_500ml', '-')} |")
            lines.append(f"| 瓶盖 | {daily.get('bottle_cap', '-')} |")
            lines.append(f"| 标签 | {daily.get('label', '-')} |")
            lines.append(f"| 纸箱 | {daily.get('carton', '-')} |")
            lines.append(f"| 纯水 | {daily.get('pure_water_total', '-')} |")
            lines.append("")

        analysis = mat_bal.get('capacity_analysis', {})
        if analysis:
            lines.append("### 10.5 产能匹配分析")
            lines.append("")
            lines.append("| 项目 | 参数 |")
            lines.append("|------|------|")
            lines.append(f"| UHT处理能力 | {analysis.get('uht_capacity', '-')} |")
            lines.append(f"| 灌装能力 | {analysis.get('filler_capacity', '-')} |")
            lines.append(f"| 缓冲方案 | {analysis.get('buffer_tank', '-')} |")
            lines.append(f"| 解决方式 | {analysis.get('solution', '-')} |")
            lines.append("")

    return "\n".join(lines) + "\n"

def generate_network_config(config):
    plcs = config.get('plcs', {})
    scada = config.get('scada_components', {})

    lines = ["## 11. 网络架构配置\n"]
    lines.append("| 层级 | 协议 | 设备 |")
    lines.append("|------|------|------|")
    lines.append("| 监控层 | Ethernet TCP/IP | SCADA服务器、操作站 |")
    lines.append("| 控制层 | Ethernet/IP | PLC控制系统 |")
    lines.append("| 现场层 | Modbus RTU/TCP | 智能仪表 |")

    lines.append("")
    lines.append("### 11.1 PLC网络配置")
    lines.append("")
    lines.append("| PLC | IP地址 | 冗余 |")
    lines.append("|-----|--------|------|")
    for pid in sorted(plcs.keys()):
        p = plcs[pid]
        lines.append(f"| {pid} | {p.get('ip', 'N/A')} | {p.get('冗余方式', '无')} |")

    lines.append("")
    return "\n".join(lines) + "\n"

# ============================================================================
# 主函数
# ============================================================================
def main():
    log_info("=" * 60)
    log_info("Process_Flow_generator.py - 生产线工艺配置生成器")
    log_info("=" * 60)

    log_info(f"读取配置文件: {CONFIG_FILE}")
    config = load_yaml(CONFIG_FILE)
    log_success(f"配置加载成功: {config.get('meta', {}).get('version', 'N/A')}")

    log_info("生成生产线工艺配置文档...")

    content = generate_header(config)
    content += generate_sections_overview(config)
    content += generate_process_flow(config)
    content += generate_plc_config(config)
    content += generate_io_summary(config)
    content += generate_capacity_info(config)
    content += generate_product_config(config)
    content += generate_process_params(config)
    content += generate_ccp_config(config)
    content += generate_cip_config(config)
    content += generate_material_balance(config)
    content += generate_network_config(config)

    content += f"""
---

**文档状态**: 自动生成
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据来源**: `01_Spec/configs/system_config.yaml`
**生成器脚本**: `_generators/Process_Flow_generator.py`

**版本历史**:
- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 初始版本，基于system_config.yaml自动生成
"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    log_success(f"文档生成成功: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
