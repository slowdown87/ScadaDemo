#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all_generators.py
茶饮料生产线SCADA系统 - 配置驱动文档生成系统

功能: 运行所有文档生成器，从单一配置源(system_config.yaml)自动生成所有依赖文档

使用方法:
    python run_all_generators.py          # 运行所有生成器
    python run_all_generators.py --list   # 列出所有生成器
    python run_all_generators.py --gen=PLC_Arch  # 运行指定生成器

文档依赖关系:
    system_config.yaml (单一真相源)
        ├──→ PLC_Architecture_auto.md
        ├──→ 位号编码规则_auto.md
        └──→ 设备参数表_auto.md

修改流程:
    1. 编辑 configs/system_config.yaml
    2. 运行 python run_all_generators.py
    3. 检查生成的 *_auto.md 文档
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# 颜色定义
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

# ============================================================================
# 生成器列表
# ============================================================================
GENERATORS = {
    "PLC_Arch": {
        "script": "PLC_Arch_generator.py",
        "desc": "PLC架构文档",
        "output": "02_Arch/PLC_Architecture_auto.md",
        "input": "configs/system_config.yaml"
    },
    "TagCode": {
        "script": "TagCode_generator.py",
        "desc": "位号编码规则",
        "output": "03_Device/位号编码规则_auto.md",
        "input": "configs/system_config.yaml"
    },
    "DeviceParam": {
        "script": "DeviceParam_generator.py",
        "desc": "设备参数表",
        "output": "03_Device/设备参数表_auto.md",
        "input": "configs/system_config.yaml"
    },
}

# ============================================================================
# 主函数
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description='配置驱动文档生成系统')
    parser.add_argument('--list', action='store_true', help='列出所有生成器')
    parser.add_argument('--gen', type=str, help='运行指定生成器')
    args = parser.parse_args()

    script_dir = Path(__file__).parent

    # 列出所有生成器
    if args.list:
        print("\n" + "=" * 70)
        print("配置驱动文档生成系统 - 可用生成器")
        print("=" * 70)
        print(f"{'生成器':<15} {'说明':<20} {'输入':<30}")
        print("-" * 70)
        for key, gen in GENERATORS.items():
            print(f"{key:<15} {gen['desc']:<20} {gen['input']:<30}")
        print("=" * 70)
        return

    # 运行指定或所有生成器
    if args.gen:
        if args.gen not in GENERATORS:
            log_error(f"未知的生成器: {args.gen}")
            log_info(f"可用生成器: {', '.join(GENERATORS.keys())}")
            sys.exit(1)
        to_run = {args.gen: GENERATORS[args.gen]}
    else:
        to_run = GENERATORS

    print("\n" + "=" * 70)
    print("配置驱动文档生成系统")
    print("=" * 70)
    log_info(f"运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 70)

    success_count = 0
    fail_count = 0

    for key, gen in to_run.items():
        script_path = script_dir / gen['script']
        if not script_path.exists():
            log_warning(f"生成器脚本不存在: {script_path}")
            continue

        print(f"\n[{key}] {gen['desc']}")
        log_info(f"运行: {script_path}")

        # 执行生成器
        result = os.system(f'python "{script_path}"')

        if result == 0:
            log_success(f"生成成功: {gen['output']}")
            success_count += 1
        else:
            log_error(f"生成失败: {gen['output']} (exit code: {result})")
            fail_count += 1

    print("\n" + "=" * 70)
    print("生成结果汇总")
    print("=" * 70)
    log_success(f"成功: {success_count}")
    if fail_count > 0:
        log_error(f"失败: {fail_count}")
    else:
        log_info(f"失败: {fail_count}")
    print("=" * 70)

    if fail_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
