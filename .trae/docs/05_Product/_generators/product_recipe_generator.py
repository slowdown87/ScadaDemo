"""
产品配方生成器
茶饮料生产线 - 从 product_recipe_templates.yaml 生成产品配方文档

使用方法:
    python product_recipe_generator.py
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_PRODUCT = SCRIPT_DIR.parent / "configs" / "product_recipe_templates.yaml"
OUTPUT_PRODUCT = SCRIPT_DIR.parent / "auto" / "产品配方_auto.md"


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
>
> ⚠️ **本文件由系统配置自动生成 - 请勿手动修改**

---

## ⚠️ 重要声明

### 生成信息

| 项目 | 内容 |
| ---- | ---- |
| **数据来源** | `05_Product/configs/product_recipe_templates.yaml` |
| **生成器脚本** | `05_Product/_generators/product_recipe_generator.py` |
| **重新生成命令** | `python 05_Product/_generators/product_recipe_generator.py` |

### 修改流程

1. 编辑 `05_Product/configs/product_recipe_templates.yaml`
2. 运行 `python 05_Product/_generators/product_recipe_generator.py`
3. 检查生成的 `05_Product/auto/产品配方_auto.md`

---

"""


def generate_product_recipe():
    data = load_yaml(CONFIG_PRODUCT)
    products = data.get('product_recipes', {})
    acceptance = data.get('acceptance_standards', {})

    output = []
    output.append(generate_header("产品配方", CONFIG_PRODUCT))

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


def main():
    print("产品配方生成器")
    print("-" * 40)

    if not CONFIG_PRODUCT.exists():
        print(f"错误: 配置文件不存在: {CONFIG_PRODUCT}")
        return

    document = generate_product_recipe()
    OUTPUT_PRODUCT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PRODUCT, 'w', encoding='utf-8') as f:
        f.write(document)

    print(f"生成文档: {OUTPUT_PRODUCT}")
    print("\n完成!")


if __name__ == '__main__':
    main()