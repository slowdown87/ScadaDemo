import yaml
from datetime import datetime
import os

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_interlock_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(os.path.dirname(script_dir), '01_Spec', 'configs')
    interlock_path = os.path.join(config_dir, 'interlock_templates.yaml')
    with open(interlock_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def generate_interlock_doc(system_config, interlock_config):
    meta = interlock_config.get('meta', {})
    interlock_templates = interlock_config.get('interlock_templates', {})
    section_interlocks = interlock_templates.get('section_interlocks', {})
    interlock_levels = interlock_templates.get('interlock_levels', {})
    esd = interlock_templates.get('esd_interlocks', {})
    operation_il = interlock_templates.get('operation_interlocks', {})
    reset_perm = interlock_templates.get('reset_permissions', [])
    reset_flow = interlock_templates.get('reset_flow', '')
    summary = interlock_templates.get('interlock_summary', [])

    lines = []
    lines.append("# 茶饮料生产线SCADA监控系统联锁逻辑说明书\n")
    lines.append("> 文档版本: v1.0")
    lines.append("> 创建日期: " + datetime.now().strftime('%Y-%m-%d'))
    lines.append("> 更新日期: " + datetime.now().strftime('%Y-%m-%d'))
    lines.append("> 项目名称: " + meta.get('project_name', '茶饮料生产线SCADA监控系统'))
    lines.append("> 产品类型: " + meta.get('product_type', '纯茶饮料'))
    lines.append("> 产能: " + meta.get('capacity', '50000B/H'))

    lines.append("\n---\n## 1. 概述")
    lines.append("### 1.1 文档目的")
    lines.append("本文档定义茶饮料生产线SCADA系统中所有安全联锁和操作联锁的逻辑关系，作为PLC程序开发和SCADA组态的依据。")

    lines.append("\n### 1.2 联锁分类")
    lines.append("| 类别 | 说明 | 响应要求 |")
    lines.append("|------|------|----------|")
    lines.append("| 安全联锁(ESD) | 涉及人员安全、设备安全的紧急联锁 | 立即执行，无需确认 |")
    lines.append("| 关键控制联锁 | 食品安全、产品质量关键点的联锁 | 立即执行，报警提示 |")
    lines.append("| 操作联锁 | 防止误操作的程序联锁 | 禁止执行，提示原因 |")
    lines.append("| 顺序联锁 | 批次生产、程序切换的逻辑联锁 | 按逻辑执行 |")

    lines.append("\n### 1.3 联锁级别定义")
    lines.append("| 级别 | 名称 | 颜色 | 声音 | 响应时间 | 处理方式 |")
    lines.append("|------|------|------|------|----------|----------|")
    for level, info in interlock_levels.items():
        lines.append("| " + level + " | " + info.get('name', '') + " | " +
                    info.get('color', '') + " | " + info.get('sound', '') + " | " +
                    info.get('response_time', '') + " | " + info.get('action', '') + " |")

    lines.append("\n---\n## 2. 紧急停止联锁(ESD)")
    lines.append("### 2.1 紧急停止触发条件")
    lines.append("| 触发源 | 位置 | 动作级别 |")
    lines.append("|--------|------|----------|")
    for t in esd.get('trigger_sources', []):
        lines.append("| " + t.get('source', '') + " | " + t.get('location', '') + " | " + t.get('level', '') + " |")

    lines.append("\n### 2.2 紧急停止动作矩阵")
    lines.append("| 触发 → | 停止设备 | 关闭阀门 | 启动动作 | 复位方式 |")
    lines.append("|--------|----------|----------|----------|----------|")
    for a in esd.get('action_matrix', []):
        lines.append("| " + a.get('trigger', '') + " | " + a.get('stop_devices', '') + " | " +
                    a.get('close_valves', '') + " | " + a.get('start_actions', '') + " | " +
                    a.get('reset_mode', '') + " |")

    section_names = {
        'UH': 'UHT杀菌系统', 'EX': '萃取系统', 'HM': '均质系统',
        'BL': '调配系统', 'PF': '灌装系统', 'WT': '水处理系统',
        'FL': '过滤系统', 'CP': 'CIP清洗系统', 'BF': '制瓶系统',
        'CG': '旋盖系统', 'LI': '灯检系统', 'CI': '喷码系统',
        'LB': '贴标系统', 'CA': '装箱系统', 'PK': '膜包码垛系统',
        'TH': '茶叶前处理系统'
    }

    section_order = ['UH', 'EX', 'HM', 'BL', 'WT', 'FL', 'TH', 'PF', 'BF', 'CG', 'LI', 'CI', 'LB', 'CA', 'PK', 'CP']

    idx = 3
    for sec_id in section_order:
        if sec_id not in section_interlocks:
            continue
        sec_data = section_interlocks[sec_id]
        sec_name = sec_data.get('name', section_names.get(sec_id, sec_id))

        lines.append("\n---\n## " + str(idx) + ". " + sec_name + "联锁")
        lines.append("### " + str(idx) + ".1 联锁因果表")
        lines.append("| 序号 | 触发条件 | 报警级别 | 联锁动作 | 复位条件 |")
        lines.append("|------|----------|----------|----------|----------|")

        for il in sec_data.get('interlocks', []):
            actions_str = '<br>'.join(il.get('actions', [])) if il.get('actions') else '-'
            lines.append("| " + il.get('id', '') + " | " + il.get('trigger_desc', '') + " | " +
                        il.get('level', '') + " (" + il.get('alarm_level', '') + ") | " +
                        actions_str + " | " + il.get('reset_condition', '-') + " |")

        if sec_data.get('start_conditions'):
            lines.append("\n### " + str(idx) + ".2 启动允许条件")
            lines.append("| 条件 | 要求 | 检查点 |")
            lines.append("|------|------|--------|")
            for sc in sec_data.get('start_conditions', []):
                lines.append("| " + sc.get('condition', '') + " | " +
                            sc.get('requirement', '') + " | " +
                            sc.get('check_point', '-') + " |")

        if sec_data.get('sequence_control'):
            lines.append("\n### " + str(idx) + ".3 顺序控制")
            for line in sec_data.get('sequence_control', '').strip().split('\n'):
                lines.append(line)

        if sec_data.get('speed_sync'):
            lines.append("\n### " + str(idx) + ".4 速度同步")
            lines.append("| 设备 | 基准速度 | 同步模式 | 容差 |")
            lines.append("|------|----------|----------|------|")
            for ss in sec_data.get('speed_sync', []):
                lines.append("| " + ss.get('device', '') + " | " +
                            ss.get('base_speed', '') + " | " +
                            ss.get('sync_mode', '') + " | " +
                            ss.get('tolerance', '') + " |")

        idx += 1

    lines.append("\n---\n## " + str(idx) + ". 操作联锁")
    lines.append("### " + str(idx) + ".1 阀门操作联锁")
    lines.append("| 阀门 | 名称 | 允许条件 | 禁止条件 | 提示信息 |")
    lines.append("|------|------|----------|----------|----------|")
    for v in operation_il.get('valve_operations', []):
        lines.append("| " + v.get('valve', '') + " | " + v.get('name', '') + " | " +
                    v.get('allow_condition', '') + " | " + v.get('forbid_condition', '') + " | " +
                    v.get('message', '') + " |")

    lines.append("\n### " + str(idx) + ".2 电机启动条件")
    lines.append("| 电机 | 名称 | 允许条件 | 禁止条件 | 提示信息 |")
    lines.append("|------|------|----------|----------|----------|")
    for m in operation_il.get('motor_start_conditions', []):
        lines.append("| " + m.get('motor', '') + " | " + m.get('name', '') + " | " +
                    m.get('allow_condition', '') + " | " + m.get('forbid_condition', '') + " | " +
                    m.get('message', '') + " |")

    lines.append("\n---\n## " + str(idx + 1) + ". 复位权限与流程")
    lines.append("### 复位权限")
    lines.append("| 级别 | 名称 | 复位权限 | 确认要求 |")
    lines.append("|------|------|----------|----------|")
    for r in reset_perm:
        lines.append("| " + r.get('level', '') + " | " + r.get('name', '') + " | " +
                    r.get('reset_authority', '') + " | " + r.get('confirm_requirement', '') + " |")

    lines.append("\n### 复位流程")
    if reset_flow:
        for line in reset_flow.strip().split('\n'):
            lines.append(line)

    lines.append("\n---\n## " + str(idx + 2) + ". 联锁点汇总")
    lines.append("| 工段 | L0 | L1 | L2 | L3 | L4 |")
    lines.append("|------|----|----|----|----|----|")
    for s in summary:
        lines.append("| " + s.get('section', '') + " | " + str(s.get('l0', 0)) +
                    " | " + str(s.get('l1', 0)) + " | " + str(s.get('l2', 0)) +
                    " | " + str(s.get('l3', 0)) + " | " + str(s.get('l4', 0)) + " |")

    total = {'l0': 0, 'l1': 0, 'l2': 0, 'l3': 0, 'l4': 0}
    for s in summary:
        for k in total:
            total[k] += s.get(k, 0)
    lines.append("| **合计** | **" + str(total['l0']) + "** | **" + str(total['l1']) +
                "** | **" + str(total['l2']) + "** | **" + str(total['l3']) +
                "** | **" + str(total['l4']) + "** |")

    return '\n'.join(lines)

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(os.path.dirname(script_dir), '01_Spec', 'configs', 'system_config.yaml')
    output_path = os.path.join(os.path.dirname(script_dir), '04_Process', 'auto', '茶饮料_联锁逻辑说明书_auto.md')

    system_config = load_config(config_path)
    interlock_config = load_interlock_config()
    doc = generate_interlock_doc(system_config, interlock_config)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)

    print(f"Generated: {output_path}")
