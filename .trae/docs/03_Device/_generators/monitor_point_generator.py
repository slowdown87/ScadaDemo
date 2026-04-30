"""
茶饮料生产线监控点表生成器
从 devices_*.yaml 配置文件自动生成监控点表 markdown 文档

使用方法:
    python monitor_point_generator.py

输出:
    茶饮料生产线监控点表_auto.md
"""

import os
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "configs"
OUTPUT_FILE = SCRIPT_DIR.parent / "茶饮料生产线监控点表_auto.md"

SECTION_NAMES = {
    'WT': '水处理系统',
    'TH': '茶叶前处理系统',
    'EX': '萃取系统',
    'FL': '过滤净化系统',
    'BL': '调配系统',
    'HM': '均质系统',
    'UH': 'UHT杀菌系统',
    'BF': '制瓶系统',
    'PF': '灌装系统',
    'CG': '旋盖系统',
    'LI': '灯检系统',
    'CI': '喷码系统',
    'LB': '贴标系统',
    'CA': '装箱系统',
    'PK': '冷却包装系统',
    'CP': 'CIP清洗系统',
}

DEVICE_TYPE_NAMES = {
    'tank': '储罐',
    'pump': '泵',
    'motor': '电机',
    'valve': '阀门',
    'heat_exchanger': '换热器',
    'filter': '过滤器',
    'uht': 'UHT杀菌锅',
    'filler': '灌装机',
    'packaging': '包装设备',
    'sensor': '传感器',
}

ALARM_LEVELS = {
    'LL': '低低报警',
    'L': '低报警',
    'H': '高报警',
    'HH': '高高报警',
}


def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_all_devices():
    devices = []
    config_files = [
        'devices_wt.yaml',
        'devices_th.yaml',
        'devices_ex.yaml',
        'devices_fl.yaml',
        'devices_bl.yaml',
        'devices_hm.yaml',
        'devices_uh.yaml',
        'devices_bf.yaml',
        'devices_cp.yaml',
        'devices_pf_cg.yaml',
        'devices_li.yaml',
        'devices_ci.yaml',
        'devices_lb_ca.yaml',
        'devices_pk.yaml',
    ]

    for filename in config_files:
        file_path = CONFIG_DIR / filename
        if file_path.exists():
            data = load_yaml(file_path)
            for key, device_list in data.items():
                if isinstance(device_list, list):
                    devices.extend(device_list)

    return devices


def get_section_from_id(device_id):
    if '-' in device_id:
        prefix = device_id.split('-')[0]
        if prefix in SECTION_NAMES:
            return prefix
    if device_id.startswith('P-'):
        for dev in load_all_devices():
            if dev.get('id') == device_id:
                return dev.get('section', '')
    if device_id.startswith('M-'):
        for dev in load_all_devices():
            if dev.get('id') == device_id:
                return dev.get('section', '')
    return ''


def generate_alarm_text(alarm_dict):
    if not alarm_dict:
        return '-'
    parts = []
    for level, value in alarm_dict.items():
        level_name = ALARM_LEVELS.get(level, level)
        parts.append(f"{level}:{value}")
    return ', '.join(parts)


def count_sensor_types(devices):
    counts = defaultdict(int)

    for device in devices:
        for sensor in device.get('sensors', []):
            code = sensor.get('code', '')
            sensor_type = sensor.get('type', '')

            if code.startswith('TT'):
                counts['温度传感器'] += 1
            elif code.startswith('PT') or code.startswith('PT2') or code == 'DPT':
                counts['压力传感器'] += 1
            elif code.startswith('LT'):
                counts['液位传感器'] += 1
            elif code.startswith('FT') or code.startswith('FT2'):
                counts['流量传感器'] += 1
            elif code in ['AT', 'BT', 'CtT']:
                counts['分析仪表'] += 1
            elif code.startswith('DT'):
                counts['阀门状态'] += 1
            elif code.startswith('ST'):
                counts['电机状态'] += 1
            elif code == 'WT':
                counts['重量传感器'] += 1
            else:
                counts['其他'] += 1

    return counts


def generate_summary_table(devices):
    lines = []
    lines.append("| 序号 | 监控类别 | 点位数量 | 说明 |")
    lines.append("|------|----------|----------|------|")

    counts = count_sensor_types(devices)

    category_order = [
        ('温度传感器', '温度传感器'),
        ('压力传感器', '压力传感器'),
        ('液位传感器', '液位传感器'),
        ('流量传感器', '流量传感器'),
        ('分析仪表', '分析仪表'),
        ('阀门状态', '阀门状态'),
        ('电机状态', '电机状态'),
        ('产量计数', '产量计数'),
        ('报警点', '报警点'),
    ]

    valve_count = 0
    motor_count = 0
    pump_count = 0

    for device in devices:
        valve_count += len(device.get('valves', []))
        motor_count += len(device.get('motors', []))
        if device.get('type') == 'pump':
            pump_count += 1

    counts['阀门状态'] = valve_count
    counts['泵状态'] = pump_count
    counts['电机状态'] = motor_count

    total = 0
    seq = 1
    for key, name in category_order:
        count = counts.get(key, 0)
        if count > 0:
            lines.append(f"| {seq} | {name} | {count}点 | - |")
            total += count
            seq += 1

    if counts.get('其他', 0) > 0:
        lines.append(f"| {seq} | 其他 | {counts.get('其他', 0)}点 | - |")
        total += counts.get('其他', 0)

    lines.append(f"| **合计** | - | **{total}点** | - |")

    return '\n'.join(lines)


def generate_device_sensors_table(device, section_key):
    lines = []
    device_id = device.get('id', '')
    device_name = device.get('name', '')

    sensors = device.get('sensors', [])
    if not sensors:
        return lines

    for sensor in sensors:
        code = sensor.get('code', '')
        sensor_name = sensor.get('name', '')
        sensor_type = sensor.get('type', '')
        range_list = sensor.get('range', [0, 100])
        unit = sensor.get('unit', '')
        alarm = sensor.get('alarm', {})
        note = sensor.get('note', '')
        is_key = sensor.get('is_key_point', False)

        tag = f"{device_id}-{code}"
        range_str = f"{range_list[0]}-{range_list[1]}" if range_list and len(range_list) == 2 else '-'
        alarm_str = generate_alarm_text(alarm) if alarm else '-'
        key_marker = ' **关键控制点**' if is_key else ''
        note_str = f" {note}" if note else ''

        lines.append(f"| {tag} | {sensor_name} | {sensor_type} | {range_str} | {unit} | {alarm_str} | {note_str}{key_marker} |")

    return lines


def generate_devices_section(devices, section_key, section_name, section_num):
    lines = []
    lines.append(f"### 2.{section_num} {section_name} ({section_key})")
    lines.append("")
    lines.append("| 位号 | 描述 | 类型 | 范围 | 单位 | 报警设定 | 备注 |")
    lines.append("|------|------|------|------|------|----------|------|")

    section_devices = [d for d in devices if d.get('section') == section_key]

    for device in section_devices:
        device_lines = generate_device_sensors_table(device, section_key)
        lines.extend(device_lines)

    lines.append("")
    return '\n'.join(lines)


def generate_valves_section(devices):
    lines = []
    lines.append("## 3. 阀门控制点表")
    lines.append("")
    lines.append("### 3.1 阀门汇总")
    lines.append("")
    lines.append("| 位号 | 描述 | 类型 | 控制方式 | 连锁说明 |")
    lines.append("|------|------|------|----------|----------|")

    valve_sections = defaultdict(list)
    for device in devices:
        section = device.get('section', '')
        for valve in device.get('valves', []):
            valve_entry = {
                'section': section,
                'valve': valve
            }
            valve_sections[section].append(valve_entry)

    valve_order = ['EX', 'BL', 'HM', 'UH', 'PF', 'CG', 'CP']

    for section_key in valve_order:
        if section_key not in valve_sections:
            continue

        section_name = SECTION_NAMES.get(section_key, section_key)

        for valve_entry in valve_sections[section_key]:
            valve = valve_entry['valve']
            valve_id = valve.get('id', '')
            valve_name = valve.get('name', '')
            valve_type = valve.get('type', '')
            control = valve.get('control', '-')

            lines.append(f"| {valve_id} | {valve_name} | {valve_type} | {control} | - |")

    lines.append("")
    return '\n'.join(lines)


def generate_pumps_motors_section(devices):
    lines = []
    lines.append("## 4. 泵与电机状态点表")
    lines.append("")

    lines.append("### 4.1 泵状态监控")
    lines.append("")
    lines.append("| 位号 | 描述 | 类型 | 控制 | 状态点 | 备注 |")
    lines.append("|------|------|------|------|--------|------|")

    pump_sections = defaultdict(list)
    for device in devices:
        if device.get('type') == 'pump':
            section = device.get('section', '')
            pump_sections[section].append(device)

    for section_key in ['WT', 'TH', 'EX', 'FL', 'BL', 'HM', 'UH', 'CP', 'PF', 'PK']:
        if section_key not in pump_sections:
            continue

        for pump in pump_sections[section_key]:
            pump_id = pump.get('id', '')
            pump_name = pump.get('name', '')
            pump_type = '变频泵' if pump.get('is_inverter') else '离心泵'
            control = pump.get('control', '-')

            lines.append(f"| {pump_id} | {pump_name} | {pump_type} | {control} | 运行/停止/故障 | 液位连锁 |")

    lines.append("")

    lines.append("### 4.2 电机状态监控")
    lines.append("")
    lines.append("| 位号 | 描述 | 功率(kW) | 控制方式 | 监控点 | 备注 |")
    lines.append("|------|------|----------|----------|--------|------|")

    motor_devices = []
    for device in devices:
        motors = device.get('motors', [])
        for motor in motors:
            motor['parent_device'] = device
            motor_devices.append(motor)

    for motor in motor_devices:
        motor_id = motor.get('id', '')
        motor_name = motor.get('name', '')
        power = motor.get('power_kw', '-')
        is_inverter = motor.get('is_inverter', False)
        control = '变频' if is_inverter else '直接启动'

        lines.append(f"| {motor_id} | {motor_name} | {power} | {control} | 运行/停止/故障/温度 | - |")

    lines.append("")
    return '\n'.join(lines)


def generate_counters_section():
    lines = []
    lines.append("## 5. 产量计数点表")
    lines.append("")
    lines.append("| 位号 | 描述 | 类型 | 单位 | 说明 |")
    lines.append("|------|------|------|------|------|")
    lines.append("| CNT-001 | 纯水产数量 | 累积计数 | m³ | 日/月统计 |")
    lines.append("| CNT-002 | 茶叶投料量 | 累积计数 | kg | 日/月统计 |")
    lines.append("| CNT-003 | 糖浆投料量 | 累积计数 | kg | 日/月统计 |")
    lines.append("| CNT-004 | 产品灌装量 | 累积计数 | 瓶 | 日/月统计 |")
    lines.append("| CNT-005 | 成品箱数 | 累积计数 | 箱 | 日/月统计 |")
    lines.append("| CNT-006 | 码垛数量 | 累积计数 | 托盘 | 日/月统计 |")
    lines.append("| CNT-007 | 灯检合格数 | 累积计数 | 瓶 | 质量统计 |")
    lines.append("| CNT-008 | 灯检不合格数 | 累积计数 | 瓶 | 废品统计 |")
    lines.append("| CNT-009 | 金属检测不合格 | 累积计数 | 瓶 | 废品统计 |")
    lines.append("| CNT-010 | 重量检测不合格 | 累积计数 | 瓶 | 废品统计 |")
    lines.append("")
    return '\n'.join(lines)


def generate_alarms_section():
    lines = []
    lines.append("## 6. 报警点汇总表")
    lines.append("")
    lines.append("### 6.1 报警等级定义")
    lines.append("")
    lines.append("| 等级 | 描述 | 颜色 | 声音 | 处理方式 |")
    lines.append("|------|------|------|------|----------|")
    lines.append("| LL | 低低报警 | 红色闪烁 | 连续 | 立即停机，人工处理 |")
    lines.append("| L | 低报警 | 黄色 | 断续 | 提示检查，30min内处理 |")
    lines.append("| H | 高报警 | 黄色 | 断续 | 提示检查，30min内处理 |")
    lines.append("| HH | 高高报警 | 红色闪烁 | 连续 | 立即停机，人工处理 |")
    lines.append("")
    return '\n'.join(lines)


def generate_document():
    today = datetime.now().strftime('%Y-%m-%d')

    devices = load_all_devices()

    lines = []
    lines.append("# 茶饮料生产线监控点表")
    lines.append("")
    lines.append("> 文档版本: v1.0")
    lines.append(f"> 创建日期: {today}")
    lines.append(f"> 更新日期: {today}")
    lines.append("> 数据来源: 03_Device/configs/devices_*.yaml (自动生成)")
    lines.append("> 产品类型: 纯茶饮料（绿茶/红茶/乌龙茶）- 共线生产")
    lines.append("> 产能: 50000B/H / 54000B/H")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 1. 监控点汇总")
    lines.append("")
    lines.append(generate_summary_table(devices))
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 2. 详细监控点清单")
    lines.append("")

    section_order = ['WT', 'TH', 'EX', 'FL', 'HM', 'BL', 'UH', 'BF', 'PF', 'CG', 'LI', 'CI', 'LB', 'CA', 'PK', 'CP']

    section_num = 1
    for section_key in section_order:
        if section_key not in SECTION_NAMES:
            continue
        section_name = SECTION_NAMES[section_key]
        section_lines = generate_devices_section(devices, section_key, section_name, section_num)
        if section_lines:
            lines.append(section_lines)
            lines.append("")
            lines.append("---")
            lines.append("")
            section_num += 1

    lines.append(generate_valves_section(devices))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(generate_pumps_motors_section(devices))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(generate_counters_section())
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(generate_alarms_section())
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"**文档状态**: 自动生成")
    lines.append("")
    lines.append(f"*本文档由系统自动生成，生成时间: {today}*")

    return '\n'.join(lines)


def main():
    print("茶饮料生产线监控点表生成器")
    print("-" * 40)
    print(f"配置目录: {CONFIG_DIR}")
    print(f"输出文件: {OUTPUT_FILE}")
    print("-" * 40)

    if not CONFIG_DIR.exists():
        print(f"错误: 配置目录不存在: {CONFIG_DIR}")
        return

    document = generate_document()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(document)

    print(f"生成文档: {OUTPUT_FILE}")
    print("\n完成!")


if __name__ == '__main__':
    main()