"""
SCADA 工程文档生成器 (配置驱动版)
茶饮料生产线 - 基于YAML配置生成Excel

使用方法:
    python engineering_generator.py --config <config_file> [--output <output_dir>]
    或通过 run_all_generators.py 统一调度

参数:
    --config      配置文件: cabinet_bom, instrument_list, terminal, cable
    --output      输出目录 (默认: 07_Engineering/auto/)

示例:
    python engineering_generator.py --config cabinet_bom      # 生成电控柜BOM
    python engineering_generator.py --config instrument_list  # 生成仪表清单
    python engineering_generator.py --config terminal         # 生成端子定义表
    python engineering_generator.py --config cable            # 生成电缆清单
    python engineering_generator.py --config all              # 生成全部Excel
"""

import os
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from jinja2 import Environment, FileSystemLoader, Template

SCRIPT_DIR = Path(__file__).parent
DOCS_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = DOCS_DIR / '07_Engineering' / 'auto'
DEFAULT_CONFIGS_DIR = DOCS_DIR / '01_Spec' / 'configs'


def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_data_dir(filename):
    data_dirs = {
        'system_config.yaml': DOCS_DIR / '01_Spec' / 'configs',
        'comm_templates.yaml': DOCS_DIR / '01_Spec' / 'configs',
        'interlock_templates.yaml': DOCS_DIR / '01_Spec' / 'configs',
        'cip_templates.yaml': DOCS_DIR / '01_Spec' / 'configs',
    }
    return data_dirs.get(filename, DOCS_DIR / '_templates')


def load_data_sources(config):
    sources = {}
    loaded_files = {}
    for key, source_info in config.get('data_sources', {}).items():
        source_file = source_info.get('source', '')
        if source_file and source_file not in loaded_files:
            if source_file == 'devices':
                loaded_files['devices'] = load_yaml(get_data_dir('system_config.yaml') / 'system_config.yaml')
            elif source_file == 'comm_templates':
                loaded_files['comm_templates'] = load_yaml(get_data_dir('comm_templates.yaml') / 'comm_templates.yaml')
            elif source_file == 'interlock_templates':
                loaded_files['interlock_templates'] = load_yaml(get_data_dir('interlock_templates.yaml') / 'interlock_templates.yaml')
            elif source_file == 'cip_templates':
                loaded_files['cip_templates'] = load_yaml(get_data_dir('cip_templates.yaml') / 'cip_templates.yaml')
        if source_file in loaded_files:
            sources[source_file] = loaded_files[source_file]
    return sources


def get_nested(data, path, default=None):
    keys = path.replace('[', '.').replace(']', '.').replace('*', '').split('.')
    keys = [k for k in keys if k]
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        elif isinstance(result, list):
            try:
                idx = int(key)
                result = result[idx] if idx < len(result) else default
            except ValueError:
                result = default
        else:
            return default
    return result if result else default


def flatten_devices_by_section(devices_dict):
    """Convert devices dict {section: [devices]} to flat list with section field."""
    result = []
    for section, devices in devices_dict.items():
        if isinstance(devices, list):
            for device in devices:
                if isinstance(device, dict):
                    device = device.copy()
                    device['section'] = section
                    result.append(device)
    return result


def filter_devices_by_type(devices_list, device_type):
    """Filter devices by type field (pump, motor, tank, etc.)."""
    return [d for d in devices_list if isinstance(d, dict) and d.get('type') == device_type]


def transform_data(template_str, context):
    try:
        template = Template(template_str)
        return template.render(**context)
    except Exception as e:
        print(f"  警告: 模板转换失败 '{template_str}': {e}")
        return template_str


def generate_cabinet_bom(config, data_sources):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    meta = config.get('meta', {})
    template_config = config.get('template', {})
    sheets_config = template_config.get('sheets', [])

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    sections_data = get_nested(data_sources, 'comm_templates.plc_config', [])
    devices_raw = get_nested(data_sources, 'devices.devices', [])
    if isinstance(devices_raw, dict):
        all_devices = flatten_devices_by_section(devices_raw)
    else:
        all_devices = devices_raw if isinstance(devices_raw, list) else []
    pumps_data = filter_devices_by_type(all_devices, 'pump')
    motors_data = filter_devices_by_type(all_devices, 'motor')

    for sheet_config in sheets_config:
        ws = wb.create_sheet(title=sheet_config['name'])
        headers = sheet_config.get('header', [])
        groups = sheet_config.get('groups', [])

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        row = 2

        if 'PLC柜元器件清单' in sheet_config['name']:
            seq = 1

            for group in groups:
                group_name = group.get('name', '')
                for item in group.get('items', []):
                    item_type = item.get('type', '')
                    item_tag = item.get('tag', '')

                    if item_type == 'plc_cpu':
                        for plc in sections_data:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=plc.get('id', '')).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value=plc.get('name', '')).border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=1).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'plc_io_di':
                        for plc in sections_data:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=plc.get('id', '')).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='SM 1221 DI 16×24VDC').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=3).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'plc_io_do':
                        for plc in sections_data:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=plc.get('id', '')).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='SM 1222 DO 16×24VDC/0.5A').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=2).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'plc_io_ai':
                        for plc in sections_data:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=plc.get('id', '')).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='SM 1231 AI 8×U/I/RTD').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=2).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'plc_io_ao':
                        for plc in sections_data:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=plc.get('id', '')).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='SM 1232 AO 4×U/I').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=1).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'plc_comm':
                        for plc in sections_data:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=plc.get('id', '')).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='CM 1542-1 PROFINET').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=1).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'plc_power':
                        for plc in sections_data:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=plc.get('id', '')).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='PS 25W 24VDC').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=1).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'inverter':
                        for pump in pumps_data:
                            if pump.get('is_inverter'):
                                power = pump.get('power_kw', '?')
                                ws.cell(row=row, column=1, value=seq).border = border
                                ws.cell(row=row, column=2, value=pump.get('id', '')).border = border
                                ws.cell(row=row, column=3, value=pump.get('name', '')).border = border
                                ws.cell(row=row, column=4, value=f'G120C {power}kW').border = border
                                ws.cell(row=row, column=5, value='SIEMENS').border = border
                                ws.cell(row=row, column=6, value=1).border = border
                                ws.cell(row=row, column=7, value='台').border = border
                                row += 1
                                seq += 1

                    elif item_type == 'contactor':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=f'{section}-{item_tag}').border = border
                            ws.cell(row=row, column=4, value='3RT1015-1A 25A').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=10).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'relay_thermal':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=f'{section}-{item_tag}').border = border
                            ws.cell(row=row, column=4, value='3RU1015 热继电器').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=5).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'circuit_breaker':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=f'{section}-{item_tag}').border = border
                            ws.cell(row=row, column=4, value='5SY 断路器').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=8).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'fuse':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=f'{section}-{item_tag}').border = border
                            ws.cell(row=row, column=4, value='5×20mm 10A').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=15).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'relay':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=f'{section}-{item_tag}').border = border
                            ws.cell(row=row, column=4, value='MY2N 24VDC').border = border
                            ws.cell(row=row, column=5, value='OMRON').border = border
                            ws.cell(row=row, column=6, value=15).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'terminal_block':
                        ws.cell(row=row, column=1, value=seq).border = border
                        ws.cell(row=row, column=2, value='通用').border = border
                        ws.cell(row=row, column=3, value=item_tag).border = border
                        ws.cell(row=row, column=4, value='UK 2.5 端子排').border = border
                        ws.cell(row=row, column=5, value='WAGO').border = border
                        ws.cell(row=row, column=6, value=500).border = border
                        ws.cell(row=row, column=7, value='个').border = border
                        row += 1
                        seq += 1

                    elif item_type == 'switch_power':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='SITOP 24VDC 10A').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=2).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'indicator_light':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=f'{section}-{item_tag}').border = border
                            ws.cell(row=row, column=4, value='AD16 22mm LED').border = border
                            ws.cell(row=row, column=5, value='国产').border = border
                            ws.cell(row=row, column=6, value=10).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'push_button':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=f'{section}-{item_tag}').border = border
                            ws.cell(row=row, column=4, value='LA38 22mm 绿/红').border = border
                            ws.cell(row=row, column=5, value='SIEMENS').border = border
                            ws.cell(row=row, column=6, value=5).border = border
                            ws.cell(row=row, column=7, value='个').border = border
                            row += 1
                            seq += 1

                    elif item_type == 'cabinet_fan':
                        for section in ['WT', 'TH', 'EX', 'BL', 'UH', 'PF', 'PK']:
                            ws.cell(row=row, column=1, value=seq).border = border
                            ws.cell(row=row, column=2, value=section).border = border
                            ws.cell(row=row, column=3, value=item_tag).border = border
                            ws.cell(row=row, column=4, value='ebm-papst 220VAC 120mm').border = border
                            ws.cell(row=row, column=5, value='ebm-papst').border = border
                            ws.cell(row=row, column=6, value=1).border = border
                            ws.cell(row=row, column=7, value='台').border = border
                            row += 1
                            seq += 1

            for col in range(1, len(headers) + 1):
                ws.column_dimensions[chr(64 + col)].width = 18

        elif '按PLC统计' in sheet_config['name']:
            for plc in sections_data:
                section_names = '/'.join(plc.get('section_names', []))
                ws.cell(row=row, column=1, value=plc.get('id', '')).border = border
                ws.cell(row=row, column=2, value=section_names).border = border
                ws.cell(row=row, column=3, value='CPU 1515-2 PN').border = border
                ws.cell(row=row, column=4, value=3).border = border
                ws.cell(row=row, column=5, value=2).border = border
                ws.cell(row=row, column=6, value=2).border = border
                ws.cell(row=row, column=7, value=1).border = border
                row += 1

            for col in range(1, 10):
                ws.column_dimensions[chr(64 + col)].width = 15

    return wb


def generate_instrument_list(config, data_sources):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    devices_raw = get_nested(data_sources, 'devices.devices', [])
    if isinstance(devices_raw, dict):
        devices_data = flatten_devices_by_section(devices_raw)
    else:
        devices_data = devices_raw if isinstance(devices_raw, list) else []

    template_config = config.get('template', {})
    sheets_config = template_config.get('sheets', [])

    section_names = {
        'WT': '水处理', 'TH': '茶叶前处理', 'EX': '萃取', 'FL': '过滤',
        'BL': '调配', 'HM': '均质', 'UH': 'UHT', 'BF': '制瓶',
        'PF': '灌装', 'CG': '旋盖', 'LI': '灯检', 'CI': '喷码',
        'LB': '贴标', 'CA': '装箱', 'PK': '膜包', 'CP': 'CIP'
    }

    for sheet_config in sheets_config:
        ws = wb.create_sheet(title=sheet_config['name'])
        headers = sheet_config.get('header', [])

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        row = 2

        if '仪表清单' in sheet_config['name']:
            for device in devices_data:
                for sensor in device.get('sensors', []):
                    code = sensor.get('code', '')
                    if code.startswith(('TT', 'PT', 'LT', 'FT', 'AT', 'BT', 'CtT')):
                        tag = f"{device.get('id', '')}-{code}"
                        name = f"{device.get('name', '')}{sensor.get('name', '')}"
                        section = device.get('section', '')
                        location = section_names.get(section, section)
                        sensor_range = sensor.get('range', [0, 100])
                        range_str = f"{sensor_range[0]}-{sensor_range[1]}"
                        unit = sensor.get('unit', '')
                        sensor_type = sensor.get('type', '')

                        if code.startswith('TT'):
                            brand, model = 'E+H', 'TR45'
                        elif code.startswith('PT'):
                            brand, model = 'E+H', 'PT51'
                        elif code.startswith('FT'):
                            brand, model = 'E+H', '10P'
                        elif code.startswith('LT'):
                            brand, model = 'E+H', 'FTL51'
                        else:
                            brand, model = 'E+H', 'CTE'

                        ws.cell(row=row, column=1, value=tag).border = border
                        ws.cell(row=row, column=2, value=name).border = border
                        ws.cell(row=row, column=3, value=f'{location}工段').border = border
                        ws.cell(row=row, column=4, value=sensor_type).border = border
                        ws.cell(row=row, column=5, value=range_str).border = border
                        ws.cell(row=row, column=6, value=unit).border = border
                        ws.cell(row=row, column=7, value=brand).border = border
                        ws.cell(row=row, column=8, value=model).border = border
                        ws.cell(row=row, column=9, value=1).border = border
                        ws.cell(row=row, column=10, value='±0.5%').border = border
                        ws.cell(row=row, column=11, value='4-20mA').border = border
                        ws.cell(row=row, column=12, value='24VDC').border = border
                        ws.cell(row=row, column=13, value='').border = border
                        row += 1

            for col in range(1, 14):
                ws.column_dimensions[chr(64 + col) if col < 27 else 'A' + chr(64 + col - 26)].width = 15

    return wb


def generate_terminal_assignments(config, data_sources):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    plc_config = get_nested(data_sources, 'comm_templates.plc_config', [])
    devices_raw = get_nested(data_sources, 'devices.devices', [])
    if isinstance(devices_raw, dict):
        devices_data = flatten_devices_by_section(devices_raw)
    else:
        devices_data = devices_raw if isinstance(devices_raw, list) else []

    section_names = {
        'WT': '水处理', 'TH': '茶叶前处理', 'EX': '萃取', 'FL': '过滤',
        'BL': '调配', 'HM': '均质', 'UH': 'UHT', 'BF': '制瓶',
        'PF': '灌装', 'CG': '旋盖', 'LI': '灯检', 'CI': '喷码',
        'LB': '贴标', 'CA': '装箱', 'PK': '膜包', 'CP': 'CIP'
    }

    template_config = config.get('template', {})
    sheets_config = template_config.get('sheets', [])

    for sheet_config in sheets_config:
        ws = wb.create_sheet(title=sheet_config['name'])
        headers = sheet_config.get('header', [])

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        row = 2

        if '端子定义总表' in sheet_config['name']:
            di_channels = ['I0.0', 'I0.1', 'I0.2', 'I0.3', 'I0.4', 'I0.5', 'I0.6', 'I0.7',
                          'I1.0', 'I1.1', 'I1.2', 'I1.3', 'I1.4', 'I1.5', 'I1.6', 'I1.7']
            do_channels = ['Q0.0', 'Q0.1', 'Q0.2', 'Q0.3', 'Q0.4', 'Q0.5', 'Q0.6', 'Q0.7',
                          'Q1.0', 'Q1.1', 'Q1.2', 'Q1.3', 'Q1.4', 'Q1.5', 'Q1.6', 'Q1.7']
            ai_channels = ['IW0', 'IW2', 'IW4', 'IW6', 'IW8', 'IW10', 'IW12', 'IW14']
            ao_channels = ['QW0', 'QW4', 'QW8', 'QW12']

            di_idx, do_idx, ai_idx, ao_idx = 0, 0, 0, 0

            for device in devices_data:
                section = device.get('section', '')
                location = section_names.get(section, section)

                for sensor in device.get('sensors', []):
                    code = sensor.get('code', '')
                    name = f"{device.get('name', '')}{sensor.get('name', '')}"
                    tag = f"{device.get('id', '')}-{code}"

                    if code.startswith(('DT',)):
                        ch = di_channels[di_idx % 16] if di_idx < 256 else f'I{di_idx//16}.{di_idx%16}'
                        ws.cell(row=row, column=1, value=section).border = border
                        ws.cell(row=row, column=2, value='PLC柜').border = border
                        ws.cell(row=row, column=3, value=ch).border = border
                        ws.cell(row=row, column=4, value='DI').border = border
                        ws.cell(row=row, column=5, value=tag).border = border
                        ws.cell(row=row, column=6, value=name).border = border
                        ws.cell(row=row, column=7, value=f'{code}状态').border = border
                        ws.cell(row=row, column=8, value='1M').border = border
                        ws.cell(row=row, column=9, value='').border = border
                        di_idx += 1
                        row += 1

                    elif code.startswith(('TT', 'PT', 'LT', 'FT')):
                        if ai_idx < len(ai_channels):
                            ch = ai_channels[ai_idx % 8]
                            ws.cell(row=row, column=1, value=section).border = border
                            ws.cell(row=row, column=2, value='PLC柜').border = border
                            ws.cell(row=row, column=3, value=ch).border = border
                            ws.cell(row=row, column=4, value='AI').border = border
                            ws.cell(row=row, column=5, value=tag).border = border
                            ws.cell(row=row, column=6, value=name).border = border
                            ws.cell(row=row, column=7, value=f'{code}信号').border = border
                            ws.cell(row=row, column=8, value='4-20mA').border = border
                            ws.cell(row=row, column=9, value='').border = border
                            ai_idx += 1
                            row += 1

            for col in range(1, 10):
                ws.column_dimensions[chr(64 + col)].width = 16

    return wb


def generate_cable_list(config, data_sources):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    plc_config = get_nested(data_sources, 'comm_templates.plc_config', [])
    devices_raw = get_nested(data_sources, 'devices.devices', [])
    if isinstance(devices_raw, dict):
        all_devices = flatten_devices_by_section(devices_raw)
    else:
        all_devices = devices_raw if isinstance(devices_raw, list) else []
    pumps_data = filter_devices_by_type(all_devices, 'pump')
    motors_data = filter_devices_by_type(all_devices, 'motor')

    template_config = config.get('template', {})
    sheets_config = template_config.get('sheets', [])

    section_names = {
        'WT': '水处理', 'TH': '茶叶前处理', 'EX': '萃取', 'FL': '过滤',
        'BL': '调配', 'HM': '均质', 'UH': 'UHT', 'BF': '制瓶',
        'PF': '灌装', 'CG': '旋盖', 'LI': '灯检', 'CI': '喷码',
        'LB': '贴标', 'CA': '装箱', 'PK': '膜包', 'CP': 'CIP'
    }

    for sheet_config in sheets_config:
        ws = wb.create_sheet(title=sheet_config['name'])
        headers = sheet_config.get('header', [])

        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        row = 2
        seq = 1

        if '电缆清单总表' in sheet_config['name']:
            for pump in pumps_data:
                section = pump.get('section', '')
                location = section_names.get(section, section)
                power = pump.get('power_kw', '?')
                cable_spec = 'YJV-0.6/1kV 4×2.5' if power < 7.5 else 'YJV-0.6/1kV 4×4'
                length = 30 if power < 7.5 else 40 if power < 15 else 50

                ws.cell(row=row, column=1, value=seq).border = border
                ws.cell(row=row, column=2, value=f'C-P{seq:03d}').border = border
                ws.cell(row=row, column=3, value=pump.get('name', '')).border = border
                ws.cell(row=row, column=4, value=f'{location}MCC柜').border = border
                ws.cell(row=row, column=5, value=f'{section}-PLC柜').border = border
                ws.cell(row=row, column=6, value=pump.get('name', '')).border = border
                ws.cell(row=row, column=7, value='动力电缆').border = border
                ws.cell(row=row, column=8, value=cable_spec).border = border
                ws.cell(row=row, column=9, value=length).border = border
                ws.cell(row=row, column=10, value=1).border = border
                ws.cell(row=row, column=11, value='桥架').border = border
                ws.cell(row=row, column=12, value='').border = border
                row += 1
                seq += 1

            for motor in motors_data:
                section = motor.get('section', '')
                location = section_names.get(section, section)
                power = motor.get('power_kw', '?')
                cable_spec = 'YJV-0.6/1kV 4×2.5' if power < 7.5 else 'YJV-0.6/1kV 4×4'
                length = 30 if power < 7.5 else 40 if power < 15 else 50

                ws.cell(row=row, column=1, value=seq).border = border
                ws.cell(row=row, column=2, value=f'C-M{seq:03d}').border = border
                ws.cell(row=row, column=3, value=motor.get('name', '')).border = border
                ws.cell(row=row, column=4, value=f'{location}MCC柜').border = border
                ws.cell(row=row, column=5, value=f'{section}-PLC柜').border = border
                ws.cell(row=row, column=6, value=motor.get('name', '')).border = border
                ws.cell(row=row, column=7, value='动力电缆').border = border
                ws.cell(row=row, column=8, value=cable_spec).border = border
                ws.cell(row=row, column=9, value=length).border = border
                ws.cell(row=row, column=10, value=1).border = border
                ws.cell(row=row, column=11, value='桥架').border = border
                ws.cell(row=row, column=12, value='').border = border
                row += 1
                seq += 1

            for col in range(1, 13):
                ws.column_dimensions[chr(64 + col) if col < 27 else 'A' + chr(64 + col - 26)].width = 14

    return wb


GENERATORS = {
    'cabinet_bom': generate_cabinet_bom,
    'instrument_list': generate_instrument_list,
    'terminal_assignments': generate_terminal_assignments,
    'cable_list': generate_cable_list,
}


def main():
    parser = argparse.ArgumentParser(description='SCADA 工程文档生成器 (配置驱动版)')
    parser.add_argument('--config', choices=['cabinet_bom', 'instrument_list', 'terminal_assignments', 'cable_list', 'all'],
                        default='all', help='配置文件')
    parser.add_argument('--configs-dir', default=str(DEFAULT_CONFIGS_DIR), help='配置文件目录')
    parser.add_argument('--output', default=str(OUTPUT_DIR), help='输出目录')

    args = parser.parse_args()

    configs_dir = Path(args.configs_dir)
    os.makedirs(args.output, exist_ok=True)

    print(f"SCADA 工程文档生成器 (配置驱动版)")
    print(f"配置文件目录: {configs_dir}")
    print(f"输出目录: {args.output}")
    print("-" * 50)

    configs = {
        'cabinet_bom': configs_dir / 'cabinet_bom.yaml',
        'instrument_list': configs_dir / 'instrument_list.yaml',
        'terminal_assignments': configs_dir / 'terminal_assignments.yaml',
        'cable_list': configs_dir / 'cable_list.yaml',
    }

    target_configs = configs.values() if args.config == 'all' else [configs[args.config]]

    for config_path in target_configs:
        if not config_path.exists():
            print(f"  配置文件不存在: {config_path}")
            continue

        config_name = config_path.stem
        print(f"正在生成: {config_name}...")

        config = load_yaml(config_path)
        data_sources = load_data_sources(config)

        generator_func = GENERATORS.get(config_name)
        if generator_func:
            wb = generator_func(config, data_sources)

            output_path = Path(config.get('output', {}).get('path', ''))
            if output_path and not output_path.is_absolute():
                output_path = Path(args.output) / output_path.name

            if not output_path or str(output_path) == '.':
                output_path = Path(args.output) / f"{config_name}_auto.xlsx"

            output_path.parent.mkdir(parents=True, exist_ok=True)
            wb.save(output_path)
            print(f"  完成: {output_path}")

    print("\n所有Excel文档生成完成!")


if __name__ == '__main__':
    main()
