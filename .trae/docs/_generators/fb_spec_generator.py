"""
FB功能块规格说明书生成器
茶饮料生产线 - 从FB_Spec_Template.yaml生成规格文档

使用方法:
    python fb_spec_generator.py
"""

import os
import yaml
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
CONFIG_DIR = SCRIPT_DIR.parent / "02_Arch" / "configs"
OUTPUT_DIR = SCRIPT_DIR.parent / "02_Arch" / "auto"


def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_interface_table(inputs_or_outputs):
    if not inputs_or_outputs:
        return ""

    lines = []
    lines.append("| 名称 | 类型 | 描述 |")
    lines.append("|------|------|------|")

    for item in inputs_or_outputs:
        name = item.get('name', '')
        iotype = item.get('type', '')
        desc = item.get('desc', '')
        default = item.get('default', '')
        range_info = item.get('range', [])

        desc_full = desc
        if default:
            desc_full += f" (默认: {default})"
        if range_info and len(range_info) == 2:
            desc_full += f" 范围: {range_info[0]}-{range_info[1]}"

        lines.append(f"| {name} | {iotype} | {desc_full} |")

    return "\n".join(lines)


def generate_parameters_table(parameters):
    if not parameters:
        return ""

    lines = []
    lines.append("| 名称 | 类型 | 默认值 | 描述 |")
    lines.append("|------|------|--------|------|")

    for item in parameters:
        name = item.get('name', '')
        ptype = item.get('type', '')
        default = item.get('default', '')
        desc = item.get('desc', '')

        lines.append(f"| {name} | {ptype} | {default} | {desc} |")

    return "\n".join(lines)


def generate_diagnostics_table(diagnostics):
    if not diagnostics:
        return ""

    lines = []
    lines.append("| 代码 | 描述 |")
    lines.append("|------|------|")

    for item in diagnostics:
        code = item.get('code', '')
        desc = item.get('desc', '')
        lines.append(f"| {code} | {desc} |")

    return "\n".join(lines)


def generate_steps_table(steps):
    if not steps:
        return ""

    lines = []
    lines.append("| 步骤 | 名称 | 动作 | 目标 | 时间限制 |")
    lines.append("|------|------|------|------|----------|")

    for item in steps:
        step_num = item.get('step', '')
        name = item.get('name', '')
        action = item.get('action', '')
        target = item.get('target', '')
        time_limit = item.get('time_limit', '')

        lines.append(f"| {step_num} | {name} | {action} | {target} | {time_limit} |")

    return "\n".join(lines)


def generate_fb_section(fb_name, fb_config):
    lines = []

    name = fb_config.get('name', '')
    description = fb_config.get('description', '')
    version = fb_config.get('version', '')
    category = fb_config.get('category', '')
    parent = fb_config.get('parent', '')

    lines.append(f"### {fb_name}")
    lines.append("")
    lines.append(f"**名称**: {name}")
    lines.append(f"**描述**: {description}")
    lines.append(f"**版本**: {version}")
    lines.append(f"**类别**: {category}")
    if parent:
        lines.append(f"**父功能块**: {parent}")
    lines.append("")

    interface = fb_config.get('interface', {})
    if interface:
        inputs = interface.get('inputs', [])
        outputs = interface.get('outputs', [])

        if inputs:
            lines.append(f"#### {fb_name} 输入参数")
            lines.append("")
            lines.append(generate_interface_table(inputs))
            lines.append("")

        if outputs:
            lines.append(f"#### {fb_name} 输出参数")
            lines.append("")
            lines.append(generate_interface_table(outputs))
            lines.append("")

    parameters = fb_config.get('parameters', [])
    if parameters:
        lines.append(f"#### {fb_name} 参数定义")
        lines.append("")
        lines.append(generate_parameters_table(parameters))
        lines.append("")

    steps = fb_config.get('steps', [])
    if steps:
        lines.append(f"#### {fb_name} 批次步骤")
        lines.append("")
        lines.append(generate_steps_table(steps))
        lines.append("")

    logic = fb_config.get('logic', [])
    if logic:
        lines.append(f"#### {fb_name} 逻辑说明")
        lines.append("")
        for step_info in logic:
            step = step_info.get('step', '')
            desc = step_info.get('desc', '')
            lines.append(f"- **{step}**: {desc}")
        lines.append("")

    diagnostics = fb_config.get('diagnostics', [])
    if diagnostics:
        lines.append(f"#### {fb_name} 诊断代码")
        lines.append("")
        lines.append(generate_diagnostics_table(diagnostics))
        lines.append("")

    ccp_monitoring = fb_config.get('ccp_monitoring', [])
    if ccp_monitoring:
        lines.append(f"#### {fb_name} CCP监控点")
        lines.append("")
        lines.append("| 监控点 | 位置 | 参数 | 限值 | 持续时间 | 动作 |")
        lines.append("|--------|------|------|------|----------|------|")
        for ccp in ccp_monitoring:
            lines.append(f"| {ccp.get('point', '')} | {ccp.get('location', '')} | {ccp.get('parameter', '')} | {ccp.get('limit', '')} | {ccp.get('duration', '')} | {ccp.get('action', '')} |")
        lines.append("")

    return "\n".join(lines)


def generate_document(config):
    meta = config.get('meta', {})
    version = meta.get('version', 'v1.0')
    created = datetime.now().strftime('%Y-%m-%d')

    lines = []
    lines.append("# PLC功能块规格说明书")
    lines.append("")
    lines.append("> 文档版本: v1.0")
    lines.append(f"> 创建日期: {created}")
    lines.append(f"> 更新日期: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("> 数据来源: 02_Arch/configs/FB_Spec_Template.yaml (自动生成)")
    lines.append("")
    lines.append("> ⚠️ **本文件由系统配置自动生成 - 请勿手动修改**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ⚠️ 重要声明")
    lines.append("")
    lines.append("### 生成信息")
    lines.append("")
    lines.append("| 项目 | 内容 |")
    lines.append("| ---- | ---- |")
    lines.append("| **数据来源** | `02_Arch/configs/FB_Spec_Template.yaml` |")
    lines.append("| **生成器脚本** | `02_Arch/_generators/fb_spec_generator.py` |")
    lines.append("| **重新生成命令** | `python 02_Arch/_generators/fb_spec_generator.py` |")
    lines.append("")
    lines.append("### 修改流程")
    lines.append("")
    lines.append("1. 编辑 `02_Arch/configs/FB_Spec_Template.yaml`")
    lines.append("2. 运行 `python 02_Arch/_generators/fb_spec_generator.py`")
    lines.append("3. 检查生成的 `02_Arch/auto/PLC功能块规格说明书_auto.md`")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. 概述")
    lines.append("")
    lines.append("### 1.1 文档目的")
    lines.append("")
    lines.append("本文档定义了茶饮料生产线SCADA系统中使用的所有PLC功能块的规格说明，包括：")
    lines.append("- 功能块接口定义（输入/输出参数）")
    lines.append("- 功能块参数配置")
    lines.append("- 功能块逻辑说明")
    lines.append("- 诊断代码定义")
    lines.append("")
    lines.append("### 1.2 适用范围")
    lines.append("")
    lines.append(f"- 项目: {meta.get('project', '茶饮料生产线')}")
    lines.append(f"- PLC型号: {meta.get('plc_version', 'Siemens S7-1500')}")
    lines.append(f"- 编程标准: {meta.get('programming_standard', 'IEC 61131-3')}")
    lines.append("")

    lines.append("## 2. 基础控制功能块")
    lines.append("")

    basic_fbs = config.get('basic_function_blocks', {})
    for fb_name, fb_config in basic_fbs.items():
        lines.append(generate_fb_section(fb_name, fb_config))
        lines.append("---\n")

    process_fbs = config.get('process_function_blocks', {})
    if process_fbs:
        lines.append("## 3. 工艺控制功能块")
        lines.append("")
        for fb_name, fb_config in process_fbs.items():
            lines.append(generate_fb_section(fb_name, fb_config))
            lines.append("---\n")

    batch_fbs = config.get('batch_function_blocks', {})
    if batch_fbs:
        lines.append("## 4. 批次控制功能块")
        lines.append("")
        for fb_name, fb_config in batch_fbs.items():
            lines.append(generate_fb_section(fb_name, fb_config))
            lines.append("---\n")

    uht_fbs = config.get('uht_function_blocks', {})
    if uht_fbs:
        lines.append("## 5. UHT杀菌专用功能块")
        lines.append("")
        for fb_name, fb_config in uht_fbs.items():
            lines.append(generate_fb_section(fb_name, fb_config))
            lines.append("---\n")

    filling_fbs = config.get('filling_function_blocks', {})
    if filling_fbs:
        lines.append("## 6. 灌装系统专用功能块")
        lines.append("")
        for fb_name, fb_config in filling_fbs.items():
            lines.append(generate_fb_section(fb_name, fb_config))
            lines.append("---\n")

    version_info = config.get('version_management', {})
    lines.append("## 7. 版本管理")
    lines.append("")
    lines.append(f"**当前版本**: {version_info.get('current_version', 'v1.0')}")
    lines.append(f"**生效日期**: {version_info.get('effective_date', created)}")
    lines.append(f"**编制人**: {version_info.get('author', '')}")
    lines.append(f"**审批人**: {version_info.get('approver', '待确认')}")
    lines.append("")
    lines.append("### 版本历史")
    lines.append("")
    lines.append("| 版本 | 日期 | 作者 | 变更内容 | 状态 |")
    lines.append("|------|------|------|----------|------|")

    history = version_info.get('history', [])
    for h in history:
        lines.append(f"| {h.get('version', '')} | {h.get('date', '')} | {h.get('author', '')} | {h.get('changes', '')} | {h.get('status', '')} |")

    lines.append("")
    lines.append("---\n")
    lines.append(f"*本文档由系统自动生成，生成时间: {created}*")

    return "\n".join(lines)


def main():
    print("FB功能块规格说明书生成器")
    print("-" * 40)

    config_file = CONFIG_DIR / "FB_Spec_Template.yaml"
    print(f"读取配置: {config_file}")

    if not config_file.exists():
        print(f"错误: 配置文件不存在: {config_file}")
        return

    config = load_yaml(config_file)
    document = generate_document(config)

    output_file = OUTPUT_DIR / "茶饮料_PLC功能块规格_auto.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(document)

    print(f"生成文档: {output_file}")
    print("\n完成!")


if __name__ == '__main__':
    main()
