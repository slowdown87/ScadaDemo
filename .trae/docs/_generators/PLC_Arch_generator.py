#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC_Architecture_generator.py
茶饮料生产线SCADA系统 - PLC架构文档生成器
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "01_Spec" / "configs" / "system_config.yaml"
OUTPUT_FILE = PROJECT_ROOT / "02_Arch" / "auto" / "茶饮料_PLC架构_auto.md"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg):
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {msg}")

def log_success(msg):
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {msg}")

def log_warning(msg):
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {msg}")

def log_error(msg):
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {msg}")

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

def generate_plc_architecture(config):
    meta = config['meta']
    plcs = config['plcs']
    sections = config['sections']
    process_flow = config['process_flow']
    high_speed_sync = config['high_speed_sync']
    plc_comm_matrix = config['plc_comm_matrix']
    scada_components = config['scada_components']
    ob_config = config['ob_config']
    io_summary = config['io_summary']

    sorted_plcs = sorted(plcs.values(), key=lambda x: x.get('process_order', 0))
    prefix_map = {sec_id: sec.get('prefix', sec_id) for sec_id, sec in sections.items()}
    liquid_plcs = [p for p in sorted_plcs if p['section'] in process_flow['liquid_line']['sections']]
    packaging_plcs = [p for p in sorted_plcs if p['section'] in process_flow['packaging_line']['sections']]
    independent_plcs = [p for p in sorted_plcs if p['section'] in process_flow['independent_systems']['sections']]

    doc = ""
    doc += "# 茶饮料生产线PLC架构设计\n\n"
    doc += "> 文档版本: " + meta['version'] + "\n"
    doc += "> 创建日期: " + meta['created'][:10] + "\n"
    doc += "> 更新日期: " + datetime.now().strftime('%Y-%m-%d') + "\n"
    doc += "> 架构: **" + str(len(plcs)) + "个独立PLC分布式架构**(FL与HM分开)\n"
    doc += ">\n"
    doc += "> **本文件由系统配置自动生成 - 请勿手动修改**\n\n"
    doc += "---\n\n"
    doc += "## 重要声明\n\n"
    doc += "**本文档为茶饮料生产线的基准架构文档**,所有其他文档(通讯接口规格书,设备参数表,位号编码规则等)必须以此为准。\n\n"
    doc += "### 生成信息\n\n"
    doc += "| 项目 | 内容 |\n"
    doc += "| ---- | ---- |\n"
    doc += "| **数据来源** | `01_Spec/configs/system_config.yaml` |\n"
    doc += "| **生成器脚本** | `docs/_generators/PLC_Arch_generator.py` |\n"
    doc += "| **重新生成命令** | `python docs/_generators/run_all_generators.py` |\n\n"
    doc += "### 修改流程\n\n"
    doc += "1. 编辑 `01_Spec/configs/system_config.yaml`\n"
    doc += "2. 运行 `python docs/_generators/run_all_generators.py`\n"
    doc += "3. 检查生成的 `02_Arch/auto/PLC_Architecture_auto.md`\n\n"
    doc += "---\n\n"
    doc += "## 1. 系统架构\n\n"
    doc += "### 1.1 架构概述\n\n"
    doc += "| 项目 | 参数 |\n"
    doc += "|------|------|\n"
    doc += "| PLC数量 | **" + str(len(plcs)) + "个**(液料线" + str(len(process_flow['liquid_line']['sections'])) + "个+包装线" + str(len(process_flow['packaging_line']['sections'])) + "个+CIP " + str(len(process_flow['independent_systems']['sections'])) + "个+备1个) |\n"
    doc += "| 控制系统 | 西门子S7-1500系列 |\n"
    doc += "| 通讯网络 | PROFINET(100Mbps)+ Industrial Ethernet |\n"
    doc += "| 冗余方式 | PLC冗余(CPU mirroring)+ 网络冗余(HRP环网) |\n"
    doc += "| 拓扑结构 | 设备层 -> 车间层 -> 监控层 |\n"
    doc += "| 产品类型 | " + meta['product_type'] + " |\n"
    doc += "| 产能 | " + meta['capacity'] + " |\n\n"

    doc += "### 1.2 网络架构图\n\n"
    doc += "```\n"
    doc += "三层架构:\n\n"
    doc += "[监控层] SCADA主站(" + scada_components['scada_primary']['ip'] + ") <-> SCADA备站(" + scada_components['scada_backup']['ip'] + ")\n"
    doc += "     |\n"
    doc += "     | PROFINET\n"
    doc += "     |\n"
    doc += "[控制层] 核心交换机1(" + scada_components['core_switch_1']['ip'] + ") <-> 核心交换机2(" + scada_components['core_switch_2']['ip'] + ")\n"
    doc += "     |\n"
    doc += "     | H-Sync光纤环网\n"
    doc += "     |\n"
    doc += "[设备层]\n"
    doc += "  液料线: " + liquid_plcs[0]['ip'] + " WT水处理, " + liquid_plcs[1]['ip'] + " TH茶叶前处理, " + liquid_plcs[2]['ip'] + " EX萃取\n"
    doc += "         " + liquid_plcs[3]['ip'] + " FL过滤, " + liquid_plcs[4]['ip'] + " BL调配, " + liquid_plcs[5]['ip'] + " HM均质, " + liquid_plcs[6]['ip'] + " UH UHT杀菌\n"
    doc += "  包装线: " + packaging_plcs[0]['ip'] + " BF制瓶, " + packaging_plcs[1]['ip'] + " PF灌装, " + packaging_plcs[2]['ip'] + " CG旋盖, " + packaging_plcs[3]['ip'] + " LI灯检, " + packaging_plcs[4]['ip'] + " CI喷码\n"
    doc += "         " + packaging_plcs[5]['ip'] + " LB贴标, " + packaging_plcs[6]['ip'] + " CA装箱, " + packaging_plcs[7]['ip'] + " PK膜包码垛\n"
    doc += "  独立系统: " + independent_plcs[0]['ip'] + " CP CIP清洗\n"
    doc += "```\n\n"

    doc += "### 1.3 工艺流程顺序与PLC分配\n\n"
    doc += "```\n"
    doc += "液料生产线:\n"
    doc += "WT -> TH -> EX -> FL -> BL -> HM -> UH\n"
    doc += "WT水处理  TH茶叶前处理  EX萃取  FL过滤  BL调配  HM均质  UH UHT杀菌\n\n"
    doc += "包装生产线:\n"
    doc += "BF -> PF -> CG -> LI -> CI -> LB -> CA -> PK\n"
    doc += "BF制瓶  PF灌装  CG旋盖  LI灯检  CI喷码  LB贴标  CA装箱  PK膜包码垛\n\n"
    doc += "独立系统:\n"
    doc += "CP (CIP清洗)\n"
    doc += "```\n\n"
    doc += "---\n\n"

    doc += "## 2. PLC配置\n\n"
    doc += "### 2.1 PLC配置表\n\n"
    doc += "| PLC编号 | 控制工段 | CPU型号 | 通讯接口 | 冗余方式 | I/O估算 | 备注 |\n"
    doc += "| ------ | --------- | ------------- | ---- | ---------- | ------ | --------- |\n"

    for plc in sorted_plcs:
        remark = plc.get('role', '')
        if plc.get('is_ccp'):
            remark = "**CCP关键**"
        if plc.get('is_high_speed'):
            remark = "**" + remark + "**" if remark else "**超高速**"
        doc += "| " + prefix_map.get(plc['section'], plc['name']) + " | " + plc['name'] + " | " + plc['name_en'] + " | " + plc['cpu'] + " | " + plc['通讯接口'] + " | " + plc['冗余方式'] + " | " + plc['io_estimate'] + " | " + remark + " |\n"

    doc += "\n**I/O总计**: 约" + str(io_summary['total_estimated']) + "点(液料线" + str(io_summary['liquid_line']) + "点 + 包装线" + str(io_summary['packaging_line']) + "点 + CIP" + str(io_summary['independent']) + "点)\n\n"

    doc += "### 2.2 IP地址规划表 (基于" + config['meta']['base_ip_subnet'] + ")\n\n"
    doc += "> **IP段**: " + config['meta']['base_ip_subnet'] + "(备选段,避免与办公网络冲突)\n"
    doc += "> **网关**: " + config['meta']['gateway'] + "\n"
    doc += "> **子网掩码**: " + config['meta']['subnet_mask'] + "\n\n"
    doc += "| PLC编号 | 控制工段 | IP地址 | 备注 |\n"
    doc += "|---------|----------|--------|------|\n"

    for plc in sorted_plcs:
        remark = plc.get('role', '')
        if plc.get('is_ccp'):
            remark = "CCP关键"
        doc += "| " + prefix_map.get(plc['section'], plc['name']) + " | " + plc['name_en'] + " | " + plc['ip'] + " | " + remark + " |\n"

    doc += "| SCADA主服务器 | - | " + scada_components['scada_primary']['ip'] + " | |\n"
    doc += "| SCADA备服务器 | - | " + scada_components['scada_backup']['ip'] + " | |\n"
    doc += "| 工程师站 | - | " + scada_components['engineer_station']['ip'] + " | |\n"
    doc += "| 核心交换机1 | - | " + scada_components['core_switch_1']['ip'] + " | " + scada_components['core_switch_1']['role'] + " |\n"
    doc += "| 核心交换机2 | - | " + scada_components['core_switch_2']['ip'] + " | " + scada_components['core_switch_2']['role'] + " |\n\n"

    doc += "### 2.3 控制系统职责划分\n\n"
    doc += "| PLC | 工段名称 | 主要控制任务 | 上游接口 | 下游接口 | 关键控制点 |\n"
    doc += "| ------ | --------- | ----------------- | ------- | ------ | --------------- |\n"

    for plc in sorted_plcs:
        section = sections[plc['section']]
        upstream = ", ".join(section.get('upstream', [])) or "-"
        downstream = ", ".join(section.get('downstream', [])) or "-"
        ctrl_level = "CCP" if plc.get('is_ccp') else "P1"
        doc += "| " + plc['name'] + " | " + plc['name'] + " | " + plc['role'] + " | " + upstream + " | " + downstream + " | " + ctrl_level + " |\n"

    doc += "\n### 2.4 PLC选型说明\n\n"
    doc += "| CPU型号 | 应用PLC | 选型理由 |\n"
    doc += "| ------------- | ------------------------------ | --------------------- |\n"

    cpu_groups = {}
    for plc in sorted_plcs:
        cpu = plc['cpu']
        if cpu not in cpu_groups:
            cpu_groups[cpu] = []
        cpu_groups[cpu].append(plc['name'])

    for cpu, plc_list in cpu_groups.items():
        if "1517" in cpu:
            reason = "高性能处理能力,满足批次控制和高速同步需求"
        elif "1215C" in cpu:
            reason = "入门级,喷码机通常自带PLC,仅需通讯对接"
        else:
            reason = "标准性能,满足一般控制需求"
        doc += "| " + cpu + " | " + ", ".join(plc_list) + " | " + reason + " |\n"

    doc += "\n---\n\n"

    doc += "## 3. 程序架构\n\n"
    doc += "### 3.1 项目总体结构\n\n"
    doc += "```\n"
    doc += "SCADA_Project\n"

    for plc in sorted_plcs:
        section = sections[plc['section']]
        plc_short = plc['name'].split('-')[0].replace('PLC-', '')
        doc += "+______________________________\n"
        doc += "|  |__ PLC_" + plc_short + "_" + section['prefix'] + "_" + section['name_en'].replace(' ', '') + "\n"
        doc += "|      |-- PLC_" + plc_short + "_" + section['prefix'] + ".config\n"
        doc += "|      |__ Program_" + plc_short + "\n"
        doc += "|          |-- OB1_Main\n"
        doc += "|          |-- OB100_StartUp\n"
        doc += "|          |__ Functions\n"

    doc += "+-- SCADA_Project.db\n"
    doc += "```\n\n"
    doc += "---\n\n"

    doc += "## 4. 高速同步与通讯\n\n"
    doc += "### 4.1 同步需求分析\n\n"
    doc += "| 高速同步对 | 同步周期 | 同步内容 | 精度要求 |\n"
    doc += "| ---------- | -------- | -------- | -------- |\n"

    for sync in high_speed_sync:
        doc += "| " + sync['from_section'] + " -> " + sync['to_section'] + " | **" + str(sync['period_ms']) + "ms** | " + sync['content'] + " | +/-" + str(sync['precision_ms']) + "ms |\n"

    doc += "\n### 4.2 PLC间通讯矩阵\n\n"
    doc += "| 发送方 | 接收方 | 通讯方式 | 数据内容 | 周期 | 说明 |\n"
    doc += "| ---------- | ---------- | -------------- | -------- | -------- | -------- |\n"

    for comm in plc_comm_matrix:
        receivers = comm['to'] if isinstance(comm['to'], list) else [comm['to']]
        receiver_str = ", ".join(receivers)
        doc += "| " + comm['from'] + " | " + receiver_str + " | " + comm['method'] + " | " + comm['data'] + " | " + str(comm['period_ms']) + "ms | " + comm['desc'] + " |\n"

    doc += "\n---\n\n"

    doc += "## 5. 中断与时间控制\n\n"
    doc += "### 5.1 中断组织块配置\n\n"
    doc += "| OB | 类型 | 循环时间 | 应用PLC | 说明 |\n"
    doc += "| --- | -------------- | -------- | -------------- | ------------ |\n"

    for ob_name, ob_info in ob_config.items():
        cycle = str(ob_info.get('cycle_ms', '-')) + "ms" if 'cycle_ms' in ob_info else "-"
        applies_to = ", ".join(ob_info['applies_to']) if isinstance(ob_info['applies_to'], list) else ob_info['applies_to']
        doc += "| " + ob_name + " | " + ob_info['type'] + " | " + cycle + " | " + applies_to + " | " + ob_info['desc'] + " |\n"

    doc += "\n### 5.2 关键时序要求\n\n"
    doc += "| 工段 | 时间要求 | 说明 |\n"
    doc += "| ---- | -------- | ---- |\n"
    doc += "| UHT杀菌温度 | 10ms响应 | CCP关键控制点 |\n"
    doc += "| 灌装同步 | 1ms精度 | 72ms周期要求 |\n"
    doc += "| 旋盖扭矩 | 5ms响应 | 品质控制 |\n"
    doc += "| 瓶位同步 | 1ms精度 | 高速线同步 |\n\n"
    doc += "---\n\n"

    doc += "## 6. 版本记录\n\n"
    doc += "| 版本 | 日期 | 变更内容 |\n"
    doc += "| ------ | ------ | ---------- |\n"
    doc += "| v1.0 | 2026-04-30 | 初始版本,从system_config.yaml自动生成 |\n\n"
    doc += "---\n\n"
    doc += "**文档状态**: 自动生成\n"
    doc += "**生成时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n"
    doc += "**审核状态**: 待审核\n"
    doc += "**批准人**: -\n"

    return doc

def main():
    log_info("=" * 60)
    log_info("PLC_Architecture_generator.py - PLC架构文档生成器")
    log_info("=" * 60)

    if not CONFIG_FILE.exists():
        log_error(f"配置文件未找到: {CONFIG_FILE}")
        log_info("请确保 configs/system_config.yaml 存在")
        sys.exit(1)

    log_info(f"读取配置文件: {CONFIG_FILE}")
    config = load_yaml(CONFIG_FILE)
    log_success(f"配置加载成功: {config['meta']['version']}")

    log_info("生成PLC架构文档...")
    doc = generate_plc_architecture(config)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(doc)

    log_success(f"文档生成成功: {OUTPUT_FILE}")
    log_info("=" * 60)

if __name__ == "__main__":
    main()
