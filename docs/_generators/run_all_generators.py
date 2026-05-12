#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一生成器调度脚本
运行所有文档生成器
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

GENERATORS = {
    "PLC_Arch": {
        "script": "plc_arch_generator.py",
        "desc": "PLC架构文档",
        "output": "02_Arch/茶饮料_PLC架构_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "TagCode": {
        "script": "tag_code_generator.py",
        "desc": "位号编码规则",
        "output": "03_Device/茶饮料_位号编码规则_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "DeviceParam": {
        "script": "device_param_generator.py",
        "desc": "设备参数表",
        "output": "03_Device/茶饮料_设备参数表_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "MonitorPoint": {
        "script": "monitor_point_generator.py",
        "desc": "监控点表",
        "output": "03_Device/茶饮料_监控点表_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "SCADA_Spec": {
        "script": "scada_spec_generator.py",
        "desc": "SCADA系统功能规格说明书",
        "output": "01_Spec/auto/茶饮料_SCADA功能规格_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "HMI_Spec": {
        "script": "hmi_generator.py",
        "desc": "HMI画面规格说明书",
        "output": "01_Spec/auto/茶饮料_HMI画面规格_auto.md",
        "input": "01_Spec/configs/hmi_config.yaml"
    },
    "FB_Spec": {
        "script": "fb_spec_generator.py",
        "desc": "PLC功能块规格说明书",
        "output": "02_Arch/auto/茶饮料_PLC功能块规格_auto.md",
        "input": "01_Spec/configs/fb_spec_config.yaml"
    },
    "Process_Flow": {
        "script": "process_flow_generator.py",
        "desc": "生产线工艺配置",
        "output": "02_Arch/auto/茶饮料_生产线工艺配置_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "Process_Recipe": {
        "script": "process_recipe_generator.py",
        "desc": "工艺配方",
        "output": "04_Process/auto/茶饮料_工艺配方_auto.md",
        "input": "01_Spec/configs/process_recipe_templates.yaml"
    },
    "Index": {
        "script": "index_generator.py",
        "desc": "文档索引清单",
        "output": "00_Index/auto/文档索引清单_auto.md",
        "input": "01_Spec/configs/index_config.yaml"
    },
    "Interlock": {
        "script": "interlock_generator.py",
        "desc": "联锁逻辑说明书",
        "output": "04_Process/auto/茶饮料_联锁逻辑说明书_auto.md",
        "input": "01_Spec/configs/system_config.yaml"
    },
    "CIP_Spec": {
        "script": "cip_spec_generator.py",
        "desc": "CIP清洗程序规格书",
        "output": "04_Process/auto/茶饮料_CIP清洗程序规格书_auto.md",
        "input": "01_Spec/configs/process_recipe_templates.yaml"
    },
    "Comm_Spec": {
        "script": "comm_spec_generator.py",
        "desc": "通讯接口规格书",
        "output": "04_Process/auto/茶饮料_通讯接口规格书_auto.md",
        "input": "01_Spec/configs/comm_templates.yaml"
    },
    "CIP_Recipe": {
        "script": "cip_recipe_generator.py",
        "desc": "CIP清洗配方",
        "output": "05_Product/auto/茶饮料_CIP配方表_auto.md",
        "input": "01_Spec/configs/process_recipe_templates.yaml"
    },
    "Product_Recipe": {
        "script": "product_recipe_generator.py",
        "desc": "产品配方",
        "output": "05_Product/auto/茶饮料_产品配方表_auto.md",
        "input": "01_Spec/configs/product_recipe_templates.yaml"
    },
    "Cabinet_BOM": {
        "script": "engineering_generator.py",
        "desc": "电控柜BOM清单",
        "output": "07_Engineering/auto/茶饮料_电控柜BOM清单_auto.xlsx",
        "input": "01_Spec/configs/cabinet_bom.yaml"
    },
    "Instrument_List": {
        "script": "engineering_generator.py",
        "desc": "仪表清单",
        "output": "07_Engineering/auto/茶饮料_仪表清单_auto.xlsx",
        "input": "01_Spec/configs/instrument_list.yaml"
    },
    "Terminal_Assignments": {
        "script": "engineering_generator.py",
        "desc": "端子定义表",
        "output": "07_Engineering/auto/茶饮料_端子定义表_auto.xlsx",
        "input": "01_Spec/configs/terminal_assignments.yaml"
    },
    "Cable_List": {
        "script": "engineering_generator.py",
        "desc": "电缆清单",
        "output": "07_Engineering/auto/茶饮料_电缆清单_auto.xlsx",
        "input": "01_Spec/configs/cable_list.yaml"
    },
}


def run_generator(script_name, generator_desc):
    script_path = SCRIPT_DIR / script_name
    print(f"  [{script_name}] {generator_desc}...", end=" ")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(SCRIPT_DIR),
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("OK")
            return True, None
        else:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            if error_msg:
                error_msg = error_msg[:300]
            print(f"FAIL")
            if error_msg:
                print(f"    Error: {error_msg}")
            return False, error_msg
    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False, "Script timeout after 120 seconds"
    except Exception as e:
        print(f"ERROR: {e}")
        return False, str(e)


def main():
    print("=" * 60)
    print("SCADA 文档生成器 - 一键生成所有文档")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目录: {SCRIPT_DIR}")
    print("=" * 60)

    success_count = 0
    fail_count = 0
    failed_scripts = []

    for key, gen in GENERATORS.items():
        desc = gen.get('desc', key)
        script = gen.get('script', '')
        success, error = run_generator(script, desc)
        if success:
            success_count += 1
        else:
            fail_count += 1
            failed_scripts.append((script, error))

    print("=" * 60)
    print(f"完成! 成功: {success_count}, 失败: {fail_count}")
    if failed_scripts:
        print("\n失败的脚本:")
        for script, error in failed_scripts:
            print(f"  - {script}")
    print("=" * 60)

    return fail_count == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
