"""
CIP清洗程序规格书生成器
茶饮料生产线 - 从 system_config.yaml 的 cip_program 配置生成CIP清洗程序规格书

使用方法:
    python _generators/cip_spec_generator.py
    或通过 run_all_generators.py 调用
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_RECIPE = SCRIPT_DIR.parent / "01_Spec" / "configs" / "process_recipe_templates.yaml"
OUTPUT_FILE = SCRIPT_DIR.parent / "04_Process" / "auto" / "茶饮料_CIP清洗程序规格书_auto.md"


def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_meta_data():
    data = load_yaml(CONFIG_RECIPE)
    return data.get('meta', {})


def generate_header():
    meta = get_meta_data()
    now = datetime.now().strftime("%Y-%m-%d")
    return f"""# 茶饮料生产线CIP清洗程序规格书

> 文档版本: v1.0
> 创建日期: {now}
> 更新日期: {now}
> 数据来源: 01_Spec/configs/process_recipe_templates.yaml (自动生成)
> 项目名称: {meta.get('project_name', '茶饮料生产线SCADA系统')}
> 产能: {meta.get('capacity', '50000B/H')}

> ⚠️ **本文件由系统配置自动生成 - 请勿手动修改**

---

## ⚠️ 重要声明

### 生成信息

| 项目 | 内容 |
| ---- | ---- |
| **数据来源** | `01_Spec/configs/process_recipe_templates.yaml` |
| **生成器脚本** | `_generators/cip_spec_generator.py` |
| **重新生成命令** | `python _generators/run_all_generators.py --gen=CIP_Spec` |

### 修改流程

1. 编辑 `01_Spec/configs/process_recipe_templates.yaml` 中的 `cip_program` 部分
2. 运行 `python _generators/run_all_generators.py --gen=CIP_Spec`
3. 检查生成的 `04_Process/auto/茶饮料_CIP清洗程序规格书_auto.md`

---

"""


def generate_standard_5step(cip_program):
    standard = cip_program.get('standard_5step', [])
    output = []
    output.append("## 1. 标准五步清洗程序\n")
    output.append("| 步骤 | 名称 | 介质 | 温度 | 时间 | 浓度 | 目的 |")
    output.append("|------|------|------|------|------|------|------|")

    for step in standard:
        output.append(f"| {step.get('step', '')} | {step.get('name', '')} | {step.get('medium', '')} | {step.get('temp', '')} | {step.get('time', '')} | {step.get('concentration', '')} | {step.get('purpose', '')} |")

    output.append("")
    return "\n".join(output)


def generate_environment_requirements(cip_program):
    env = cip_program.get('environment_requirements', {})
    output = []
    output.append("## 2. 生产环境要求\n")

    area_map = {
        'aseptic_area': '无菌区',
        'blending_area': '调配区',
        'extraction_area': '萃取区',
        'general_area': '一般区'
    }

    for key, area in env.items():
        area_name = area_map.get(key, key)
        output.append(f"### 2.{list(env.keys()).index(key)+1} {area_name}\n")
        output.append(f"| 项目 | 要求 |")
        output.append("|------|------|")
        output.append(f"| 洁净度 | {area.get('cleanliness', '')} |")
        output.append(f"| 温度 | {area.get('temp', '')} |")
        output.append(f"| 湿度 | {area.get('humidity', '')} |")
        output.append(f"| 压力 | {area.get('pressure', '')} |")
        output.append("")

    return "\n".join(output)


def generate_cip_system(cip_program):
    system = cip_program.get('system', {})
    output = []
    output.append("## 3. CIP系统配置\n")

    stations = system.get('stations', [])
    if stations:
        output.append("### 3.1 CIP站配置\n")
        output.append("| 罐ID | 名称 | 容量(m³) | 材质 | 化学介质 | 默认浓度 | 浓度范围 | 默认温度 | 温度范围 |")
        output.append("|------|------|----------|------|----------|----------|----------|----------|----------|")

        for station in stations:
            output.append(f"| {station.get('id', '')} | {station.get('name', '')} | {station.get('volume_m3', '')} | {station.get('tank_type', '')} | {station.get('chemical', '')} | {station.get('concentration_default', '')} | {station.get('concentration_range', '')} | {station.get('temp_default', '')} | {station.get('temp_range', '')} |")

        output.append("")

    pumps = system.get('pumps', [])
    if pumps:
        output.append("### 3.2 CIP泵配置\n")
        output.append("| 泵ID | 名称 | 流量(m³/h) | 变频 |")
        output.append("|------|------|-------------|------|")

        for pump in pumps:
            output.append(f"| {pump.get('id', '')} | {pump.get('name', '')} | {pump.get('flow_m3_h', '')} | {'是' if pump.get('is_inverter') else '否'} |")

        output.append("")

    return "\n".join(output)


def generate_cleaning_agents(cip_program):
    agents = cip_program.get('cleaning_agents', {})
    output = []
    output.append("## 4. 清洗剂规格\n")
    output.append("| 清洗剂 | 名称 | 默认浓度 | 浓度单位 | 默认温度 | 默认时间 | 时间单位 | 适用范围 |")
    output.append("|--------|------|----------|----------|----------|----------|----------|----------|")

    for key, agent in agents.items():
        output.append(f"| {key} | {agent.get('name', '')} | {agent.get('concentration_default', '')} | {agent.get('concentration_unit', '')} | {agent.get('temp_default', '')} | {agent.get('time_default', '')} | {agent.get('unit', '')} | {agent.get('applicable', '')} |")

    output.append("")
    return "\n".join(output)


def generate_cleaning_zones(cip_program):
    zones = cip_program.get('zones', {})
    output = []
    output.append("## 5. 清洗区域定义\n")

    zone_list = list(zones.items())

    for idx, (key, zone) in enumerate(zone_list, 1):
        output.append(f"### 5.{idx} {zone.get('name', '')} ({zone.get('description', '')})\n")
        output.append(f"| 项目 | 内容 |")
        output.append("|------|------|")
        output.append(f"| 区域代码 | {key} |")
        output.append(f"| 区域名称 | {zone.get('name', '')} |")
        output.append(f"| 描述 | {zone.get('description', '')} |")
        output.append(f"| 适用工段 | {', '.join(zone.get('section_codes', []))} |")
        output.append(f"| 目标设备 | {zone.get('target_devices', '')} |")
        output.append(f"| CIP程序 | {zone.get('cip_program', '')} |")
        output.append(f"| 清洗频率 | {zone.get('frequency', '')} |")
        output.append("")

    return "\n".join(output)


def generate_cip_programs(cip_program):
    programs = cip_program.get('programs', {})
    output = []
    output.append("## 6. CIP清洗程序详细规格\n")

    program_list = list(programs.items())

    for idx, (key, prog) in enumerate(program_list, 1):
        output.append(f"### 6.{idx} {prog.get('name', '')} (程序ID: {key})\n")
        output.append(f"**区域**: {prog.get('zone', '')}区")
        output.append(f"**描述**: {prog.get('description', '')}\n")

        output.append("#### 6." + str(idx) + ".1 触发条件\n")
        for trigger in prog.get('trigger_conditions', []):
            output.append(f"- {trigger}")
        output.append("")

        steps = prog.get('steps', [])
        if steps:
            output.append("#### 6." + str(idx) + ".2 清洗步骤\n")
            output.append("| 步骤 | 名称 | 介质 | 温度 | 时间(min) | 流速(m³/h) | 排放 | 循环 | 验收标准 |")
            output.append("|------|------|------|------|-----------|-------------|------|------|----------|")

            for step in steps:
                output.append(f"| {step.get('step', '')} | {step.get('name', '')} | {step.get('medium', '')} | {step.get('temp', '')} | {step.get('time_min', '')} | {step.get('flow_m3_h', '')} | {'是' if step.get('drain') else '否'} | {'是' if step.get('circulation') else '否'} | {step.get('standard', '')} |")

            output.append("")

        notes = prog.get('notes', [])
        if notes:
            output.append("#### 6." + str(idx) + ".3 注意事项\n")
            for note in notes:
                output.append(f"- {note}")
            output.append("")

        enhanced = prog.get('enhanced_cleaning', {})
        if enhanced:
            output.append("#### 6." + str(idx) + ".4 加强清洗\n")
            output.append(f"**频率**: {enhanced.get('frequency', '')}\n")
            enhanced_steps = enhanced.get('steps', [])
            if enhanced_steps:
                output.append("| 步骤 | 介质 | 温度 | 时间(min) | 说明 |")
                output.append("|------|------|------|-----------|------|")
                for step in enhanced_steps:
                    output.append(f"| {step.get('step', '')} | {step.get('medium', '')} | {step.get('temp', '')} | {step.get('time_min', '')} | {step.get('note', '')} |")
                output.append("")
        output.append("")

    return "\n".join(output)


def generate_product_switch_matrix(cip_program):
    matrix = cip_program.get('product_switch_matrix', [])
    output = []
    output.append("## 7. 产品切换清洗矩阵\n")
    output.append("| 当前产品 | 目标产品 | 清洗程序 | 预计时间(h) |")
    output.append("|----------|----------|----------|-------------|")

    for item in matrix:
        output.append(f"| {item.get('current_product', '')} | {item.get('target_product', '')} | {', '.join(item.get('programs', []))} | {item.get('estimated_time_h', '')} |")

    output.append("")
    return "\n".join(output)


def generate_acceptance_standards(cip_program):
    standards = cip_program.get('acceptance_standards', {})
    output = []
    output.append("## 8. 清洗验收标准\n")
    output.append("| 检测项目 | 检测方法 | 验收标准 |")
    output.append("|----------|----------|----------|")

    std_map = {
        'visual': '目视检查',
        'pH': 'pH值',
        'conductivity': '电导率',
        'microbiology': '微生物',
        'ATP': 'ATP检测'
    }

    for key, std in standards.items():
        output.append(f"| {std_map.get(key, key)} | {std.get('method', '')} | {std.get('standard', '')} |")

    output.append("")
    return "\n".join(output)


def generate_water_specifications(cip_program):
    specs = cip_program.get('water_specifications', {})
    output = []
    output.append("## 9. 清洗用水规格\n")
    output.append("| 用途 | 水类型 | 电导率要求 | 微生物要求 |")
    output.append("|------|--------|------------|------------|")

    for key, spec in specs.items():
        output.append(f"| {key} | {spec.get('type', '')} | {spec.get('conductivity_max', '')} | {spec.get('microbiology_max', '')} |")

    output.append("")
    return "\n".join(output)


def generate_cip_spec():
    data = load_yaml(CONFIG_RECIPE)
    cip_program = data.get('cip_program', {})

    output = []
    output.append(generate_header())
    output.append(generate_standard_5step(cip_program))
    output.append(generate_environment_requirements(cip_program))
    output.append(generate_cip_system(cip_program))
    output.append(generate_cleaning_agents(cip_program))
    output.append(generate_cleaning_zones(cip_program))
    output.append(generate_cip_programs(cip_program))
    output.append(generate_product_switch_matrix(cip_program))
    output.append(generate_acceptance_standards(cip_program))
    output.append(generate_water_specifications(cip_program))

    output.append("---\n")
    output.append(f"**文档状态**: 自动生成\n")
    output.append(f"**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    output.append(f"**版本历史**:\n")
    output.append(f"- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本\n")

    return "\n".join(output)


def main():
    print("CIP清洗程序规格书生成器")
    print("-" * 40)

    if not CONFIG_RECIPE.exists():
        print(f"错误: 配置文件不存在: {CONFIG_RECIPE}")
        return

    document = generate_cip_spec()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(document)

    print(f"生成文档: {OUTPUT_FILE}")
    print("\n完成!")


if __name__ == '__main__':
    main()