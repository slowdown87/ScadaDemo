"""
SCADA 配方文档自动生成器
茶饮料生产线 - 产品配方、工艺配方、CIP配方 自动生成

使用方法:
    python recipe_generator.py --generate <document_type> [--output <output_dir>]

参数:
    --generate     生成文档类型: all, product, process, cip
    --output       输出目录 (默认: ../)

示例:
    python recipe_generator.py --generate all           # 生成所有配方文档
    python recipe_generator.py --generate product      # 仅生成产品配方
    python recipe_generator.py --generate process      # 仅生成工艺配方
    python recipe_generator.py --generate cip          # 仅生成CIP配方
"""

import os
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR
OUTPUT_DIR = SCRIPT_DIR.parent

RECIPE_FILE = DATA_DIR / "recipe_templates.yaml"

OUTPUT_PRODUCT = OUTPUT_DIR / "产品配方_auto.md"
OUTPUT_PROCESS = OUTPUT_DIR / "工艺配方_auto.md"
OUTPUT_CIP = OUTPUT_DIR / "CIP配方_auto.md"


def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_recipe_data():
    return load_yaml(RECIPE_FILE)


def generate_header(doc_type, version="v1.0"):
    meta = get_recipe_data().get('meta', {})
    now = datetime.now().strftime("%Y-%m-%d")
    return f"""# 茶饮料生产线{doc_type}

> 文档版本: {version}
> 创建日期: {now}
> 更新日期: {now}
> 数据来源: scada_data/recipe_templates.yaml (自动生成)
> 项目名称: {meta.get('project_name', '茶饮料生产线SCADA系统')}
> 产能: {meta.get('capacity', '50000B/H')}

---

"""


def generate_product_recipe():
    """生成产品配方文档"""
    data = get_recipe_data()
    products = data.get('product_recipes', {})
    acceptance = data.get('acceptance_standards', {})

    output = []
    output.append(generate_header("产品配方"))

    output.append("## 1. 产品配方汇总\n")
    output.append("| 产品名称 | 产品代码 | 状态 | 茶多酚要求 | 目标Brix | 目标pH | 清洗配方 |")
    output.append("|----------|----------|------|------------|----------|--------|----------|")

    for key, product in products.items():
        quality = product.get('quality', {})
        output.append(f"| {product.get('name', '')} | {product.get('code', '')} | {product.get('status', '')} | {quality.get('tea_polyphenol_min', '-')}{quality.get('tea_polyphenol_unit', '')} | {product.get('blending', {}).get('target_brix', {}).get('value', '')}{product.get('blending', {}).get('target_brix', {}).get('unit', '')} | {product.get('blending', {}).get('target_ph', {}).get('value', '')} | {product.get('cleaning_recipe', '')} |")

    output.append("")

    for key, product in products.items():
        output.append("---")
        output.append(f"\n## 2. {product.get('name', '')} ({product.get('code', '')}) 配方\n")
        output.append(f"**描述**: {product.get('description', '')}\n")

        tea_spec = product.get('tea_spec', {})
        output.append("### 2.1 茶叶原料规格\n")
        output.append("| 项目 | 规格 |")
        output.append("|------|------|")
        output.append(f"| 茶叶类型 | {tea_spec.get('type', '')} |")
        output.append(f"| 等级 | {tea_spec.get('grade', '')} |")
        output.append(f"| 产地 | {tea_spec.get('origin', '')} |")
        output.append(f"| 粒度 | {tea_spec.get('particle_size', '')} |")
        output.append(f"| 储存温度 | {tea_spec.get('storage_temp', '')} |")
        output.append(f"| 储存湿度 | {tea_spec.get('storage_humidity', '')} |")
        output.append("")

        extraction = product.get('extraction', {})
        output.append("### 2.2 萃取工艺参数\n")
        output.append("| 参数 | 设定值 | 范围 | 单位 |")
        output.append("|------|--------|------|------|")
        output.append(f"| 水温设定 | {extraction.get('water_temp_setpoint', '')} | {extraction.get('water_temp_range', ['',''])[0]}-{extraction.get('water_temp_range', ['',''])[1]} | ℃ |")
        output.append(f"| 茶水比 | 1:{extraction.get('tea_ratio_min', '')}-{extraction.get('tea_ratio_max', '')} | {extraction.get('tea_ratio_unit', '')} |")
        output.append(f"| 萃取时间 | {extraction.get('extraction_time_setpoint', '')} | {extraction.get('extraction_time_range', ['',''])[0]}-{extraction.get('extraction_time_range', ['',''])[1]} | {extraction.get('extraction_time_unit', '')} |")
        output.append(f"| 搅拌速度 | {extraction.get('agitation_speed', '')} | - | {extraction.get('agitation_speed_unit', '')} |")
        output.append(f"| 萃取级数 | {extraction.get('stages', '')} | - | 级 |")
        output.append(f"| 逆流萃取 | {'是' if extraction.get('counter_current', False) else '否'} | - | - |")
        output.append("")

        blending = product.get('blending', {})
        output.append("### 2.3 调配工艺参数\n")
        output.append("| 参数 | 设定值 | 容差 | 单位 |")
        output.append("|------|--------|------|------|")
        incoming = blending.get('incoming_tea_conc', {})
        output.append(f"| 进料茶汁浓度 | {incoming.get('value', '')} | {incoming.get('tolerance', '')} | {incoming.get('unit', '')} |")
        sugar = blending.get('sugar_syrup_conc', {})
        output.append(f"| 糖浆浓度 | {sugar.get('value', '')} | - | {sugar.get('unit', '')} |")
        brix = blending.get('target_brix', {})
        output.append(f"| 目标Brix | {brix.get('value', '')} | {brix.get('tolerance', '')} | {brix.get('unit', '')} |")
        ph = blending.get('target_ph', {})
        output.append(f"| 目标pH | {ph.get('value', '')} | {ph.get('tolerance', '')} | - |")
        output.append(f"| 柠檬酸添加量 | {blending.get('citric_acid_percent', '')} | - | % |")
        blend_temp = blending.get('blending_temp', {})
        output.append(f"| 调配温度 | {blend_temp.get('value', '')} | {blend_temp.get('range', ['',''])[0]}-{blend_temp.get('range', ['',''])[1]} | {blend_temp.get('unit', '')} |")
        output.append(f"| 调配时间 | {blending.get('blending_time', '')} | - | {blending.get('blending_time_unit', '')} |")
        output.append(f"| 搅拌速度 | {blending.get('agitation_speed', '')} | - | {blending.get('agitation_speed_unit', '')} |")
        output.append("")

        homogenization = product.get('homogenization', {})
        output.append("### 2.4 均质工艺参数\n")
        output.append("| 参数 | 设定值 | 范围 | 单位 |")
        output.append("|------|--------|------|------|")
        output.append(f"| 均质压力 | {homogenization.get('pressure_setpoint', '')} | {homogenization.get('pressure_range', ['',''])[0]}-{homogenization.get('pressure_range', ['',''])[1]} | {homogenization.get('pressure_unit', '')} |")
        output.append(f"| 进料温度 | {homogenization.get('inlet_temp', '')} | {homogenization.get('inlet_temp_range', ['',''])[0]}-{homogenization.get('inlet_temp_range', ['',''])[1]} | ℃ |")
        output.append(f"| 出料温度上限 | {homogenization.get('outlet_temp_max', '')} | - | ℃ |")
        output.append(f"| 均质次数 | {homogenization.get('passes', '')} | - | 次 |")
        output.append("")

        uht = product.get('uht', {})
        output.append("### 2.5 UHT杀菌参数\n")
        output.append("| 参数 | 设定值 | 范围 | 单位 |")
        output.append("|------|--------|------|------|")
        output.append(f"| 预热温度 | {uht.get('preheat_temp', '')} | - | ℃ |")
        output.append(f"| 杀菌温度 | {uht.get('sterilization_temp', '')} | {uht.get('sterilization_temp_range', ['',''])[0]}-{uht.get('sterilization_temp_range', ['',''])[1]} | ℃ |")
        output.append(f"| 杀菌时间 | {uht.get('sterilization_time', '')} | - | {uht.get('sterilization_time_unit', '')} |")
        output.append(f"| 保温温度下限 | {uht.get('holding_temp_min', '')} | - | ℃ |")
        output.append(f"| 冷却出口温度 | {uht.get('cooling_temp_outlet', '')} | 最高{uht.get('cooling_temp_outlet_max', '')} | ℃ |")
        output.append(f"| 产品流量 | {uht.get('flow_rate', '')} | - | {uht.get('flow_rate_unit', '')} |")
        output.append(f"| 背压 | {uht.get('back_pressure', '')} | - | {uht.get('back_pressure_unit', '')} |")
        output.append("")

        filling = product.get('filling', {})
        output.append("### 2.6 灌装参数\n")
        output.append("| 参数 | 设定值 | 范围 | 单位 |")
        output.append("|------|--------|------|------|")
        output.append(f"| 灌装温度 | {filling.get('temp', '')} | {filling.get('temp_range', ['',''])[0]}-{filling.get('temp_range', ['',''])[1]} | {filling.get('temp_unit', '')} |")
        output.append(f"| 灌装速度 | {filling.get('speed', '')} | - | {filling.get('speed_unit', '')} |")
        output.append(f"| 瓶容量 | {filling.get('bottle_volume', '')} | - | {filling.get('bottle_volume_unit', '')} |")
        output.append(f"| 顶隙高度 | {filling.get('headspace', '')} | - | {filling.get('headspace_unit', '')} |")
        output.append(f"| 盖扭矩 | {filling.get('cap_torque_min', '')}-{filling.get('cap_torque_max', '')} | - | {filling.get('cap_torque_unit', '')} |")
        output.append("")

        quality = product.get('quality', {})
        output.append("### 2.7 品质指标\n")
        output.append("| 项目 | 指标 | 方法/单位 |")
        output.append("|------|------|------------|")
        output.append(f"| 茶多酚 | ≥{quality.get('tea_polyphenol_min', '')} | {quality.get('tea_polyphenol_unit', '')} |")
        output.append(f"| 浊度 | ≤{quality.get('turbidity_max', '')} | {quality.get('turbidity_unit', '')} |")
        output.append(f"| 色泽 | {quality.get('color', '')} | - |")
        output.append(f"| 风味 | {quality.get('flavor', '')} | - |")
        output.append("")

        output.append("### 2.8 清洗信息\n")
        output.append(f"| 清洗配方 | {product.get('cleaning_recipe', '')} |")
        output.append(f"| 预计清洗时间 | {product.get('cleaning_time_estimate', '')} {product.get('cleaning_time_unit', '')} |")
        output.append("")

    output.append("---")
    output.append("\n## 3. 验收标准\n")

    output.append("### 3.1 感官指标\n")
    output.append("| 项目 | 标准 | 检验方法 |")
    output.append("|------|------|----------|")
    for item in acceptance.get('sensory', []):
        output.append(f"| {item.get('parameter', '')} | {item.get('standard', '')} | {item.get('method', '')} |")
    output.append("")

    output.append("### 3.2 理化指标\n")
    output.append("| 项目 | 标准 | 单位 | 检验方法 |")
    output.append("|------|------|------|----------|")
    for item in acceptance.get('physical', []):
        output.append(f"| {item.get('parameter', '')} | {item.get('standard', '')} | {item.get('unit', '')} | {item.get('method', '')} |")
    output.append("")

    output.append("### 3.3 化学指标\n")
    output.append("| 项目 | 标准 | 单位 | 检验方法 |")
    output.append("|------|------|------|----------|")
    for item in acceptance.get('chemical', []):
        output.append(f"| {item.get('parameter', '')} | {item.get('standard', '')} | {item.get('unit', '')} | {item.get('method', '')} |")
    output.append("")

    output.append("### 3.4 微生物指标\n")
    output.append("| 项目 | 标准 | 单位 | 检验方法 |")
    output.append("|------|------|------|----------|")
    for item in acceptance.get('microbiological', []):
        output.append(f"| {item.get('parameter', '')} | {item.get('standard', '')} | {item.get('unit', '')} | {item.get('method', '')} |")
    output.append("")

    version_info = data.get('version_management', {})
    output.append("---")
    output.append("**文档状态**: 自动生成\n")
    output.append("**版本历史**:\n")
    for hist in version_info.get('history', []):
        output.append(f"- {hist.get('version', '')} ({hist.get('date', '')}): {hist.get('changes', '')}\n")

    return "\n".join(output)


def generate_process_recipe():
    """生成工艺配方文档"""
    data = get_recipe_data()
    processes = data.get('process_recipes', {})

    output = []
    output.append(generate_header("工艺配方"))

    output.append("## 1. 工艺配方汇总\n")
    output.append("| 配方ID | 工艺名称 | 工段 | 关联清洗 |")
    output.append("|--------|----------|------|----------|")

    section_names = {
        'WT': '水处理', 'TH': '茶叶前处理', 'EX': '萃取',
        'FL': '过滤', 'BL': '调配', 'HM': '均质',
        'UH': 'UHT杀菌', 'PF': '灌装', 'PK': '包装'
    }

    for key, proc in processes.items():
        section = proc.get('section', '')
        section_name = section_names.get(section, section)
        output.append(f"| {proc.get('recipe_id', '')} | {proc.get('name', '')} | {section} ({section_name}) | {proc.get('cleaning_recipe', '')} |")

    output.append("")

    for key, proc in processes.items():
        output.append("---")
        section = proc.get('section', '')
        section_name = section_names.get(section, section)
        output.append(f"\n## 2. {proc.get('name', '')}\n")
        output.append(f"**配方ID**: {proc.get('recipe_id', '')}")
        output.append(f"**工段**: {section} ({section_name})\n")

        params = proc.get('parameters', {})

        if section == 'WT':
            output.append("### 2.1 原水规格\n")
            raw = params.get('raw_water', {})
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度 | {raw.get('temp', '')} | {raw.get('temp_unit', '')} |")
            output.append(f"| 压力范围 | {raw.get('pressure_min', '')}-{raw.get('pressure_max', '')} | {raw.get('pressure_unit', '')} |")
            output.append("")

            output.append("### 2.2 多介质过滤器\n")
            mmf = params.get('multimedia_filter', {})
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 设计流量 | {mmf.get('flow_rate', '')} | {mmf.get('flow_rate_unit', '')} |")
            output.append(f"| 反洗间隔 | {mmf.get('backwash_interval', '')} | {mmf.get('backwash_interval_unit', '')} |")
            output.append(f"| 滤料 | {mmf.get('filter_media', '')} | - |")
            output.append("")

            output.append("### 2.3 活性炭过滤器\n")
            acf = params.get('active_carbon_filter', {})
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 设计流量 | {acf.get('flow_rate', '')} | {acf.get('flow_rate_unit', '')} |")
            output.append(f"| 反洗间隔 | {acf.get('backwash_interval', '')} | {acf.get('backwash_interval_unit', '')} |")
            output.append("")

            output.append("### 2.4 RO反渗透系统\n")
            ro = params.get('ro_system', {})
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 产水流量 | {ro.get('flow_rate_product', '')} | {ro.get('flow_rate_unit', '')} |")
            output.append(f"| 回收率 | ≥{ro.get('recovery_rate_min', '')} | {ro.get('recovery_rate_unit', '')} |")
            output.append(f"| 产水电导率 | ≤{ro.get('conductivity_max', '')} | {ro.get('conductivity_unit', '')} |")
            output.append(f"| 运行压力 | {ro.get('pressure_normal', '')} | {ro.get('pressure_unit', '')} |")
            output.append("")

            output.append("### 2.5 离子交换系统\n")
            ion = params.get('ion_exchange', {})
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 出水电导率 | ≤{ion.get('conductivity_max', '')} | {ion.get('conductivity_unit', '')} |")
            output.append(f"| 再生周期 | {ion.get('regeneration_interval', '')} | {ion.get('regeneration_interval_unit', '')} |")
            output.append("")

            output.append("### 2.6 UV紫外线杀菌\n")
            uv = params.get('uv_sterilizer', {})
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 功率 | {uv.get('power', '')} | {uv.get('power_unit', '')} |")
            output.append(f"| 杀菌效率 | ≥{uv.get('efficacy_min', '')} | {uv.get('efficacy_unit', '')} |")
            output.append("")

            output.append("### 2.7 纯水储罐\n")
            storage = params.get('storage_tank', {})
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度上限 | {storage.get('temp_max', '')} | {storage.get('temp_unit', '')} |")
            output.append(f"| 温度报警值 | {storage.get('temp_alarm_high', '')} | ℃ |")
            output.append("")

        elif section == 'EX':
            for stage_num in [1, 2, 3]:
                stage_key = f'stage_{stage_num}'
                if stage_key in params:
                    stage = params.get(stage_key, {})
                    output.append(f"### 2.{stage_num} {stage.get('name', f'一级萃取罐')}\n")
                    output.append("| 参数 | 设定值 | 范围 | 单位 |")
                    output.append("|------|--------|------|------|")
                    output.append(f"| 罐体ID | {stage.get('tank_id', '')} | - | - |")
                    output.append(f"| 水温 | {stage.get('water_temp', '')} | {stage.get('water_temp_range', ['',''])[0]}-{stage.get('water_temp_range', ['',''])[1]} | {stage.get('water_temp_unit', '')} |")
                    output.append(f"| 茶叶加载量 | {stage.get('tea_load', '')} | - | {stage.get('tea_load_unit', '')} |")
                    output.append(f"| 加水量 | {stage.get('water_volume', '')} | - | {stage.get('water_volume_unit', '')} |")
                    output.append(f"| 萃取时间 | {stage.get('extraction_time', '')} | - | {stage.get('extraction_time_unit', '')} |")
                    output.append(f"| 搅拌速度 | {stage.get('agitation_speed', '')} | - | {stage.get('agitation_speed_unit', '')} |")
                    output.append("")

            sep = params.get('separation', {})
            output.append("### 2.4 茶渣分离\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 分离温度 | {sep.get('temperature', '')} | {sep.get('temperature_unit', '')} |")
            output.append(f"| 离心速度 | {sep.get('centrifuge_speed', '')} | {sep.get('centrifuge_speed_unit', '')} |")
            output.append(f"| 分离因数 | {sep.get('separation_factor', '')} | - |")
            output.append("")

            cool = params.get('cooling', {})
            output.append("### 2.5 冷却\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 目标温度 | {cool.get('target_temp', '')} | {cool.get('target_temp_unit', '')} |")
            output.append(f"| 冷却时间上限 | {cool.get('cooling_time_max', '')} | {cool.get('cooling_time_unit', '')} |")
            output.append("")

            batch = proc.get('batch_size', {})
            output.append("### 2.6 批次规格\n")
            output.append("| 产品 | 批次量 | 单位 |")
            output.append("|------|--------|------|")
            for prod, val in batch.items():
                if isinstance(val, dict):
                    output.append(f"| {prod} | {val.get('value', '')} | {val.get('unit', 'L/batch')} |")
                else:
                    output.append(f"| {prod} | {val} | L/batch |")
            output.append("")

        elif section == 'BL':
            tea_conc = params.get('tea_concentrate', {})
            output.append("### 2.1 茶浓缩汁\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| Brix | {tea_conc.get('brix', '')} | {tea_conc.get('brix_unit', '')} |")
            output.append(f"| pH | {tea_conc.get('ph', '')} | - |")
            output.append(f"| 温度上限 | {tea_conc.get('temp_max', '')} | {tea_conc.get('temp_unit', '')} |")
            output.append("")

            sugar = params.get('sugar_syrup', {})
            output.append("### 2.2 糖浆\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| Brix | {sugar.get('brix', '')} | {sugar.get('brix_unit', '')} |")
            output.append(f"| 温度 | {sugar.get('temp', '')} | {sugar.get('temp_unit', '')} |")
            output.append(f"| 溶解时间 | {sugar.get('dissolution_time', '')} | {sugar.get('dissolution_time_unit', '')} |")
            output.append("")

            acid = params.get('citric_acid_solution', {})
            output.append("### 2.3 柠檬酸溶液\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 浓度 | {acid.get('concentration', '')} | {acid.get('concentration_unit', '')} |")
            output.append(f"| 温度 | {acid.get('temp', '')} | {acid.get('temp_unit', '')} |")
            output.append("")

            target = params.get('target_blend', {})
            output.append("### 2.4 目标调配指标\n")
            output.append("| 参数 | 规格 | 容差 | 单位 |")
            output.append("|------|------|------|------|")
            output.append(f"| Brix | {target.get('brix', '')} | {target.get('brix_tolerance', '')} | {target.get('brix_unit', '')} |")
            output.append(f"| pH | {target.get('ph', '')} | {target.get('ph_tolerance', '')} | - |")
            output.append(f"| 温度 | {target.get('temp', '')} | {target.get('temp_range', ['',''])[0]}-{target.get('temp_range', ['',''])[1]} | {target.get('temp_unit', '')} |")
            output.append("")

            seq = params.get('blending_sequence', [])
            if seq:
                output.append("### 2.5 调配顺序\n")
                output.append("| 步骤 | 操作 | 参数 |")
                output.append("|------|------|------|")
                for step in seq:
                    step_str = f"{step.get('step', '')}"
                    action = step.get('action', '')
                    if 'target_brix' in step:
                        action += f", 目标Brix: {step.get('target_brix', '')}"
                    if 'target_ph' in step:
                        action += f", 目标pH: {step.get('target_ph', '')}"
                    if 'volume' in step:
                        action += f", 量: {step.get('volume', '')}{step.get('volume_unit', '')}"
                    if 'time' in step:
                        action += f", 时间: {step.get('time', '')}{step.get('time_unit', '')}"
                    if 'speed' in step:
                        action += f", 速度: {step.get('speed', '')}{step.get('speed_unit', '')}"
                    output.append(f"| {step_str} | {action} | - |")
                output.append("")

            qc = params.get('quality_check', [])
            if qc:
                output.append("### 2.6 质量检查\n")
                output.append("| 参数 | 仪器 | 频率 |")
                output.append("|------|------|------|")
                for item in qc:
                    output.append(f"| {item.get('parameter', '')} | {item.get('instrument', '')} | {item.get('frequency', '')} |")
                output.append("")

        elif section == 'HM':
            inlet = params.get('inlet', {})
            output.append("### 2.1 进料条件\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度 | {inlet.get('temp', '')} | {inlet.get('temp_unit', '')} |")
            output.append(f"| 压力下限 | {inlet.get('pressure_min', '')} | {inlet.get('pressure_unit', '')} |")
            output.append("")

            homo = params.get('homogenizer', {})
            output.append("### 2.2 均质机参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {homo.get('model', '')} | - |")
            output.append(f"| 压力设定 | {homo.get('pressure_setpoint', '')} | {homo.get('pressure_unit', '')} |")
            output.append(f"| 压力范围 | {homo.get('pressure_range', ['',''])[0]}-{homo.get('pressure_range', ['',''])[1]} | {homo.get('pressure_unit', '')} |")
            output.append(f"| 压力报警 | {homo.get('pressure_alarm_low', '')}-{homo.get('pressure_alarm_high', '')} | {homo.get('pressure_unit', '')} |")
            output.append(f"| 处理量 | {homo.get('capacity', '')} | {homo.get('capacity_unit', '')} |")
            output.append(f"| 电机功率 | {homo.get('motor_power', '')} | {homo.get('motor_power_unit', '')} |")
            output.append("")

            outlet = params.get('outlet', {})
            output.append("### 2.3 出料条件\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度上限 | {outlet.get('temp_max', '')} | {outlet.get('temp_unit', '')} |")
            output.append(f"| 压力 | {outlet.get('pressure_normal', '')} | {outlet.get('pressure_unit', '')} |")
            output.append("")

            valve_group = params.get('valve_group', {})
            output.append("### 2.4 阀门组\n")
            output.append("| 阀门 | 位号 |")
            output.append("|------|------|")
            output.append(f"| 进料阀 | {valve_group.get('inlet_valve', '')} |")
            output.append(f"| 出料阀 | {valve_group.get('outlet_valve', '')} |")
            output.append(f"| 旁通阀 | {valve_group.get('bypass_valve', '')} |")
            output.append("")

            startup = valve_group.get('startup_sequence', [])
            if startup:
                output.append("**启动顺序**:\n")
                for i, s in enumerate(startup, 1):
                    output.append(f"{i}. {s}\n")
                output.append("")

            shutdown = valve_group.get('shutdown_sequence', [])
            if shutdown:
                output.append("**停机顺序**:\n")
                for i, s in enumerate(shutdown, 1):
                    output.append(f"{i}. {s}\n")
                output.append("")

            particle = params.get('particle_size', {})
            output.append("### 2.5 粒度要求\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 目标粒径 | {particle.get('target', '')} | {particle.get('target_unit', '')} |")
            output.append(f"| 最大粒径 | {particle.get('max', '')} | {particle.get('target_unit', '')} |")
            output.append(f"| 测量方式 | {particle.get('measurement', '')} | - |")
            output.append("")

        elif section == 'UH':
            preheat = params.get('preheating', {})
            output.append("### 2.1 预热段\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度设定 | {preheat.get('temp_setpoint', '')} | {preheat.get('temp_unit', '')} |")
            output.append(f"| 温度范围 | {preheat.get('temp_range', ['',''])[0]}-{preheat.get('temp_range', ['',''])[1]} | {preheat.get('temp_unit', '')} |")
            output.append(f"| 保温时间 | {preheat.get('hold_time', '')} | {preheat.get('hold_time_unit', '')} |")
            output.append("")

            ster = params.get('sterilization', {})
            output.append("### 2.2 杀菌段\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度设定 | {ster.get('temp_setpoint', '')} | {ster.get('temp_unit', '')} |")
            output.append(f"| 温度范围 | {ster.get('temp_range', ['',''])[0]}-{ster.get('temp_range', ['',''])[1]} | {ster.get('temp_unit', '')} |")
            output.append(f"| 杀菌时间 | {ster.get('time', '')} | {ster.get('time_unit', '')} |")
            output.append(f"| 关键限值 | ≥{ster.get('critical_limit', '')} | {ster.get('critical_limit_unit', '')} |")
            output.append("")

            hold = params.get('holding', {})
            output.append("### 2.3 保温段\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度下限 | {hold.get('temp_min', '')} | {hold.get('temp_min_unit', '')} |")
            output.append(f"| 保温时间 | {hold.get('time', '')} | {hold.get('time_unit', '')} |")
            output.append("")

            cool = params.get('cooling', {})
            output.append("### 2.4 冷却段\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 一段温度 | {cool.get('stage_1_temp', '')} | {cool.get('stage_1_temp_unit', '')} |")
            output.append(f"| 二段温度 | {cool.get('stage_2_temp', '')} | {cool.get('stage_2_temp_unit', '')} |")
            output.append(f"| 出口温度 | {cool.get('outlet_temp', '')} | 最高{cool.get('outlet_temp_max', '')} | {cool.get('outlet_temp_unit', '')} |")
            output.append("")

            sys_info = params.get('system', {})
            output.append("### 2.5 系统参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 产品流量 | {sys_info.get('flow_rate', '')} | {sys_info.get('flow_rate_unit', '')} |")
            output.append(f"| 背压 | {sys_info.get('back_pressure', '')} | {sys_info.get('back_pressure_unit', '')} |")
            output.append("")

            quality_uht = params.get('quality', {})
            output.append("### 2.6 质量指标\n")
            output.append("| 参数 | 规格 |")
            output.append("|------|------|")
            output.append(f"| 灭菌标准 | {quality_uht.get('sterility', '')} |")
            output.append(f"| F₀值 | ≥{quality_uht.get('f0_value_min', '')} |")
            output.append(f"| 货架期 | {quality_uht.get('shelf_life', '')} {quality_uht.get('shelf_life_unit', '')} |")
            output.append("")

            aseptic = params.get('aseptic_tank', {})
            output.append("### 2.7 无菌储罐\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 罐体ID | {aseptic.get('tank_id', '')} | - |")
            output.append(f"| 容积 | {aseptic.get('capacity', '')} | {aseptic.get('capacity_unit', '')} |")
            output.append(f"| 温度上限 | {aseptic.get('temp_max', '')} | {aseptic.get('temp_unit', '')} |")
            output.append(f"| 压力上限 | {aseptic.get('pressure_max', '')} | {aseptic.get('pressure_unit', '')} |")
            output.append(f"| 正常压力 | {aseptic.get('pressure_normal', '')} | {aseptic.get('pressure_unit', '')} |")
            output.append("")

        elif section == 'PF':
            bottle = params.get('bottle', {})
            output.append("### 2.1 瓶子规格\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 材质 | {bottle.get('material', '')} | - |")
            output.append(f"| 公称容积 | {bottle.get('volume_nominal', '')} | {bottle.get('volume_unit', '')} |")
            output.append(f"| 实际容积范围 | {bottle.get('volume_actual_range', ['',''])[0]}-{bottle.get('volume_actual_range', ['',''])[1]} | {bottle.get('volume_unit', '')} |")
            output.append(f"| 灌装温度 | {bottle.get('temperature', '')} | {bottle.get('temperature_unit', '')} |")
            output.append("")

            filler = params.get('filler', {})
            output.append("### 2.2 灌装机参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {filler.get('model', '')} | - |")
            output.append(f"| 头数 | {filler.get('heads', '')} | - |")
            output.append(f"| 额定速度 | {filler.get('speed_nominal', '')} | {filler.get('speed_unit', '')} |")
            output.append(f"| 速度范围 | {filler.get('speed_range', ['',''])[0]}-{filler.get('speed_range', ['',''])[1]} | {filler.get('speed_unit', '')} |")
            output.append(f"| 灌装精度 | {filler.get('fill_accuracy', '')} | - |")
            output.append(f"| 液位精度 | {filler.get('level_accuracy', '')} | - |")
            output.append("")

            capper = params.get('capper', {})
            output.append("### 2.3 旋盖机参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {capper.get('model', '')} | - |")
            output.append(f"| 头数 | {capper.get('heads', '')} | - |")
            output.append(f"| 扭矩范围 | {capper.get('torque_min', '')}-{capper.get('torque_max', '')} | {capper.get('torque_unit', '')} |")
            output.append(f"| 密封检查 | {capper.get('seal_check', '')} | - |")
            output.append("")

            cooling = params.get('cooling', {})
            output.append("### 2.4 冷却参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 入口温度 | {cooling.get('inlet_temp', '')} | ℃ |")
            output.append(f"| 出口温度上限 | {cooling.get('outlet_temp_max', '')} | ℃ |")
            output.append(f"| 隧道长度 | {cooling.get('tunnel_length', '')} | {cooling.get('tunnel_length_unit', '')} |")
            output.append(f"| 冷却方式 | {cooling.get('cooling_method', '')} | - |")
            output.append("")

            quality_pf = params.get('quality', {})
            output.append("### 2.5 质量指标\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 泄漏率 | ≤{quality_pf.get('leak_rate_max', '')} | {quality_pf.get('leak_rate_unit', '')} |")
            output.append(f"| 顶隙高度 | {quality_pf.get('headspace_height', '')} | {quality_pf.get('headspace_height_unit', '')} |")
            output.append("")

        elif section == 'FL':
            disc = params.get('disc_centrifuge', {})
            output.append("### 2.1 碟式离心机\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {disc.get('model', '')} | - |")
            output.append(f"| 处理量 | {disc.get('capacity', '')} | {disc.get('capacity_unit', '')} |")
            output.append(f"| 转速 | {disc.get('speed', '')} | {disc.get('speed_unit', '')} |")
            output.append(f"| 分离因数 | {disc.get('separation_factor', '')} | - |")
            output.append(f"| 进口压力上限 | {disc.get('inlet_pressure_max', '')} | {disc.get('inlet_pressure_unit', '')} |")
            output.append("")

            uf = params.get('ultrafiltration', {})
            output.append("### 2.2 超滤膜组件\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 膜类型 | {uf.get('membrane_type', '')} | - |")
            output.append(f"| 孔径 | {uf.get('pore_size', '')} | {uf.get('pore_size_unit', '')} |")
            output.append(f"| 处理量 | {uf.get('capacity', '')} | {uf.get('capacity_unit', '')} |")
            output.append(f"| 进口压力 | {uf.get('inlet_pressure_normal', '')} | {uf.get('inlet_pressure_unit', '')} |")
            output.append(f"| 进口压力上限 | {uf.get('inlet_pressure_max', '')} | {uf.get('inlet_pressure_unit', '')} |")
            output.append(f"| 膜压差上限 | {uf.get('trans_membrane_pressure_max', '')} | {uf.get('trans_membrane_pressure_unit', '')} |")
            output.append(f"| 工作温度 | {uf.get('temperature_range', ['',''])[0]}-{uf.get('temperature_range', ['',''])[1]} | {uf.get('temperature_unit', '')} |")
            output.append(f"| 正常通量 | {uf.get('flux_normal', '')} | {uf.get('flux_unit', '')} |")
            output.append(f"| 反洗间隔 | {uf.get('backwash_interval', '')} | {uf.get('backwash_interval_unit', '')} |")
            output.append("")

    output.append("---")
    output.append("**文档状态**: 自动生成\n")
    output.append("**版本历史**:\n")
    output.append(f"- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本\n")

    return "\n".join(output)


def generate_cip_recipe():
    """生成CIP配方文档"""
    data = get_recipe_data()
    cip_recipes = data.get('cip_recipes', {})

    output = []
    output.append(generate_header("CIP清洗配方"))

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
    parser = argparse.ArgumentParser(description='SCADA 配方文档自动生成器')
    parser.add_argument('--generate', choices=['all', 'product', 'process', 'cip'],
                        default='all', help='要生成的文档类型')
    parser.add_argument('--output', default=str(OUTPUT_DIR), help='输出目录')

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print(f"SCADA 配方生成器")
    print(f"输出目录: {args.output}")
    print("-" * 50)

    if args.generate in ['all', 'product']:
        print("正在生成: 产品配方...")
        content = generate_product_recipe()
        output_file = Path(args.output) / OUTPUT_PRODUCT.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  完成: {output_file}")

    if args.generate in ['all', 'process']:
        print("正在生成: 工艺配方...")
        content = generate_process_recipe()
        output_file = Path(args.output) / OUTPUT_PROCESS.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  完成: {output_file}")

    if args.generate in ['all', 'cip']:
        print("正在生成: CIP配方...")
        content = generate_cip_recipe()
        output_file = Path(args.output) / OUTPUT_CIP.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  完成: {output_file}")

    if args.generate == 'all':
        print("\n所有配方文档生成完成!")
        print(f"输出目录: {args.output}")


if __name__ == '__main__':
    main()
