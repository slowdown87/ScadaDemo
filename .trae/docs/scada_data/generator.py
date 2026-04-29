"""
SCADA 文档自动生成器
茶饮料生产线 - 监控点表、联锁逻辑、CIP规格、通讯接口 自动生成

使用方法:
    python generator.py --generate <document_type> [--output <output_dir>]

参数:
    --generate     生成文档类型: all, points, interlocks, cip, comm
    --output       输出目录 (默认: ../)

示例:
    python generator.py --generate all           # 生成所有文档
    python generator.py --generate points        # 仅生成监控点表
    python generator.py --generate interlocks     # 仅生成联锁逻辑
"""

import os
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path

# ============================================================================
# 配置
# ============================================================================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR  # YAML文件在脚本同一目录

# 输出目录 (上级目录的 documents 文件夹)
OUTPUT_DIR = SCRIPT_DIR.parent

# 数据文件 (与脚本同一目录)
DEVICES_FILE = DATA_DIR / "devices.yaml"
SENSORS_FILE = DATA_DIR / "sensor_templates.yaml"
INTERLOCK_FILE = DATA_DIR / "interlock_templates.yaml"
CIP_FILE = DATA_DIR / "cip_templates.yaml"
COMM_FILE = DATA_DIR / "comm_templates.yaml"

# 输出文件 (上级目录的 documents 文件夹)
OUTPUT_POINTS = OUTPUT_DIR / "茶饮料生产线监控点表_auto.md"
OUTPUT_INTERLOCKS = OUTPUT_DIR / "联锁逻辑说明书_auto.md"
OUTPUT_CIP = OUTPUT_DIR / "CIP清洗程序规格书_auto.md"
OUTPUT_COMM = OUTPUT_DIR / "通讯接口规格书_auto.md"


# ============================================================================
# 数据加载
# ============================================================================
def load_yaml(file_path):
    """加载 YAML 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_devices():
    """获取设备数据"""
    data = load_yaml(DEVICES_FILE)
    return data.get('devices', [])


def get_pumps():
    """获取泵数据"""
    data = load_yaml(DEVICES_FILE)
    return data.get('pumps', [])


def get_motors():
    """获取电机数据"""
    data = load_yaml(DEVICES_FILE)
    return data.get('motors', [])


def get_sections():
    """获取工段定义"""
    data = load_yaml(DEVICES_FILE)
    return data.get('sections', {})


def get_sensor_templates():
    """获取传感器模板"""
    return load_yaml(SENSORS_FILE)


def get_meta():
    """获取元数据"""
    data = load_yaml(DEVICES_FILE)
    return data.get('meta', {})


# ============================================================================
# 工具函数
# ============================================================================
def format_alarm(alarm_dict):
    """格式化报警信息"""
    if not alarm_dict:
        return "-"
    parts = []
    for level, value in alarm_dict.items():
        parts.append(f"{level}:{value}")
    return ", ".join(parts)


def generate_header(doc_type, version="v1.0"):
    """生成文档头部"""
    meta = get_meta()
    now = datetime.now().strftime("%Y-%m-%d")
    return f"""# 茶饮料生产线{doc_type}

> 文档版本: {version}
> 创建日期: {now}
> 更新日期: {now}
> 数据来源: scada_data/devices.yaml (自动生成)
> 产品类型: {meta.get('product_type', '纯茶饮料')}
> 产能: {meta.get('capacity_rated', '50000B/H')} / {meta.get('capacity_max', '54000B/H')}

---
"""


# ============================================================================
# 生成器: 监控点表
# ============================================================================
def generate_tag_number(device_id, sensor_code):
    """生成完整位号"""
    if sensor_code in ['TT1', 'TT2', 'TT3', 'TT4', 'TT5', 'PT1', 'PT2', 'FT2']:
        base = device_id
    else:
        base = device_id
    return f"{base}-{sensor_code}"


def generate_points_table():
    """生成监控点表"""
    devices = get_devices()
    pumps = get_pumps()
    motors = get_motors()
    templates = get_sensor_templates()
    sections = get_sections()
    measurement_types = templates.get('measurement_types', {})

    output = []
    output.append(generate_header("监控点表"))

    # 1. 监控点汇总
    total_points = 0
    category_counts = {}

    output.append("## 1. 监控点汇总\n")
    output.append("| 序号 | 监控类别 | 点位数量 | 说明 |")
    output.append("|------|----------|----------|------|")

    categories = {
        'temperature': ('温度传感器', 0),
        'pressure': ('压力传感器', 0),
        'level': ('液位传感器', 0),
        'flow': ('流量传感器', 0),
        'analyzer': ('分析仪表', 0),
        'valve': ('阀门状态', 0),
        'pump': ('泵状态', 0),
        'motor': ('电机状态', 0),
        'count': ('产量计数', 0),
        'alarm': ('报警点', 0),
    }

    # 统计各类点位
    for device in devices:
        section = device.get('section', '')
        sensors = device.get('sensors', [])
        for sensor in sensors:
            code = sensor.get('code', '')
            if code in ['TT', 'TT1', 'TT2', 'TT3', 'TT4', 'TT5']:
                categories['temperature'] = (categories['temperature'][0], categories['temperature'][1] + 1)
            elif code in ['PT', 'PT2']:
                categories['pressure'] = (categories['pressure'][0], categories['pressure'][1] + 1)
            elif code == 'LT':
                categories['level'] = (categories['level'][0], categories['level'][1] + 1)
            elif code in ['FT', 'FT2']:
                categories['flow'] = (categories['flow'][0], categories['flow'][1] + 1)
            elif code in ['AT', 'BT', 'CtT']:
                categories['analyzer'] = (categories['analyzer'][0], categories['analyzer'][1] + 1)
            elif code == 'DT':
                categories['valve'] = (categories['valve'][0], categories['valve'][1] + 1)
            elif code == 'MT':
                categories['motor'] = (categories['motor'][0], categories['motor'][1] + 1)

    # 加上泵和电机
    categories['pump'] = ('泵状态', len(pumps))
    categories['motor'] = ('电机状态', len(motors) + categories['motor'][1])

    # 加上计数点位
    categories['count'] = ('产量计数', 10)  # CNT-001 ~ CNT-010
    categories['alarm'] = ('报警点', 55)  # 联锁逻辑中的报警点

    total = 0
    idx = 1
    for cat_key, (cat_name, count) in categories.items():
        if count > 0:
            output.append(f"| {idx} | {cat_name} | {count}点 | - |")
            total += count
            idx += 1

    output.append(f"| **合计** | - | **{total}点** | - |")
    output.append("")

    # 2. 按工段生成详细监控点
    output.append("---\n")
    output.append("\n## 2. 详细监控点清单\n")

    section_order = ['WT', 'TH', 'EX', 'FL', 'BL', 'HM', 'UH', 'CP', 'PF', 'PK']

    for section_code in section_order:
        section_info = sections.get(section_code, {})
        section_name = section_info.get('name', section_code)
        output.append(f"### 2.{section_order.index(section_code)+1} {section_name} ({section_code})\n")

        # 查找该工段的设备
        section_devices = [d for d in devices if d.get('section') == section_code]

        if section_devices:
            output.append("| 位号 | 描述 | 类型 | 范围 | 单位 | 报警设定 | 备注 |")
            output.append("|------|------|------|------|------|----------|------|")

            for device in section_devices:
                device_id = device.get('id', '')
                device_name = device.get('name', '')
                sensors = device.get('sensors', [])

                for sensor in sensors:
                    code = sensor.get('code', '')
                    name = sensor.get('name', '')
                    sensor_type = sensor.get('type', '')
                    range_vals = sensor.get('range', [0, 100])
                    unit = sensor.get('unit', '')
                    alarm = sensor.get('alarm', {})
                    note = sensor.get('note', '')
                    is_key = sensor.get('is_key_point', False)

                    tag = generate_tag_number(device_id, code)
                    desc = f"{device_name}{name}"
                    range_str = f"{range_vals[0]}-{range_vals[1]}" if range_vals else "-"
                    alarm_str = format_alarm(alarm)
                    note_str = "**关键控制点**" if is_key else note

                    output.append(f"| {tag} | {desc} | {sensor_type} | {range_str} | {unit} | {alarm_str} | {note_str} |")

            output.append("")
        else:
            output.append("*（该工段无监控点位）*\n\n")

    # 3. 阀门控制点表
    output.append("---\n\n")
    output.append("## 3. 阀门控制点表\n")

    # 按工段分组阀门
    for section_code in section_order:
        section_info = sections.get(section_code, {})
        section_name = section_info.get('name', '')
        section_devices = [d for d in devices if d.get('section') == section_code]

        valves_found = []
        for device in section_devices:
            valves = device.get('valves', [])
            valves_found.extend(valves)

        if valves_found:
            output.append(f"### 3.{section_order.index(section_code)+1} {section_name}阀门\n")
            output.append("| 位号 | 描述 | 类型 | 控制方式 | 连锁说明 |")
            output.append("|------|------|------|----------|----------|")

            for valve in valves_found:
                valve_id = valve.get('id', '')
                valve_name = valve.get('name', '')
                valve_type = valve.get('type', '')
                control = valve.get('control', '')

                output.append(f"| {valve_id} | {valve_name} | {valve_type} | {control} | - |")

            output.append("")

    # 4. 泵与电机状态点表
    output.append("---\n\n")
    output.append("## 4. 泵与电机状态点表\n")

    output.append("### 4.1 泵状态监控\n")
    output.append("| 位号 | 描述 | 类型 | 控制 | 状态点 | 备注 |")
    output.append("|------|------|------|------|--------|------|")

    for pump in pumps:
        pump_id = pump.get('id', '')
        pump_name = pump.get('name', '')
        section = pump.get('section', '')
        control = pump.get('control', '')

        output.append(f"| {pump_id} | {pump_name} | 变频泵 | 自动 | 运行/停止/故障 | {control} |")

    output.append("")

    output.append("### 4.2 电机状态监控\n")
    output.append("| 位号 | 描述 | 功率(kW) | 控制方式 | 监控点 | 备注 |")
    output.append("|------|------|----------|----------|--------|------|")

    for motor in motors:
        motor_id = motor.get('id', '')
        motor_name = motor.get('name', '')
        power = motor.get('power_kw', '-')
        inverter = motor.get('is_inverter', False)
        control = "变频" if inverter else "直接启动"

        output.append(f"| {motor_id} | {motor_name} | {power} | {control} | 运行/停止/故障/温度 | - |")

    output.append("")

    # 5. 产量计数点表
    output.append("---\n\n")
    output.append("## 5. 产量计数点表\n")

    output.append("| 位号 | 描述 | 类型 | 单位 | 说明 |")
    output.append("|------|------|------|------|------|")

    count_tags = [
        ("CNT-001", "纯水产数量", "累积计数", "m³", "日/月统计"),
        ("CNT-002", "茶叶投料量", "累积计数", "kg", "日/月统计"),
        ("CNT-003", "糖浆投料量", "累积计数", "kg", "日/月统计"),
        ("CNT-004", "产品灌装量", "累积计数", "瓶", "日/月统计"),
        ("CNT-005", "成品箱数", "累积计数", "箱", "日/月统计"),
        ("CNT-006", "码垛数量", "累积计数", "托盘", "日/月统计"),
        ("CNT-007", "灯检合格数", "累积计数", "瓶", "质量统计"),
        ("CNT-008", "灯检不合格数", "累积计数", "瓶", "废品统计"),
        ("CNT-009", "金属检测不合格", "累积计数", "瓶", "废品统计"),
        ("CNT-010", "重量检测不合格", "累积计数", "瓶", "废品统计"),
    ]

    for tag, name, type_, unit, desc in count_tags:
        output.append(f"| {tag} | {name} | {type_} | {unit} | {desc} |")

    output.append("")

    # 6. 报警点汇总表
    output.append("---\n\n")
    output.append("## 6. 报警点汇总表\n")

    output.append("### 6.1 报警等级定义\n")
    output.append("| 等级 | 描述 | 颜色 | 声音 | 处理方式 |")
    output.append("|------|------|------|------|----------|")

    alarm_defs = [
        ("LL", "低低报警", "红色闪烁", "连续", "立即停机，人工处理"),
        ("L", "低报警", "黄色", "断续", "提示检查，30min内处理"),
        ("H", "高报警", "黄色", "断续", "提示检查，30min内处理"),
        ("HH", "高高报警", "红色闪烁", "连续", "立即停机，人工处理"),
    ]

    for level, name, color, sound, response in alarm_defs:
        output.append(f"| {level} | {name} | {color} | {sound} | {response} |")

    output.append("")

    # 文档状态
    output.append("---\n\n")
    output.append("**文档状态**: 自动生成\n")
    output.append("**版本历史**:\n")
    output.append(f"- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本\n")

    return "\n".join(output)


def get_interlock_templates():
    """获取联锁模板"""
    return load_yaml(INTERLOCK_FILE)


def get_cip_templates():
    """获取CIP模板"""
    return load_yaml(CIP_FILE)


def generate_interlocks_table():
    """生成联锁逻辑说明书"""
    interlock_data = get_interlock_templates()
    meta = interlock_data.get('meta', {})
    interlock_levels = interlock_data.get('interlock_levels', {})
    interlock_templates_data = interlock_data.get('interlock_templates', {})
    operation_interlocks = interlock_data.get('operation_interlocks', {})
    esd_interlocks = interlock_data.get('esd_interlocks', {})
    reset_permissions = interlock_data.get('reset_permissions', [])
    reset_flow = interlock_data.get('reset_flow', '')
    interlock_summary = interlock_data.get('interlock_summary', [])

    output = []
    output.append(f"""# {meta.get('project_name', '茶饮料生产线SCADA系统')}联锁逻辑说明书

> 文档版本: {meta.get('version', 'v1.0')}
> 创建日期: {meta.get('created', '2026-04-28')}
> 更新日期: {datetime.now().strftime('%Y-%m-%d')}
> 项目名称: {meta.get('project_name', '')}
> 产品类型: {meta.get('product_type', '纯茶饮料')}
> 产能: {meta.get('capacity_rated', '50000B/H')} / {meta.get('capacity_max', '54000B/H')}

---""")

    # 1. 概述
    output.append("## 1. 概述")
    output.append("### 1.1 文档目的")
    output.append("本文档定义茶饮料生产线SCADA系统中所有安全联锁和操作联锁的逻辑关系，作为PLC程序开发和SCADA组态的依据。")
    output.append("### 1.2 联锁分类")
    output.append("| 类别 | 说明 | 响应要求 |")
    output.append("|------|------|----------|")
    output.append("| 安全联锁(ESD) | 涉及人员安全、设备安全的紧急联锁 | 立即执行，无需确认 |")
    output.append("| 关键控制联锁 | 食品安全、产品质量关键点的联锁 | 立即执行，报警提示 |")
    output.append("| 操作联锁 | 防止误操作的程序联锁 | 禁止执行，提示原因 |")
    output.append("| 顺序联锁 | 批次生产、程序切换的逻辑联锁 | 按逻辑执行 |")

    # 1.3 联锁级别定义
    output.append("### 1.3 联锁级别定义")
    output.append("| 级别 | 名称 | 颜色 | 声音 | 响应时间 | 处理方式 |")
    output.append("|------|------|------|------|----------|----------|")
    for level, info in interlock_levels.items():
        output.append(f"| {level} | {info.get('name', '')} | {info.get('color', '')} | {info.get('sound', '')} | {info.get('response_time', '')} | {info.get('action', '')} |")

    # 2. 紧急停止联锁(ESD)
    output.append("---")
    output.append("## 2. 紧急停止联锁(ESD)")
    output.append("### 2.1 紧急停止触发条件")
    output.append("| 触发源 | 位置 | 动作级别 |")
    output.append("|--------|------|----------|")
    for trigger in esd_interlocks.get('trigger_sources', []):
        output.append(f"| {trigger.get('source', '')} | {trigger.get('location', '')} | {trigger.get('level', '')} |")

    output.append("### 2.2 紧急停止动作矩阵")
    output.append("| 触发 → | 停止设备 | 关闭阀门 | 启动动作 | 复位方式 |")
    output.append("|--------|----------|----------|----------|----------|")
    for action in esd_interlocks.get('action_matrix', []):
        output.append(f"| {action.get('trigger', '')} | {action.get('stop_devices', '')} | {action.get('close_valves', '')} | {action.get('start_actions', '')} | {action.get('reset_mode', '')} |")

    # 3-10. 各工段联锁
    section_order = ['UH', 'EX', 'HM', 'BL', 'PF', 'WT', 'CP', 'FL']

    for section_code in section_order:
        if section_code not in interlock_templates_data:
            continue

        section_data = interlock_templates_data[section_code]
        section_name = section_data.get('name', section_code)
        section_index = section_data.get('section_index', section_order.index(section_code) + 3)
        interlocks = section_data.get('interlocks', [])

        output.append("---")
        output.append(f"## {section_index}. {section_name}联锁")

        # 关键控制点说明
        if section_data.get('critical_points_desc'):
            output.append(f"### {section_index}.1 关键控制点")
            output.append(section_data.get('critical_points_desc', ''))

        # 联锁因果表
        output.append(f"### {section_index}.2 联锁因果表")
        output.append("| 序号 | 触发条件 | 报警级别 | 联锁动作 | 复位条件 |")
        output.append("|------|----------|----------|----------|----------|")

        for ilock in interlocks:
            ilock_id = ilock.get('id', '')
            trigger_desc = ilock.get('trigger_desc', '')
            level = ilock.get('level', '')
            alarm_level = ilock.get('alarm_level', '')
            actions = ilock.get('actions', [])
            reset = ilock.get('reset_condition', '')

            level_display = f"{alarm_level} ({level})" if alarm_level else level
            actions_str = "<br>".join(actions) if actions else "-"

            output.append(f"| {ilock_id} | {trigger_desc} | {level_display} | {actions_str} | {reset} |")

        # 启动允许条件
        start_conditions = section_data.get('start_conditions', [])
        if start_conditions:
            output.append(f"### {section_index}.3 启动允许条件")
            output.append("| 条件 | 要求 | 检查点 |")
            output.append("|------|------|--------|")
            for cond in start_conditions:
                output.append(f"| {cond.get('condition', '')} | {cond.get('requirement', '')} | {cond.get('check_point', '')} |")

        # 萃取顺序控制
        if section_data.get('sequence_control'):
            output.append(f"### {section_index}.3 顺序控制")
            output.append("```")
            output.append(section_data.get('sequence_control', ''))
            output.append("```")

        # 灌装速度同步
        speed_sync = section_data.get('speed_sync', [])
        if speed_sync:
            output.append(f"### {section_index}.3 速度同步逻辑")
            output.append("| 设备 | 基准速度 | 同步方式 | 允许偏差 |")
            output.append("|------|----------|----------|----------|")
            for sync in speed_sync:
                output.append(f"| {sync.get('device', '')} | {sync.get('base_speed', '')} | {sync.get('sync_mode', '')} | {sync.get('tolerance', '')} |")

        # CIP清洗允许条件
        allow_conditions = section_data.get('allow_conditions', [])
        if allow_conditions:
            output.append(f"### {section_index}.1 清洗允许条件")
            output.append("| 条件 | 要求 | 说明 |")
            output.append("|------|------|------|")
            for cond in allow_conditions:
                output.append(f"| {cond.get('condition', '')} | {cond.get('requirement', '')} | {cond.get('note', '')} |")

    # 11. 操作联锁（防止误操作）
    output.append("---")
    output.append("## 11. 操作联锁（防止误操作）")

    valve_ops = operation_interlocks.get('valve_operations', [])
    if valve_ops:
        output.append("### 11.1 阀门操作联锁")
        output.append("| 操作 | 允许条件 | 禁止条件 | 提示信息 |")
        output.append("|------|----------|----------|----------|")
        for op in valve_ops:
            output.append(f"| {op.get('valve', '')} {op.get('name', '')} | {op.get('allow_condition', '')} | {op.get('forbid_condition', '')} | {op.get('message', '')} |")

    motor_ops = operation_interlocks.get('motor_start_conditions', [])
    if motor_ops:
        output.append("### 11.2 电机启动联锁")
        output.append("| 电机 | 前置条件 | 禁止条件 |")
        output.append("|------|----------|----------|")
        for op in motor_ops:
            output.append(f"| {op.get('motor', '')} {op.get('name', '')} | {op.get('allow_condition', '')} | {op.get('forbid_condition', '')} |")

    # 12. 联锁复位与确认
    output.append("---")
    output.append("## 12. 联锁复位与确认")
    output.append("### 12.1 复位权限")
    output.append("| 级别 | 复位权限 | 确认要求 |")
    output.append("|------|----------|----------|")
    for perm in reset_permissions:
        output.append(f"| {perm.get('level', '')} | {perm.get('reset_authority', '')} | {perm.get('confirm_requirement', '')} |")

    output.append("### 12.2 复位流程")
    output.append("```")
    output.append(reset_flow.strip() if isinstance(reset_flow, str) else "")
    output.append("```")

    # 13. 联锁点汇总表
    output.append("---")
    output.append("## 13. 联锁点汇总表")
    output.append("| 工段 | L0级 | L1级 | L2级 | L3级 | 合计 |")
    output.append("|------|------|------|------|------|------|")

    total_l0 = total_l1 = total_l2 = total_l3 = 0
    for summary in interlock_summary:
        l0 = summary.get('l0', 0)
        l1 = summary.get('l1', 0)
        l2 = summary.get('l2', 0)
        l3 = summary.get('l3', 0)
        total = l0 + l1 + l2 + l3
        total_l0 += l0
        total_l1 += l1
        total_l2 += l2
        total_l3 += l3
        output.append(f"| {summary.get('section', '')} | {l0} | {l1} | {l2} | {l3} | {total} |")

    output.append(f"| **合计** | **{total_l0}** | **{total_l1}** | **{total_l2}** | **{total_l3}** | **{total_l0+total_l1+total_l2+total_l3}** |")

    # 文档状态
    output.append("---")
    output.append("**文档状态**: 自动生成")
    output.append("**版本历史**:")
    output.append(f"- v1.0 ({meta.get('created', '2026-04-28')}): 初始版本")
    output.append(f"- v1.1 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本")

    return "\n".join(output)


def generate_cip_spec():
    """生成CIP清洗程序规格书"""
    cip_data = get_cip_templates()
    meta = cip_data.get('meta', {})
    cip_system = cip_data.get('cip_system', {})
    cleaning_agents = cip_data.get('cleaning_agents', {})
    cleaning_zones = cip_data.get('cleaning_zones', {})
    cip_programs = cip_data.get('cip_programs', {})
    product_switch = cip_data.get('product_switch_matrix', [])
    acceptance = cip_data.get('acceptance_standards', {})
    water_spec = cip_data.get('water_specifications', {})

    output = []
    output.append(generate_header("CIP清洗程序规格书"))

    # 1. CIP系统配置
    output.append("## 1. CIP系统配置")
    stations = cip_system.get('stations', [])
    pumps = cip_system.get('pumps', [])

    output.append("| 设备 | 规格 | 数量 |")
    output.append("|------|------|------|")

    for station in stations:
        output.append(f"| {station.get('id', '')} | {station.get('name', '')}, {station.get('volume_m3', '')}m³, {station.get('tank_type', '')} | 1 |")

    for pump in pumps:
        output.append(f"| {pump.get('id', '')} | {pump.get('name', '')} | 1 |")

    # 2. 清洗剂规格
    output.append("---")
    output.append("## 2. 清洗剂规格")
    output.append("| 清洗剂 | 浓度 | 温度 | 时间 | 适用对象 |")
    output.append("|--------|------|------|------|----------|")

    for agent_key, agent in cleaning_agents.items():
        conc = agent.get('concentration_default', '-')
        conc_unit = agent.get('concentration_unit', '')
        temp = agent.get('temp_default', '-')
        time_val = agent.get('time_default', '-')
        time_unit = agent.get('unit', '')
        applicable = agent.get('applicable', '')

        conc_str = f"{conc}{conc_unit}" if conc != '-' else '-'
        temp_str = f"{temp}℃" if isinstance(temp, (int, float)) else str(temp)
        time_str = f"{time_val}{time_unit}" if time_val != '-' else '-'

        output.append(f"| {agent.get('name', agent_key)} | {conc_str} | {temp_str} | {time_str} | {applicable} |")

    # 3. 清洗区域
    output.append("---")
    output.append("## 3. 清洗区域划分")
    output.append("| 区域 | 清洗对象 | 清洗程序 | 频率 |")
    output.append("|------|----------|----------|------|")

    for zone_key, zone in cleaning_zones.items():
        target = ", ".join(zone.get('target_devices', [])) if isinstance(zone.get('target_devices'), list) else zone.get('target_devices', '')
        output.append(f"| {zone_key}区 | {zone.get('description', '')} | {zone.get('cip_program', '')} | {zone.get('frequency', '')} |")

    # 4. 各工段清洗程序
    program_order = ['CIP-WT', 'CIP-EX', 'CIP-FL', 'CIP-BL', 'CIP-UH', 'CIP-PF']

    output.append("---")
    output.append("## 4. 各工段清洗程序详细规格")

    for idx, prog_key in enumerate(program_order, 1):
        if prog_key not in cip_programs:
            continue

        prog = cip_programs[prog_key]
        output.append(f"### 4.{idx} {prog.get('name', prog_key)}")
        output.append(f"**清洗对象**: {prog.get('description', '')}")
        output.append("**清洗触发条件**:")
        for trigger in prog.get('trigger_conditions', []):
            output.append(f"- {trigger}")
        output.append("**清洗矩阵**:")
        output.append("| 步骤 | 介质 | 温度 | 时间 | 验收标准 |")
        output.append("|------|------|------|------|----------|")

        for step in prog.get('steps', []):
            step_num = step.get('step', '')
            medium = step.get('medium', '-')
            temp = step.get('temp', '-')
            time_min = step.get('time_min', '-')
            standard = step.get('standard', '-')

            temp_str = f"{temp}℃" if isinstance(temp, (int, float)) else str(temp)

            output.append(f"| {step_num} | {medium} | {temp_str} | {time_min}min | {standard} |")

        notes = prog.get('notes', [])
        if notes:
            output.append("**注意事项**:")
            for note in notes:
                output.append(f"- {note}")

    # 5. 清洗程序选择矩阵
    output.append("---")
    output.append("## 5. 清洗程序选择矩阵")
    output.append("| 当前产品 | 目标产品 | 清洗程序 | 清洗时间 |")
    output.append("|----------|----------|----------|----------|")

    for switch in product_switch:
        programs = ", ".join(switch.get('programs', []))
        time_h = switch.get('estimated_time_h', '-')
        output.append(f"| {switch.get('current_product', '')} | {switch.get('target_product', '')} | {programs} | 约{time_h}小时 |")

    # 6. 清洗验收标准
    output.append("---")
    output.append("## 6. 清洗验收标准")
    output.append("| 检测项目 | 标准 | 检测方法 |")
    output.append("|----------|------|----------|")

    for key, spec in acceptance.items():
        method = spec.get('method', '-')
        standard = spec.get('standard', '-')
        output.append(f"| {key} | {standard} | {method} |")

    # 7. 清洗用水规格
    output.append("---")
    output.append("## 7. 清洗用水规格")
    output.append("| 用途 | 水质要求 | 说明 |")
    output.append("|------|----------|------|")

    for usage, spec in water_spec.items():
        water_type = spec.get('type', '-')
        note = spec.get('conductivity_max', spec.get('microbiology_max', '-'))
        output.append(f"| {usage} | {water_type} | {note} |")

    # 文档状态
    output.append("---")
    output.append("**文档状态**: 自动生成")
    output.append("**版本历史**:")
    output.append(f"- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本")

    return "\n".join(output)


def get_comm_templates():
    """获取通讯模板"""
    return load_yaml(COMM_FILE)


def generate_comm_spec():
    """生成通讯接口规格书"""
    comm_data = get_comm_templates()
    meta = comm_data.get('meta', {})
    plc_config = comm_data.get('plc_config', [])
    protocol_params = comm_data.get('protocol_params', {})
    smart_devices = comm_data.get('smart_devices', {})
    third_party = comm_data.get('third_party_interfaces', {})
    ip_planning = comm_data.get('ip_planning', {})
    serial_ports = comm_data.get('serial_ports', [])
    port_summary = comm_data.get('port_summary', [])
    diagnostics = comm_data.get('comm_diagnostics', {})
    fault_log = comm_data.get('fault_log_format', [])

    output = []
    output.append(f"""# {meta.get('project_name', '茶饮料生产线SCADA系统')}通讯接口规格书

> 文档版本: {meta.get('version', 'v1.0')}
> 创建日期: {meta.get('created', '2026-04-28')}
> 更新日期: {datetime.now().strftime('%Y-%m-%d')}
> 项目名称: {meta.get('project_name', '')}
> 产品类型: {meta.get('product_type', '纯茶饮料')}
> 产能: {meta.get('capacity_rated', '')} / {meta.get('capacity_max', '')}

---""")

    # 1. 概述
    output.append("## 1. 概述")
    output.append("### 1.1 文档目的")
    output.append("本文档定义SCADA系统与PLC、智能仪表、第三方系统之间的通讯接口规格，作为系统集成和调试的依据。")
    output.append("### 1.2 通讯架构")
    output.append("```")
    output.append("┌─────────────────────────────────────────────────────────────────┐")
    output.append("│                        SCADA系统                                 │")
    output.append("│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │")
    output.append("│  │ OPC UA Server │  │ Modbus TCP  │  │ 串口通讯    │            │")
    output.append("│  │ (MES对接)    │  │ (仪表)      │  │ (瓶盖等)   │            │")
    output.append("│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │")
    output.append("└─────────┼────────────────┼────────────────┼─────────────────────┘")
    output.append("          │                │                │")
    output.append("          ▼                ▼                ▼")
    output.append("    ┌──────────┐    ┌──────────┐    ┌──────────┐")
    output.append("    │  MES系统  │    │ 智能仪表  │    │ 瓶盖供应  │")
    output.append("    └──────────┘    └──────────┘    └──────────┘")
    output.append("```")

    # 1.3 通讯资源统计
    output.append("### 1.3 通讯资源统计")
    output.append("| 协议 | 设备数量 | 点位数量 | 备注 |")
    output.append("|------|----------|----------|------|")
    output.append(f"| Ethernet/IP (PLC) | {len(plc_config)} | 2000点/PLC | S7-1500冗余 |")
    output.append(f"| Modbus TCP | 6 | 48点 | 电能表、流量计等 |")
    output.append(f"| Modbus RTU | {len(smart_devices.get('modbus_rtu_devices', {}).get('flowmeters', {}).get('devices', [])) + len(smart_devices.get('modbus_rtu_devices', {}).get('conductivity_meters', {}).get('devices', []))} | 112点 | 串口通讯 |")
    output.append(f"| HART | {len(smart_devices.get('hart_devices', {}).get('ph_meters', {}).get('devices', []))} | {len(smart_devices.get('hart_devices', {}).get('ph_meters', {}).get('devices', []))}点 | pH计 |")
    output.append(f"| OPC UA | 1 | 200点 | MES系统对接 |")
    output.append(f"| TCP/IP | 2 | 16点 | 贴标机、喷码机 |")
    output.append(f"| 串口RS485 | 1 | 2点 | 瓶盖计数器 |")

    # 2. PLC通讯规格
    output.append("---")
    output.append("## 2. PLC通讯规格")
    output.append("### 2.1 PLC配置")
    output.append("| PLC | 型号 | IP地址 | 控制区域 | 冗余 |")
    output.append("|-----|------|--------|----------|------|")
    for plc in plc_config:
        sections = "/".join(plc.get('section_names', []))
        output.append(f"| {plc.get('id', '')} | {plc.get('name', '')} | {plc.get('ip', '')} | {sections} | {'是' if plc.get('redundant') else '否'} |")

    output.append("### 2.2 Ethernet/IP通讯参数")
    eth_params = protocol_params.get('ethernet_ip', {})
    output.append("| 参数 | 规格 |")
    output.append("|------|------|")
    output.append(f"| 协议 | {eth_params.get('name', '')} |")
    output.append(f"| 扫描周期 | {eth_params.get('scan_cycle', '')} |")
    output.append(f"| 通讯冗余 | {eth_params.get('redundancy', '')} |")
    output.append(f"| 单PLC数据量 | {eth_params.get('points_per_plc', '')}点 |")
    output.append(f"| 超时处理 | {eth_params.get('timeout', '')} |")

    output.append("### 2.3 数据点位规划")
    for plc in plc_config:
        output.append(f"**{plc.get('id', '')} 数据区 ({'/'.join(plc.get('section_names', []))}):**")
        output.append("| 数据类型 | 地址区 | 点数 | 说明 |")
        output.append("|----------|--------|------|------|")
        data_area = plc.get('data_area', {})
        for type_key, type_data in data_area.items():
            type_names = {'di': 'DI (开关输入)', 'do': 'DO (开关输出)', 'ai': 'AI (模拟输入)', 'ao': 'AO (模拟输出)'}
            output.append(f"| {type_names.get(type_key, type_key)} | {type_data.get('start', '')} - {type_data.get('end', '')} | {type_data.get('points', '')} | {type_data.get('desc', '')} |")
        output.append("")

    # 3. 智能仪表通讯规格
    output.append("---")
    output.append("## 3. 智能仪表通讯规格")

    modbus_rtu = smart_devices.get('modbus_rtu_devices', {})
    output.append("### 3.1 Modbus RTU 通讯 (115.2kbps)")
    output.append("**流量计 (Modbus RTU, 9600,8,N,1):**")
    flowmeters = modbus_rtu.get('flowmeters', {})
    output.append(f"| 参数 | 值 |")
    output.append(f"|------|---|")
    output.append(f"| 通讯参数 | {flowmeters.get('baudrate', 9600)},8,N,1 |")
    output.append(f"| 寄存器地址 | {flowmeters.get('register', 40001)} (保持寄存器) |")
    output.append(f"| 功能码 | {flowmeters.get('function_code', 3)} (读保持寄存器) |")
    output.append(f"| 数据格式 | {flowmeters.get('data_format', '浮点数(IEEE754)')} |")
    output.append("")
    output.append("| 位号 | 设备 | 地址 | 寄存器 | 说明 |")
    output.append("|------|------|------|--------|------|")
    for dev in flowmeters.get('devices', []):
        output.append(f"| {dev.get('tag', '')} | {dev.get('desc', '')} | {dev.get('addr', ''):02d} | {flowmeters.get('register', 40001)} | {dev.get('unit', '')} |")

    output.append("")
    output.append("**电导率仪 (Modbus RTU):**")
    conductivity = modbus_rtu.get('conductivity_meters', {})
    output.append(f"| 参数 | 值 |")
    output.append(f"|------|---|")
    output.append(f"| 通讯参数 | {conductivity.get('baudrate', 9600)},8,N,1 |")
    output.append(f"| 寄存器地址 | {conductivity.get('register', 40001)} |")
    output.append(f"| 功能码 | {conductivity.get('function_code', 3)} |")
    output.append("")
    output.append("| 位号 | 设备 | 地址 | 寄存器 | 说明 |")
    output.append("|------|------|------|--------|------|")
    for dev in conductivity.get('devices', []):
        output.append(f"| {dev.get('tag', '')} | {dev.get('desc', '')} | {dev.get('addr', ''):02d} | {conductivity.get('register', 40001)} | {dev.get('unit', '')} |")

    hart = smart_devices.get('hart_devices', {})
    output.append("### 3.2 HART协议通讯")
    ph_meters = hart.get('ph_meters', {})
    output.append("**pH计 (HART):**")
    output.append(f"| 参数 | 值 |")
    output.append(f"|------|---|")
    output.append(f"| 协议 | {ph_meters.get('protocol', 'HART 7.x')} |")
    output.append(f"| 轮询地址 | {ph_meters.get('polling_addr', 0)} |")
    output.append(f"| 主变量 | {ph_meters.get('primary_var', 'pH值 (0-14)')} |")
    output.append(f"| 副变量 | {ph_meters.get('secondary_var', '温度')} |")
    output.append(f"| 扫描周期 | {ph_meters.get('scan_cycle', '1秒')} |")
    output.append("")
    output.append("| 位号 | 设备 | 地址 | 说明 |")
    output.append("|------|------|------|------|")
    for dev in ph_meters.get('devices', []):
        output.append(f"| {dev.get('tag', '')} | {dev.get('desc', '')} | {dev.get('addr', '')} | - |")

    modbus_tcp = smart_devices.get('modbus_tcp_devices', {})
    output.append("### 3.3 Modbus TCP 通讯")
    power_meters = modbus_tcp.get('power_meters', {})
    output.append("**电能表 (Modbus TCP):**")
    output.append(f"| 参数 | 值 |")
    output.append(f"|------|---|")
    output.append(f"| IP地址 | {power_meters.get('ip_range', '192.168.1.31 - 36')} |")
    output.append(f"| 端口 | {power_meters.get('port', 502)} |")
    output.append(f"| 设备ID | {power_meters.get('device_id', '1-6')} |")
    output.append(f"| 寄存器 | {power_meters.get('register_start', 40001)}起 |")
    output.append("")
    output.append("| 位号 | 设备 | IP | 监控内容 |")
    output.append("|------|------|-----|----------|")
    for dev in power_meters.get('devices', []):
        output.append(f"| {dev.get('tag', '')} | {dev.get('desc', '')} | {dev.get('ip', '')} | kWh, kVARh |")
    output.append("")
    output.append("**Modbus TCP寄存器定义:**")
    output.append("| 寄存器 | 参数 | 数据类型 |")
    output.append("|--------|------|----------|")
    for reg in power_meters.get('registers', []):
        output.append(f"| {reg.get('addr', '')} | {reg.get('param', '')} | {reg.get('type', '')} |")

    # 4. 第三方系统接口
    output.append("---")
    output.append("## 4. 第三方系统接口规格")

    mes = third_party.get('mes_opcua', {})
    output.append("### 4.1 MES系统接口 (OPC UA)")
    output.append("**接口概述:**")
    output.append("| 项目 | 规格 |")
    output.append("|------|------|")
    output.append(f"| 协议 | {mes.get('protocol', 'OPC UA Client/Server')} |")
    output.append(f"| 方向 | {mes.get('direction', '')} |")
    output.append(f"| 订阅模式 | {mes.get('subscription_mode', '')} |")
    output.append(f"| 数据量 | 约{mes.get('data_count', '')}点位 |")
    output.append("")
    output.append("**服务器端点:**")
    output.append("```")
    output.append(mes.get('endpoint', 'opc.tcp://SCADA-SERVER:4840/SCADA/MESInterface'))
    output.append("```")
    output.append("")
    output.append("**安全策略:**")
    output.append("| 参数 | 值 |")
    output.append("|------|------|")
    output.append(f"| 安全模式 | {mes.get('security_mode', 'SignAndEncrypt')} |")
    output.append(f"| 策略 | {mes.get('security_policy', 'Basic256Sha256')} |")
    output.append(f"| 认证方式 | {mes.get('auth_method', '用户名密码')} |")
    output.append(f"| 证书 | {mes.get('certificate', 'X.509v3')} |")
    output.append("")
    output.append("**MES订阅点位表:**")
    output.append("| 位号 | 描述 | 数据类型 | 更新方式 |")
    output.append("|------|------|----------|----------|")
    for pt in mes.get('read_points', []):
        output.append(f"| {pt.get('tag', '')} | {pt.get('desc', '')} | {pt.get('type', '')} | {pt.get('mode', '')} |")
    output.append("")
    output.append("**写入点位表 (MES→SCADA):**")
    output.append("| 位号 | 描述 | 数据类型 | 说明 |")
    output.append("|------|------|----------|------|")
    for pt in mes.get('write_points', []):
        output.append(f"| {pt.get('tag', '')} | {pt.get('desc', '')} | {pt.get('type', '')} | {pt.get('trigger', pt.get('values', ''))} |")

    energy = third_party.get('energy_modbus_tcp', {})
    output.append("### 4.2 能源管理系统接口 (Modbus TCP)")
    output.append("**接口概述:**")
    output.append("| 项目 | 规格 |")
    output.append("|------|------|")
    output.append(f"| 协议 | {energy.get('protocol', 'Modbus TCP')} |")
    output.append(f"| 方向 | {energy.get('direction', '')} |")
    output.append(f"| SCADA作为 | {energy.get('scada_role', 'Server')} |")
    output.append(f"| 数据量 | 约{energy.get('data_count', '')}点位 |")
    output.append("")
    output.append("**SCADA作为Server的寄存器定义:**")
    output.append("| 寄存器 | 参数 | 数据类型 | 说明 |")
    output.append("|--------|------|----------|------|")
    for reg in energy.get('registers', []):
        unit = reg.get('unit', '')
        desc = reg.get('desc', '')
        output.append(f"| {reg.get('addr', '')} | {reg.get('param', '')} | {reg.get('type', '')} | {desc} {unit} |")

    bottle_cap = third_party.get('bottle_cap_serial', {})
    output.append("### 4.3 瓶盖供应系统接口 (串口)")
    output.append("**接口概述:**")
    output.append("| 项目 | 规格 |")
    output.append("|------|------|")
    output.append(f"| 协议 | {bottle_cap.get('protocol', 'Modbus RTU (从模式)')} |")
    output.append(f"| 端口 | {bottle_cap.get('port', 'COM1')} |")
    output.append(f"| 通讯参数 | {bottle_cap.get('baudrate', 9600)},{bottle_cap.get('databits', 8)},{bottle_cap.get('parity', 'N')},{bottle_cap.get('stopbits', 1)} |")
    output.append(f"| 方向 | {bottle_cap.get('direction', '')} |")
    output.append("")
    output.append("**数据帧格式:**")
    output.append("| 字段 | 长度 | 说明 |")
    output.append("|------|------|------|")
    output.append("| 地址 | 1字节 | 设备地址 (0x01) |")
    output.append("| 功能码 | 1字节 | 0x03 (读保持寄存器) |")
    output.append("| 起始地址 | 2字节 | 高位在前 |")
    output.append("| 寄存器数量 | 2字节 | 高位在前 |")
    output.append("| CRC | 2字节 | 低位在前 |")
    output.append("")
    output.append("**瓶盖计数器寄存器:**")
    output.append("| 寄存器 | 参数 | 说明 |")
    output.append("|--------|------|------|")
    for reg in bottle_cap.get('registers', []):
        output.append(f"| {reg.get('addr', '')} | {reg.get('param', '')} | {reg.get('desc', '')} |")

    labeler = third_party.get('labeler_tcp', {})
    output.append("### 4.4 贴标机接口 (TCP/IP)")
    output.append("**接口概述:**")
    output.append("| 项目 | 规格 |")
    output.append("|------|------|")
    output.append(f"| 协议 | {labeler.get('protocol', 'TCP/IP (自定义协议)')} |")
    output.append(f"| SCADA作为 | {labeler.get('scada_role', 'Client')} |")
    output.append(f"| 贴标机作为 | {labeler.get('device_role', 'Server')} |")
    output.append(f"| IP地址 | {labeler.get('ip', '192.168.1.51')} |")
    output.append(f"| 端口 | {labeler.get('port', 5000)} |")
    output.append("")
    frame = labeler.get('frame_format', {})
    output.append("**数据帧格式 (ASCII):**")
    output.append("| 字段 | 长度 | 说明 |")
    output.append("|------|------|------|")
    output.append(f"| 帧头 | 2字节 | {frame.get('header', '0xAA 0x55')} |")
    output.append(f"| 数据长度 | 1字节 | {frame.get('length', 'n')} |")
    output.append(f"| 命令码 | 1字节 | {frame.get('command', '01=速度,02=状态')} |")
    output.append(f"| 数据 | n字节 | {frame.get('data', '-')} |")
    output.append(f"| 校验和 | 1字节 | {frame.get('checksum', 'XOR')} |")
    output.append(f"| 帧尾 | 2字节 | {frame.get('trailer', '0x0D 0x0A')} |")
    output.append("")
    output.append("**数据定义:**")
    output.append("| 命令码 | 数据内容 | 说明 |")
    output.append("|--------|----------|------|")
    for cmd in labeler.get('commands', []):
        output.append(f"| {cmd.get('code', '')} | {cmd.get('data', '')} | {cmd.get('desc', '')} |")

    coder = third_party.get('coder_tcp', {})
    output.append("### 4.5 喷码机接口 (TCP/IP)")
    output.append("**接口概述:**")
    output.append("| 项目 | 规格 |")
    output.append("|------|------|")
    output.append(f"| 协议 | {coder.get('protocol', 'TCP/IP')} |")
    output.append(f"| SCADA作为 | {coder.get('scada_role', 'Client')} |")
    output.append(f"| 喷码机作为 | {coder.get('device_role', 'Server')} |")
    output.append(f"| IP地址 | {coder.get('ip', '192.168.1.52')} |")
    output.append(f"| 端口 | {coder.get('port', 2000)} |")
    output.append("")
    output.append("**接口功能:**")
    output.append("| 功能 | 说明 |")
    output.append("|------|------|")
    for func in coder.get('functions', []):
        output.append(f"| {func.get('name', '')} | {func.get('desc', '')} |")

    # 5. 通讯诊断
    output.append("---")
    output.append("## 5. 通讯诊断与故障处理")
    output.append("### 5.1 通讯故障诊断")
    output.append("| 诊断项 | 检测方法 | 报警条件 | 处理方式 |")
    output.append("|--------|----------|----------|----------|")
    for key, diag in diagnostics.items():
        output.append(f"| {key} | {diag.get('method', '')} | {diag.get('alarm', '')} | {diag.get('action', '')} |")

    output.append("### 5.2 故障记录")
    output.append("| 记录内容 | 说明 |")
    output.append("|----------|------|")
    for field in fault_log:
        output.append(f"| {field.get('field', '')} | {field.get('format', '')} |")

    # 6. 通讯配置汇总
    output.append("---")
    output.append("## 6. 通讯配置汇总")
    output.append("### 6.1 IP地址规划")
    output.append("| 设备 | IP地址 | 子网掩码 | 网关 |")
    output.append("|------|--------|----------|------|")
    for dev in ip_planning.get('servers', []):
        output.append(f"| {dev.get('device', '')} | {dev.get('ip', '')} | {dev.get('mask', '')} | {dev.get('gateway', '')} |")
    for dev in ip_planning.get('plcs', []):
        output.append(f"| {dev.get('device', '')} | {dev.get('ip', '')} | {dev.get('mask', '')} | {dev.get('gateway', '')} |")
    for dev in ip_planning.get('instruments', []):
        output.append(f"| {dev.get('device', '')} | {dev.get('ip', '')} | {dev.get('mask', '')} | {dev.get('gateway', '')} |")
    for dev in ip_planning.get('third_party', []):
        output.append(f"| {dev.get('device', '')} | {dev.get('ip', '')} | {dev.get('mask', '')} | {dev.get('gateway', '')} |")

    output.append("### 6.2 串口配置")
    output.append("| 端口 | 用途 | 波特率 | 数据位 | 校验 | 停止位 |")
    output.append("|------|------|--------|--------|------|--------|")
    for port in serial_ports:
        output.append(f"| {port.get('port', '')} | {port.get('usage', '')} | {port.get('baudrate', '')} | {port.get('databits', '')} | {port.get('parity', '')} | {port.get('stopbits', '')} |")

    output.append("### 6.3 端口用途汇总")
    output.append("| 端口 | 协议 | 用途 |")
    output.append("|------|------|------|")
    for p in port_summary:
        output.append(f"| {p.get('port', '')} | {p.get('protocol', '')} | {p.get('usage', '')} |")

    # 文档状态
    output.append("---")
    output.append("**文档状态**: 自动生成")
    output.append("**版本历史**:")
    output.append(f"- v1.0 ({meta.get('created', '2026-04-28')}): 初始版本")
    output.append(f"- v1.1 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本")

    return "\n".join(output)
def main():
    parser = argparse.ArgumentParser(description='SCADA 文档自动生成器')
    parser.add_argument('--generate', choices=['all', 'points', 'interlocks', 'cip', 'comm'],
                        default='all', help='要生成的文档类型')
    parser.add_argument('--output', default=str(OUTPUT_DIR), help='输出目录')

    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(args.output, exist_ok=True)

    print(f"SCADA 文档生成器")
    print(f"输出目录: {args.output}")
    print("-" * 50)

    if args.generate in ['all', 'points']:
        print("正在生成: 监控点表...")
        content = generate_points_table()
        output_file = Path(args.output) / OUTPUT_POINTS.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  完成: {output_file}")

    if args.generate in ['all', 'interlocks']:
        print("正在生成: 联锁逻辑说明书...")
        content = generate_interlocks_table()
        output_file = Path(args.output) / OUTPUT_INTERLOCKS.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  完成: {output_file}")

    if args.generate in ['all', 'cip']:
        print("正在生成: CIP清洗程序规格书...")
        content = generate_cip_spec()
        output_file = Path(args.output) / OUTPUT_CIP.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  完成: {output_file}")

    if args.generate in ['all', 'comm']:
        print("正在生成: 通讯接口规格书...")
        content = generate_comm_spec()
        output_file = Path(args.output) / OUTPUT_COMM.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  完成: {output_file}")

    if args.generate == 'all':
        print("\n所有文档生成完成!")
        print(f"输出目录: {args.output}")


if __name__ == '__main__':
    main()
