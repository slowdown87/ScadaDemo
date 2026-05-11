"""
工艺配方生成器
茶饮料生产线 - 从 process_recipe_templates.yaml 生成工艺配方文档

使用方法:
    python process_recipe_generator.py
    或通过 run_all_generators.py 调用
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_PROCESS = SCRIPT_DIR.parent / "01_Spec" / "configs" / "process_recipe_templates.yaml"
OUTPUT_PROCESS = SCRIPT_DIR.parent / "04_Process" / "auto" / "茶饮料_工艺配方_auto.md"


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
| **数据来源** | `01_Spec/configs/process_recipe_templates.yaml` |
| **生成器脚本** | `_generators/process_recipe_generator.py` |
| **重新生成命令** | `python _generators/run_all_generators.py --gen=Process_Recipe` |

### 修改流程

1. 编辑 `01_Spec/configs/process_recipe_templates.yaml`
2. 运行 `python _generators/run_all_generators.py --gen=Process_Recipe`
3. 检查生成的 `04_Process/auto/茶饮料_工艺配方_auto.md`

---

"""


def generate_process_recipe():
    data = load_yaml(CONFIG_PROCESS)
    processes = data.get('process_recipes', {})

    output = []
    output.append(generate_header("工艺配方", CONFIG_PROCESS))

    output.append("## 1. 工艺配方汇总\n")
    output.append("| 配方ID | 工艺名称 | 工段 | 关联清洗 |")
    output.append("|--------|----------|------|----------|")

    section_names = {
        'WT': '水处理', 'TH': '茶叶前处理', 'EX': '萃取',
        'FL': '过滤', 'BL': '调配', 'HM': '均质',
        'UH': 'UHT杀菌', 'PF': '灌装', 'CP': 'CIP站', 'PK': '包装'
    }

    for key, proc in processes.items():
        if not isinstance(proc, dict):
            continue
        section = proc.get('section', '')
        section_name = section_names.get(section, section)
        output.append(f"| {proc.get('recipe_id', '')} | {proc.get('name', '')} | {section} ({section_name}) | {proc.get('cleaning_recipe', '')} |")

    output.append("")

    for key, proc in processes.items():
        if not isinstance(proc, dict):
            continue
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

        elif section == 'TH':
            storage = params.get('storage', {})
            output.append("### 2.1 储茶罐\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 罐体ID | {storage.get('tank_id', '')} | - |")
            output.append(f"| 容量 | {storage.get('capacity', '')} | {storage.get('capacity_unit', '')} |")
            output.append(f"| 温度范围 | {storage.get('temp_range', ['',''])[0]}-{storage.get('temp_range', ['',''])[1]} | {storage.get('temp_unit', '')} |")
            output.append(f"| 湿度上限 | {storage.get('humidity_max', '')} | {storage.get('humidity_unit', '')} |")
            output.append("")

            mag = params.get('magnetic_separator', {})
            output.append("### 2.2 磁选机\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {mag.get('model', '')} | - |")
            output.append(f"| 磁场强度 | {mag.get('magnetic_strength', '')} | {mag.get('magnetic_strength_unit', '')} |")
            output.append(f"| 皮带速度 | {mag.get('belt_speed', '')} | {mag.get('belt_speed_unit', '')} |")
            output.append(f"| 处理量 | {mag.get('capacity', '')} | {mag.get('capacity_unit', '')} |")
            output.append("")

            metal = params.get('metal_detector', {})
            output.append("### 2.3 金属检测器\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {metal.get('model', '')} | - |")
            output.append(f"| 灵敏度 | {metal.get('sensitivity', '')} | {metal.get('sensitivity_unit', '')} |")
            output.append(f"| 检测类型 | {metal.get('detection_type', '')} | - |")
            output.append(f"| 剔除方式 | {metal.get('reject_mode', '')} | - |")
            output.append("")

        elif section == 'CP':
            cip_tank = params.get('cip_tank', {})
            output.append("### 2.1 CIP罐\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 酸罐ID | {cip_tank.get('acid_tank_id', '')} | - |")
            output.append(f"| 酸罐容量 | {cip_tank.get('acid_tank_capacity', '')} | {cip_tank.get('acid_tank_capacity_unit', '')} |")
            output.append(f"| 碱罐ID | {cip_tank.get('alkali_tank_id', '')} | - |")
            output.append(f"| 碱罐容量 | {cip_tank.get('alkali_tank_capacity', '')} | {cip_tank.get('alkali_tank_capacity_unit', '')} |")
            output.append(f"| 水罐ID | {cip_tank.get('water_tank_id', '')} | - |")
            output.append(f"| 水罐容量 | {cip_tank.get('water_tank_capacity', '')} | {cip_tank.get('water_tank_capacity_unit', '')} |")
            output.append("")

        elif section == 'PK':
            film = params.get('film_wrapper', {})
            output.append("### 2.1 膜包机\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {film.get('model', '')} | - |")
            output.append(f"| 膜宽 | {film.get('film_width', '')} | {film.get('film_width_unit', '')} |")
            output.append(f"| 膜厚范围 | {film.get('film_thickness_range', ['',''])[0]}-{film.get('film_thickness_range', ['',''])[1]} | {film.get('film_thickness_range_unit', '')} |")
            output.append(f"| 包装速度 | {film.get('package_speed', '')} | {film.get('package_speed_unit', '')} |")
            output.append("")

            robot = params.get('robot_palletizer', {})
            output.append("### 2.2 码垛机器人\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {robot.get('model', '')} | - |")
            output.append(f"| 负载 | {robot.get('payload', '')} | {robot.get('payload_unit', '')} |")
            output.append(f"| 臂展 | {robot.get('reach', '')} | {robot.get('reach_unit', '')} |")
            output.append(f"| 轴数 | {robot.get('axes', '')} | - |")
            output.append(f"| 循环时间 | {robot.get('cycle_time', '')} | {robot.get('cycle_time_unit', '')} |")
            output.append(f"| 定位精度 | {robot.get('position_accuracy', '')} | {robot.get('position_accuracy_unit', '')} |")
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

        elif section == 'BL':
            target = params.get('target_blend', {})
            output.append("### 2.1 目标调配指标\n")
            output.append("| 参数 | 规格 | 容差 | 单位 |")
            output.append("|------|------|------|------|")
            output.append(f"| Brix | {target.get('brix', '')} | {target.get('brix_tolerance', '')} | {target.get('brix_unit', '')} |")
            output.append(f"| pH | {target.get('ph', '')} | {target.get('ph_tolerance', '')} | - |")
            output.append(f"| 温度 | {target.get('temp', '')} | {target.get('temp_range', ['',''])[0]}-{target.get('temp_range', ['',''])[1]} | {target.get('temp_unit', '')} |")
            output.append("")

        elif section == 'HM':
            homo = params.get('homogenizer', {})
            output.append("### 2.1 均质机参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {homo.get('model', '')} | - |")
            output.append(f"| 压力设定 | {homo.get('pressure_setpoint', '')} | {homo.get('pressure_unit', '')} |")
            output.append(f"| 压力范围 | {homo.get('pressure_range', ['',''])[0]}-{homo.get('pressure_range', ['',''])[1]} | {homo.get('pressure_unit', '')} |")
            output.append(f"| 处理量 | {homo.get('capacity', '')} | {homo.get('capacity_unit', '')} |")
            output.append("")

        elif section == 'UH':
            preheat = params.get('preheating', {})
            output.append("### 2.1 预热段\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度设定 | {preheat.get('temp_setpoint', '')} | {preheat.get('temp_unit', '')} |")
            output.append(f"| 温度范围 | {preheat.get('temp_range', ['',''])[0]}-{preheat.get('temp_range', ['',''])[1]} | {preheat.get('temp_unit', '')} |")
            output.append("")

            ster = params.get('sterilization', {})
            output.append("### 2.2 杀菌段\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 温度设定 | {ster.get('temp_setpoint', '')} | {ster.get('temp_unit', '')} |")
            output.append(f"| 杀菌时间 | {ster.get('time', '')} | {ster.get('time_unit', '')} |")
            output.append(f"| 关键限值 | ≥{ster.get('critical_limit', '')} | {ster.get('critical_limit_unit', '')} |")
            output.append("")

            sys_info = params.get('system', {})
            output.append("### 2.3 系统参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 产品流量 | {sys_info.get('flow_rate', '')} | {sys_info.get('flow_rate_unit', '')} |")
            output.append(f"| 背压 | {sys_info.get('back_pressure', '')} | {sys_info.get('back_pressure_unit', '')} |")
            output.append("")

        elif section == 'PF':
            bottle = params.get('bottle', {})
            output.append("### 2.1 瓶子规格\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 材质 | {bottle.get('material', '')} | - |")
            output.append(f"| 公称容积 | {bottle.get('volume_nominal', '')} | {bottle.get('volume_unit', '')} |")
            output.append(f"| 灌装温度 | {bottle.get('temperature', '')} | {bottle.get('temperature_unit', '')} |")
            output.append("")

            filler = params.get('filler', {})
            output.append("### 2.2 灌装机参数\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {filler.get('model', '')} | - |")
            output.append(f"| 头数 | {filler.get('heads', '')} | - |")
            output.append(f"| 额定速度 | {filler.get('speed_nominal', '')} | {filler.get('speed_unit', '')} |")
            output.append(f"| 灌装精度 | {filler.get('fill_accuracy', '')} | - |")
            output.append("")

        elif section == 'FL':
            disc = params.get('disc_centrifuge', {})
            output.append("### 2.1 碟式离心机\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 型号 | {disc.get('model', '')} | - |")
            output.append(f"| 处理量 | {disc.get('capacity', '')} | {disc.get('capacity_unit', '')} |")
            output.append(f"| 转速 | {disc.get('speed', '')} | {disc.get('speed_unit', '')} |")
            output.append("")

            uf = params.get('ultrafiltration', {})
            output.append("### 2.2 超滤膜组件\n")
            output.append("| 参数 | 规格 | 单位 |")
            output.append("|------|------|------|")
            output.append(f"| 膜类型 | {uf.get('membrane_type', '')} | - |")
            output.append(f"| 孔径 | {uf.get('pore_size', '')} | {uf.get('pore_size_unit', '')} |")
            output.append(f"| 处理量 | {uf.get('capacity', '')} | {uf.get('capacity_unit', '')} |")
            output.append(f"| 进口压力 | {uf.get('inlet_pressure_normal', '')} | {uf.get('inlet_pressure_unit', '')} |")
            output.append("")

    output.append("---")
    output.append("**文档状态**: 自动生成\n")
    output.append("**版本历史**:\n")
    output.append(f"- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 自动生成版本\n")

    return "\n".join(output)


def main():
    print("工艺配方生成器")
    print("-" * 40)

    if not CONFIG_PROCESS.exists():
        print(f"错误: 配置文件不存在: {CONFIG_PROCESS}")
        return

    document = generate_process_recipe()
    OUTPUT_PROCESS.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PROCESS, 'w', encoding='utf-8') as f:
        f.write(document)

    print(f"生成文档: {OUTPUT_PROCESS}")
    print("\n完成!")


if __name__ == '__main__':
    main()