"""
CIP配方生成器
茶饮料生产线 - 从 cip_recipe_templates.yaml 生成CIP清洗配方文档

使用方法:
    python cip_recipe_generator.py
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_CIP = SCRIPT_DIR.parent / "configs" / "cip_recipe_templates.yaml"
OUTPUT_CIP = SCRIPT_DIR.parent / "CIP配方_auto.md"


def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_meta_data(config_file):
    data = load_yaml(config_file)
    return data.get('meta', {})


def generate_header(doc_type, config_file, version="v1.0"):
    meta = get_meta_data(config_file)
    now = datetime.now().strftime("%Y-%m-%d")
    return f"""# 茶饮料生产线{doc_type}

> 文档版本: {version}
> 创建日期: {now}
> 更新日期: {now}
> 数据来源: {config_file.name} (自动生成)
> 项目名称: {meta.get('project_name', '茶饮料生产线SCADA系统')}
> 产能: {meta.get('capacity', '50000B/H')}

---

"""


def generate_cip_recipe():
    data = load_yaml(CONFIG_CIP)
    cip_recipes = data.get('cip_recipes', {})

    output = []
    output.append(generate_header("CIP清洗配方", CONFIG_CIP))

    output.append("## 1. CIP配方汇总\n")
    output.append("| 配方ID | 名称 | 区域 | 适用工段 | 预计时间 |")
    output.append("|--------|------|------|----------|----------|")

    for key, cip in cip_recipes.items():
        sections = ", ".join(cip.get('section_codes', []))
        total_time = cip.get('total_time', '')
        time_unit = cip.get('total_time_unit', '')
        if cip.get('total_time_note', ''):
            time_str = f"{total_time}{time_unit} ({cip.get('total_time_note', '')})"
        else:
            time_str = f"{total_time}{time_unit}"
        output.append(f"| {cip.get('recipe_id', '')} | {cip.get('name', '')} | {cip.get('zone', '')}区 | {sections} | {time_str} |")

    output.append("")

    for key, cip in cip_recipes.items():
        output.append("---")
        output.append(f"\n## 2. {cip.get('name', '')}\n")
        output.append(f"**配方ID**: {cip.get('recipe_id', '')}")
        output.append(f"**区域**: {cip.get('zone', '')}区")
        output.append(f"**适用工段**: {', '.join(cip.get('section_codes', []))}\n")

        output.append("### 2.1 触发条件\n")
        for trigger in cip.get('trigger_conditions', []):
            output.append(f"- {trigger}")
        output.append("")

        steps = cip.get('steps', [])
        if steps and 'recipe' in steps[0]:
            output.append("### 2.2 清洗顺序\n")
            output.append("| 顺序 | 工段 | 清洗程序 |")
            output.append("|------|------|----------|")
            for step in steps:
                output.append(f"| {step.get('sequence', '')} | {step.get('section', '')} | {step.get('recipe', '')} |")
        else:
            output.append("### 2.2 清洗步骤\n")
            output.append("| 步骤 | 名称 | 介质 | 浓度 | 温度 | 时间 | 流速 | 验收标准 |")
            output.append("|------|------|------|------|------|------|------|----------|")

            for step in steps:
                step_num = step.get('step', step.get('sequence', ''))
                name = step.get('name', '')
                medium = step.get('medium', '-')
                conc = step.get('concentration', '')
                conc_unit = step.get('concentration_unit', '')
                temp = step.get('temp', '-')
                temp_unit = step.get('temp_unit', '℃')
                time_val = step.get('time', '')
                time_unit = step.get('time_unit', 'min')
                flow = step.get('flow_rate', '')
                flow_unit = step.get('flow_rate_unit', 'm³/h')
                acceptance = step.get('acceptance', '-')

                if conc:
                    conc_str = f"{conc}{conc_unit}"
                else:
                    conc_str = '-'

                if temp != '-' and isinstance(temp, (int, float)):
                    temp_str = f"{temp}{temp_unit}"
                else:
                    temp_str = str(temp) if temp != '-' else temp_unit

                if time_val:
                    time_str = f"{time_val}{time_unit}"
                else:
                    time_str = '-'

                if flow:
                    flow_str = f"{flow}{flow_unit}"
                else:
                    flow_str = '-'

                output.append(f"| {step_num} | {name} | {medium} | {conc_str} | {temp_str} | {time_str} | {flow_str} | {acceptance} |")

        output.append("")

        notes = cip.get('notes', [])
        if notes:
            output.append("### 2.3 注意事项\n")
            for note in notes:
                output.append(f"- {note}")
            output.append("")

        total_time = cip.get('total_time', '')
        time_unit = cip.get('total_time_unit', '')
        output.append(f"**总清洗时间**: {total_time} {time_unit}\n")

    output.append("---")
    output.append("\n## 3. 产品切换清洗矩阵\n")

    switch_matrix = data.get('product_switch_matrix', [])
    output.append("| 当前产品 | 目标产品 | 清洗配方 | 预计时间 | 说明 |")
    output.append("|----------|----------|----------|----------|------|")

    for switch in switch_matrix:
        from_prod = switch.get('from_product_name', switch.get('from_product', ''))
        to_prod = switch.get('to_product_name', switch.get('to_product', ''))
        cip_list = ", ".join(switch.get('cip_recipes', []))
        time_val = switch.get('estimated_time', '')
        time_unit = switch.get('estimated_time_unit', '')
        notes = switch.get('notes', '')
        output.append(f"| {from_prod} | {to_prod} | {cip_list} | {time_val}{time_unit} | {notes} |")

    output.append("")

    output.append("---")
    output.append("**文档状态**: 自动生成\n")
    output.append("**版本历史**:\n")
    output.append(f"- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本\n")

    return "\n".join(output)


def main():
    print("CIP配方生成器")
    print("-" * 40)

    if not CONFIG_CIP.exists():
        print(f"错误: 配置文件不存在: {CONFIG_CIP}")
        return

    document = generate_cip_recipe()
    OUTPUT_CIP.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CIP, 'w', encoding='utf-8') as f:
        f.write(document)

    print(f"生成文档: {OUTPUT_CIP}")
    print("\n完成!")


if __name__ == '__main__':
    main()