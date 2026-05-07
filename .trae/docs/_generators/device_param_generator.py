#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeviceParam_generator.py
茶饮料生产线SCADA系统 - 设备参数表文档生成器

功能: 从 system_config.yaml 读取设备定义，自动生成 设备参数表_auto.md
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "01_Spec" / "configs" / "system_config.yaml"
OUTPUT_FILE = PROJECT_ROOT / "03_Device" / "auto" / "茶饮料_设备参数表_auto.md"

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

def get_control_template(ctrl_type, templates):
    return templates.get(ctrl_type, templates.get('temperature_loop'))

def generate_device_list_table(devices):
    lines = []
    lines.append("| 设备ID | 设备名称 | 类型 | 供应商 | 规格 | 数量 |")
    lines.append("|--------|----------|------|--------|------|------|")
    for dev in devices:
        lines.append(f"| {dev.get('id', '-')} | {dev.get('name', '-')} | {dev.get('type', '-')} | {dev.get('supplier', '-')} | {dev.get('spec', '-')} | {dev.get('quantity', 1)} |")
    return "\n".join(lines)

def generate_sensor_table(devices):
    lines = []
    has_sensors = False
    for dev in devices:
        if dev.get('sensors'):
            has_sensors = True
            break
    if not has_sensors:
        return ""
    lines.append("| 设备ID | 传感器位号 | 传感器名称 | 范围 | 单位 | 报警设置 | 关键点 |")
    lines.append("|--------|------------|------------|------|------|----------|--------|")
    for dev in devices:
        for sensor in dev.get('sensors', []):
            alarm = sensor.get('alarm', {})
            if isinstance(alarm, dict):
                alarm_str = ",".join([f"{k}:{v}" for k,v in alarm.items()])
            else:
                alarm_str = str(alarm) if alarm else "-"
            is_key = "**CCP**" if sensor.get('is_key_point') else "-"
            lines.append(f"| {dev.get('id', '-')} | {sensor.get('code', '-')} | {sensor.get('name', '-')} | {sensor.get('range', '-')} | {sensor.get('unit', '-')} | {alarm_str} | {is_key} |")
    return "\n".join(lines)

def generate_control_params_section(devices, ctrl_templates, interlock_templates, process_params):
    lines = []
    lines.append("### 核心控制参数")
    lines.append("")
    lines.append("| 参数 | 设备 | 设定值 | 控制范围 | 控制精度 | 控制方式 | 报警设置 | 联锁动作 |")
    lines.append("|------|------|--------|----------|----------|----------|----------|----------|")

    for dev in devices:
        dev_id = dev.get('id', '')
        dev_name = dev.get('name', '')
        ctrl = dev.get('control', '')
        power = dev.get('power_kw', '')

        if ctrl:
            lines.append(f"| {ctrl} | {dev_name}({dev_id}) | - | - | - | {ctrl} | - | - |")
        if power:
            lines.append(f"| 功率 | {dev_name}({dev_id}) | {power}kW | - | - | {'变频' if dev.get('is_inverter') else '直接'} | - | - |")

    lines.append("")
    return "\n".join(lines)

def generate_pid_params_section(devices, ctrl_templates, process_params, sec_id):
    lines = []
    lines.append("### PID参数配置")
    lines.append("")
    lines.append("| 回路 | 被控变量 | 设定值 | Kp | Ti | Td | 控制周期 | 说明 |")
    lines.append("|------|----------|--------|----|----|----|----------|------|")

    pid_added = False
    for dev in devices:
        for sensor in dev.get('sensors', []):
            sensor_type = sensor.get('type', '')
            sensor_code = sensor.get('code', '')
            sensor_name = sensor.get('name', '')
            alarm = sensor.get('alarm', {})
            range_val = sensor.get('range', '')

            ctrl_type = None
            if '温度' in sensor_name or 'TT' in sensor_code:
                ctrl_type = 'temperature_loop'
            elif '压力' in sensor_name or 'PT' in sensor_code or ' pressure' in sensor_name.lower():
                ctrl_type = 'pressure_loop'
            elif '流量' in sensor_name or 'FT' in sensor_code:
                ctrl_type = 'flow_loop'
            elif '液位' in sensor_name or 'LT' in sensor_code:
                ctrl_type = 'level_loop'
            elif 'Brix' in sensor_name or 'BT' in sensor_code:
                ctrl_type = 'brix_loop'
            elif 'pH' in sensor_name or 'AT' in sensor_code:
                ctrl_type = 'ph_loop'

            if ctrl_type and ctrl_type in ctrl_templates:
                tpl = ctrl_templates[ctrl_type]
                setpoint = ""
                if isinstance(range_val, list) and len(range_val) == 2:
                    mid = (range_val[0] + range_val[1]) / 2
                    setpoint = str(mid)
                lines.append(f"| {sensor_code} | {sensor_name} | {setpoint} | {tpl.get('Kp', '-')} | {tpl.get('Ti', '-')}s | {tpl.get('Td', '-')}s | {tpl.get('cycle_ms', '-')}ms | {tpl.get('note', '-')} |")
                pid_added = True

    if not pid_added:
        lines.append("| - | - | - | - | - | - | - | 暂无PID控制回路 |")

    lines.append("")
    return "\n".join(lines)

def generate_ccp_section(devices, ccp_interlocks, sec_id):
    lines = []
    ccp_list = []

    for dev in devices:
        for sensor in dev.get('sensors', []):
            if sensor.get('is_key_point'):
                ccp_list.append({
                    'dev_name': dev.get('name', ''),
                    'sensor_code': sensor.get('code', ''),
                    'sensor_name': sensor.get('name', ''),
                    'alarm': sensor.get('alarm', {})
                })

    if not ccp_list:
        return ""

    lines.append("### CCP监控参数")
    lines.append("")
    lines.append("| CCP点 | 参数 | 设定值 | 临界值 | 响应时间 | 联锁动作 |")
    lines.append("|-------|------|--------|--------|----------|----------|")

    ccp_idx = 1
    for ccp in ccp_list:
        alarm = ccp['alarm']
        condition = ""
        action = ""
        delay = ""

        if isinstance(alarm, dict):
            for k, v in alarm.items():
                if k in ['L', 'LL']:
                    condition += f"<{v} "
                elif k in ['H', 'HH']:
                    condition += f">{v} "

        for key, ilock in ccp_interlocks.items():
            if ccp['sensor_code'] in ilock.get('sensor', '') or ccp['sensor_name'] in ilock.get('sensor', ''):
                action = ilock.get('action', '-')
                delay = f"{ilock.get('delay_ms', 0)}ms"

        lines.append(f"| CCP{ccp_idx} | {ccp['sensor_code']} {ccp['sensor_name']} | - | {condition.strip()} | {delay} | {action} |")
        ccp_idx += 1

    lines.append("")
    return "\n".join(lines)

def generate_process_params_section(process_params, sec_id):
    if sec_id not in process_params or not process_params[sec_id]:
        return ""

    lines = []
    lines.append("### 工艺参数表")
    lines.append("")
    lines.append("| 参数 | 设定值 | 控制范围 | 控制方式 |")
    lines.append("|------|--------|----------|----------|")

    params = process_params[sec_id].get('params', [])
    for p in params:
        lines.append(f"| {p.get('name', '-')} | {p.get('value', '-')} | {p.get('range', '-')} | {p.get('control', '-')} |")

    lines.append("")
    return "\n".join(lines)

def generate_device_param_table(config):
    meta = config['meta']
    sections = config['sections']
    plcs = config['plcs']
    devices = config.get('devices', {})
    process_params = config.get('process_params', {})
    ctrl_templates = config.get('control_templates', {})
    interlock_templates = config.get('interlock_templates', {})
    ccp_interlocks = config.get('ccp_interlocks', {})

    sorted_sections = sorted(sections.values(), key=lambda x: x.get('process_order', 0))

    doc = f"""# 茶饮料生产线设备参数表

> 文档版本: v1.0
> 创建日期: {meta['created'][:10]}
> 更新日期: {datetime.now().strftime('%Y-%m-%d')}
> 数据来源: system_config.yaml

> **本文件由系统配置自动生成 - 请勿手动修改**
>
> **注意**: PID参数为推荐值，实际调试时需根据现场情况微调

---

## 1. 概述

### 1.1 生成信息

| 项目 | 内容 |
| ---- | ---- |
| **数据来源** | `01_Spec/configs/system_config.yaml` |
| **生成器脚本** | `docs/_generators/DeviceParam_generator.py` |
| **重新生成命令** | `python docs/_generators/run_all_generators.py` |

### 1.2 工段分布

| 工段 | 名称 | PLC编号 | 控制级别 |
|------|------|---------|----------|
"""

    for section in sorted_sections:
        plc_id = section.get('plc', '')
        plc = plcs.get(plc_id, {})
        ctrl_level = "CCP" if plc.get('is_ccp') else "P1"
        doc += f"| {section.get('prefix', section.get('id', ''))} | {section.get('name', '')} | {section.get('plc', '')} | {ctrl_level} |\n"

    section_order = ['WT', 'TH', 'EX', 'FL', 'BL', 'HM', 'UH', 'BF', 'PF', 'CG', 'LI', 'CI', 'LB', 'CA', 'PK', 'CP']
    section_names = {
        'WT': '公用工程-水处理', 'TH': '液料-茶叶前处理', 'EX': '液料-萃取',
        'FL': '液料-过滤', 'BL': '液料-调配', 'HM': '液料-均质',
        'UH': '液料-UHT杀菌', 'BF': '包装-制瓶', 'PF': '包装-灌装', 'CG': '包装-旋盖',
        'LI': '包装-灯检', 'CI': '包装-喷码', 'LB': '包装-贴标',
        'CA': '包装-装箱', 'PK': '包装-膜包码垛', 'CP': '公用工程-CIP'
    }

    idx = 2
    for sec_id in section_order:
        if sec_id not in devices:
            continue
        sec_devices = devices[sec_id]
        if not sec_devices:
            continue
        section_name = section_names.get(sec_id, sections.get(sec_id, {}).get('name', sec_id))
        doc += f"""
---

## {idx}. {section_name}

### {idx}.1 设备清单

{generate_device_list_table(sec_devices)}

### {idx}.2 传感器配置

{generate_sensor_table(sec_devices)}

{generate_control_params_section(sec_devices, ctrl_templates, interlock_templates, process_params)}

{generate_pid_params_section(sec_devices, ctrl_templates, process_params, sec_id)}

{generate_ccp_section(sec_devices, ccp_interlocks, sec_id)}

{generate_process_params_section(process_params, sec_id)}
"""
        idx += 1

    doc += f"""
---

## {idx}. 设备汇总

### {idx}.1 关键传感器点位(CCP)

| 设备 | 工段 | 传感器 | 功能 |
|------|------|--------|------|
"""
    for sec_id in section_order:
        if sec_id not in devices:
            continue
        for dev in devices[sec_id]:
            for sensor in dev.get('sensors', []):
                if sensor.get('is_key_point'):
                    doc += f"| {dev.get('name', '-')} | {sec_id} | {sensor.get('code', '-')} {sensor.get('name', '-')} | {sensor.get('note', '-')} |\n"

    doc += f"""
### {idx}.2 变频设备汇总

| 设备ID | 设备名称 | 工段 | 功率 | 说明 |
|--------|----------|------|------|------|
"""
    for sec_id in section_order:
        if sec_id not in devices:
            continue
        for dev in devices[sec_id]:
            if dev.get('is_inverter'):
                doc += f"| {dev.get('id', '-')} | {dev.get('name', '-')} | {sec_id} | {dev.get('power_kw', '-')}kW | 变频控制 |\n"

    doc += f"""
---

## {idx+1}. 版本记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | {meta['created'][:10]} | 初始版本，从system_config.yaml自动生成 |

---

**文档状态**: 自动生成
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**审核状态**: 待审核
"""

    return doc

def main():
    log_info("=" * 60)
    log_info("DeviceParam_generator.py - 设备参数表生成器")
    log_info("=" * 60)

    if not CONFIG_FILE.exists():
        log_error(f"配置文件未找到: {CONFIG_FILE}")
        sys.exit(1)

    log_info(f"读取配置文件: {CONFIG_FILE}")
    config = load_yaml(CONFIG_FILE)
    log_success("配置加载成功")

    log_info("生成设备参数表文档...")
    doc = generate_device_param_table(config)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(doc)

    log_success(f"文档生成成功: {OUTPUT_FILE}")
    log_info("=" * 60)

if __name__ == "__main__":
    main()
