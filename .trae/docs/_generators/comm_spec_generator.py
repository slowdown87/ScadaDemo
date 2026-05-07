"""
通讯接口规格书生成器
茶饮料生产线 - 从 comm_templates.yaml 生成通讯接口规格书

使用方法:
    python comm_spec_generator.py
"""

import os
import yaml
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
CONFIG_COMM = SCRIPT_DIR.parent / "configs" / "comm_templates.yaml"
OUTPUT_COMM = SCRIPT_DIR.parent / "auto" / "通讯接口规格书_auto.md"


def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_meta_data(config_file):
    data = load_yaml(config_file)
    return data.get('meta', {})


def generate_header(version="v2.0"):
    meta = get_meta_data(CONFIG_COMM)
    now = datetime.now().strftime("%Y-%m-%d")
    ip_segment = meta.get('ip_segment', '192.168.2.x')
    return f"""# 茶饮料生产线SCADA监控系统通讯接口规格书

> 文档版本: {version}
> 创建日期: {now}
> 更新日期: {now}
> 数据来源: comm_templates.yaml (自动生成)
> 项目名称: {meta.get('project_name', '茶饮料生产线SCADA监控系统')}
> 产品类型: {meta.get('product_type', '纯茶饮料')}
> 产能: {meta.get('capacity', '50000B/H')}
> IP段: {ip_segment}
>
> ⚠️ **本文件由系统配置自动生成 - 请勿手动修改**

---

## ⚠️ 重要声明

### 生成信息

| 项目 | 内容 |
| ---- | ---- |
| **数据来源** | `04_Process/configs/comm_templates.yaml` |
| **生成器脚本** | `04_Process/_generators/comm_spec_generator.py` |
| **重新生成命令** | `python 04_Process/_generators/comm_spec_generator.py` |

### 修改流程

1. 编辑 `04_Process/configs/comm_templates.yaml`
2. 运行 `python 04_Process/_generators/comm_spec_generator.py`
3. 检查生成的 `04_Process/auto/通讯接口规格书_auto.md`

---

**基准架构文档**: PLC_Architecture_auto.md v1.0

---

"""


def generate_overview():
    data = load_yaml(CONFIG_COMM)
    protocol = data.get('protocol_params', {})

    output = []
    output.append("## 1. 概述\n")
    output.append("### 1.1 文档目的\n")
    output.append("本文档定义SCADA系统与15个PLC、智能仪表、第三方系统之间的通讯接口规格，作为系统集成和调试的依据。\n")

    output.append("### 1.2 通讯资源统计\n")
    output.append("| 协议 | 设备数量 | 点位数量 | 备注 |\n")
    output.append("|------|----------|----------|------|\n")

    eth_ip = protocol.get('ethernet_ip', {})
    output.append(f"| Ethernet/IP (PLC) | 15 | ~1970点 | S7-1500冗余 |\n")

    modbus_tcp = protocol.get('modbus_tcp', {})
    output.append(f"| Modbus TCP | {modbus_tcp.get('devices', 6)} | {modbus_tcp.get('points', 48)}点 | 电能表、流量计等 |\n")

    modbus_rtu = protocol.get('modbus_rtu', {})
    output.append(f"| Modbus RTU | {modbus_rtu.get('devices', 28)} | {modbus_rtu.get('points', 112)}点 | 串口通讯 |\n")

    hart = protocol.get('hart', {})
    output.append(f"| HART | {hart.get('devices', 4)} | {hart.get('points', 4)}点 | pH计 |\n")

    opc_ua = protocol.get('opc_ua', {})
    output.append(f"| OPC UA | 1 | {opc_ua.get('points', 200)}点 | MES系统对接 |\n")

    output.append("\n")
    return "".join(output)


def generate_plc_config():
    data = load_yaml(CONFIG_COMM)
    plc_list = data.get('plc_config', [])
    ip_planning = data.get('ip_planning', {})
    servers = ip_planning.get('servers', [])

    output = []
    output.append("## 2. PLC通讯规格\n")

    output.append("### 2.1 PLC配置表\n")
    output.append("| PLC编号 | 控制工段 | IP地址 | CPU型号 | 冗余 | I/O估算 |\n")
    output.append("|---------|----------|--------|---------|------|----------|\n")

    for plc in plc_list:
        plc_id = plc.get('id', '')
        sections = ",".join(plc.get('sections', []))
        section_names = ",".join(plc.get('section_names', []))
        ip = plc.get('ip', '')
        cpu_name = plc.get('name', '')
        redundant = "H-Sync光纤环网" if plc.get('redundant', False) else "无"
        data_area = plc.get('data_area', {})
        di_points = data_area.get('di', {}).get('points', 0)
        do_points = data_area.get('do', {}).get('points', 0)
        ai_points = data_area.get('ai', {}).get('points', 0)
        ao_points = data_area.get('ao', {}).get('points', 0)
        total_points = di_points + do_points + ai_points + ao_points
        output.append(f"| {plc_id} | {sections}({section_names}) | {ip} | {cpu_name} | {redundant} | ~{total_points}点 |\n")

    output.append("\n")

    output.append("### 2.2 Ethernet/IP通讯参数\n")
    output.append("| 参数 | 规格 |\n")
    output.append("|------|------|\n")
    eth_ip = data.get('protocol_params', {}).get('ethernet_ip', {})
    output.append(f"| 协议 | Ethernet/IP |\n")
    output.append(f"| 扫描周期 | {eth_ip.get('scan_cycle', '100ms')} |\n")
    output.append(f"| 通讯冗余 | {eth_ip.get('redundancy', '双网口绑定')} |\n")
    output.append(f"| 超时处理 | {eth_ip.get('timeout', '3次重试后报警')} |\n")

    for server in servers:
        device = server.get('device', '')
        ip = server.get('ip', '')
        if 'SCADA' in device and 'BACKUP' not in device:
            output.append(f"| SCADA主服务器 | {ip} |\n")
        elif 'BACKUP' in device:
            output.append(f"| SCADA备服务器 | {ip} |\n")

    output.append("\n")
    return "".join(output)


def generate_data_areas():
    data = load_yaml(CONFIG_COMM)
    plc_list = data.get('plc_config', [])

    output = []
    output.append("### 2.3 数据点位规划\n")

    for plc in plc_list:
        plc_id = plc.get('id', '')
        sections = ",".join(plc.get('sections', []))
        section_names = ",".join(plc.get('section_names', []))
        data_area = plc.get('data_area', {})

        output.append(f"#### PLC-{plc_id} 数据区 ({sections})\n")
        output.append("| 数据类型 | 地址区 | 点数 | 说明 |\n")
        output.append("|----------|--------|------|------|\n")

        di = data_area.get('di', {})
        do = data_area.get('do', {})
        ai = data_area.get('ai', {})
        ao = data_area.get('ao', {})

        output.append(f"| DI | {di.get('start', 'I0.0')} - {di.get('end', 'Ix.x')} | {di.get('points', 0)} | {di.get('desc', '')} |\n")
        output.append(f"| DO | {do.get('start', 'Q0.0')} - {do.get('end', 'Qx.x')} | {do.get('points', 0)} | {do.get('desc', '')} |\n")
        output.append(f"| AI | {ai.get('start', 'IW0')} - {ai.get('end', 'IWx')} | {ai.get('points', 0)} | {ai.get('desc', '')} |\n")
        output.append(f"| AO | {ao.get('start', 'QW0')} - {ao.get('end', 'QWx')} | {ao.get('points', 0)} | {ao.get('desc', '')} |\n")

        output.append("\n")

    output.append("---\n\n")
    return "".join(output)


def generate_plc_comm():
    output = []
    output.append("## 3. PLC间通讯\n")
    output.append("### 3.1 PROFINET I-Device通讯\n")
    output.append("| 通讯方向 | 通讯方式 | 数据内容 | 刷新周期 | 备注 |\n")
    output.append("|----------|----------|----------|----------|------|\n")

    comm_pairs = [
        ("PLC-1 → PLC-3", "PROFINET I-Device", "纯水产水量、茶原料量", "100ms", "实时同步"),
        ("PLC-1 → PLC-5", "PROFINET I-Device", "纯水产水量", "100ms", "调配用水"),
        ("PLC-3 → PLC-4", "PROFINET I-Device", "茶汁流量、温度、批次完成", "50ms", "批次信号"),
        ("PLC-4 → PLC-5", "PROFINET I-Device", "调配液流量、批次完成", "50ms", "批次信号"),
        ("PLC-5 → PLC-6", "PROFINET I-Device", "流量、压力、温度", "20ms", "高速同步"),
        ("PLC-6 → PLC-7", "PROFINET I-Device", "无菌料信号、速度主令", "10ms", "**超高速**"),
        ("PLC-7 → PLC-8", "PROFINET I-Device", "瓶速、瓶位", "10ms", "同步控制"),
        ("PLC-8 → PLC-9", "PROFINET I-Device", "旋盖速度、扭矩设定", "10ms", "同步控制"),
        ("PLC-9 → PLC-10", "PROFINET I-Device", "产品计数、合格信号", "50ms", "检测触发"),
        ("PLC-10 → PLC-11", "PROFINET I-Device", "剔除信号", "50ms", "不合格跳过"),
        ("PLC-11 → PLC-12", "PROFINET I-Device", "喷码内容、打印完成", "50ms", "标签信息"),
        ("PLC-12 → PLC-13", "PROFINET I-Device", "产品计数", "100ms", "装箱触发"),
        ("PLC-13 → PLC-14", "PROFINET I-Device", "纸箱计数", "100ms", "码垛触发"),
        ("PLC-8 → PLC-1~6", "PROFINET I-Device", "急停/清洗请求", "10ms", "安全联锁"),
    ]

    for pair in comm_pairs:
        output.append(f"| {pair[0]} | {pair[1]} | {pair[2]} | {pair[3]} | {pair[4]} |\n")

    output.append("\n---\n\n")
    return "".join(output)


def generate_third_party():
    data = load_yaml(CONFIG_COMM)
    third_party = data.get('third_party_interfaces', {})
    smart = data.get('smart_devices', {})

    output = []
    output.append("## 4. 与第三方系统通讯\n")

    output.append("### 4.1 MES系统 (OPC UA)\n")
    mes = third_party.get('mes_opcua', {})
    output.append("| 参数 | 规格 |\n")
    output.append("|------|------|\n")
    output.append(f"| 协议 | {mes.get('protocol', 'OPC UA')} |\n")
    output.append(f"| 点位数量 | ~{mes.get('data_count', 200)}点 |\n")
    output.append(f"| 数据类型 | 批次数据、配方参数、产品追溯 |\n")
    output.append(f"| 刷新周期 | 按需 |\n")
    output.append("\n")

    output.append("### 4.2 智能仪表 (Modbus TCP)\n")
    modbus_tcp = data.get('protocol_params', {}).get('modbus_tcp', {})
    output.append("| 设备 | 数量 | 点位 | 备注 |\n")
    output.append("|------|------|------|------|\n")
    output.append(f"| 电能表 | 4 | 32点 | 各工段电力监控 |\n")
    output.append(f"| 流量计 | 3 | 24点 | 原水、产品流量 |\n")
    output.append(f"| 液位计 | 1 | 8点 | 储罐液位 |\n")
    output.append("\n")

    output.append("---\n\n")
    return "".join(output)


def generate_change_log():
    now = datetime.now().strftime("%Y-%m-%d")
    output = []
    output.append("## 5. 文档变更记录\n")
    output.append("| 版本 | 日期 | 变更内容 |\n")
    output.append("|------|------|----------|\n")
    output.append(f"| v1.0 | 2026-04-28 | 初始版本 |\n")
    output.append(f"| v2.0 | {now} | 自动生成，IP段更新为192.168.2.x |\n")
    output.append("\n\n")
    output.append("---\n\n")
    output.append("**文档状态**: 自动生成\n")
    output.append(f"**生成时间**: {now}\n")
    return "".join(output)


def generate_comm_spec():
    document = []
    document.append(generate_header())
    document.append(generate_overview())
    document.append(generate_plc_config())
    document.append(generate_data_areas())
    document.append(generate_plc_comm())
    document.append(generate_third_party())
    document.append(generate_change_log())
    return "".join(document)


def main():
    print("通讯接口规格书生成器")
    print("-" * 40)

    if not CONFIG_COMM.exists():
        print(f"错误: 配置文件不存在: {CONFIG_COMM}")
        return

    document = generate_comm_spec()
    OUTPUT_COMM.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_COMM, 'w', encoding='utf-8') as f:
        f.write(document)

    print(f"生成文档: {OUTPUT_COMM}")
    print("\n完成!")


if __name__ == '__main__':
    main()
