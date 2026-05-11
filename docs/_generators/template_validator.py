"""
SCADA 模板验证器 v1.0
茶饮料生产线 - 验证YAML模板的标准化和引用完整性

使用方法:
    python template_validator.py [--path <template_dir>] [--fix]

参数:
    --path     模板目录 (默认: ../)
    --fix      自动修复可识别的问题

示例:
    python template_validator.py                    # 验证所有模板
    python template_validator.py --fix             # 验证并修复
    python template_validator.py --path ../../     # 验证指定目录
"""

import os
import sys
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

SCRIPT_DIR = Path(__file__).parent
DEFAULT_TEMPLATE_DIR = SCRIPT_DIR.parent


REQUIRED_META_FIELDS = {
    'version',      # 版本格式: v1.0
    'created',       # 创建日期: YYYY-MM-DD
    'updated',       # 更新日期: YYYY-MM-DD
    'author',        # 作者
    'status',        # 状态: draft/active/approved
    'source_docs',   # 源文档列表(复数)
    'project_name',  # 项目名称
}

VALID_STATUSES = ['draft', 'active', 'approved', 'deprecated']

SECTION_CODES = {
    'WT', 'TH', 'EX', 'FL', 'BL', 'HM', 'UH', 'BF',
    'PF', 'CG', 'LI', 'CI', 'LB', 'CA', 'PK', 'CP',
    'Total'  # 总电能表，不属于单一工段
}

SECTION_NAMES = {
    'WT': '水处理', 'TH': '茶叶前处理', 'EX': '萃取', 'FL': '过滤',
    'BL': '调配', 'HM': '均质', 'UH': 'UHT', 'BF': '制瓶',
    'PF': '灌装', 'CG': '旋盖', 'LI': '灯检', 'CI': '喷码',
    'LB': '贴标', 'CA': '装箱', 'PK': '膜包码垛', 'CP': 'CIP清洗'
}


class ValidationResult:
    def __init__(self):
        self.errors: List[Tuple[str, str]] = []
        self.warnings: List[Tuple[str, str]] = []
        self.fixes: List[Tuple[str, str, str]] = []

    def add_error(self, file: str, msg: str):
        self.errors.append((file, msg))

    def add_warning(self, file: str, msg: str):
        self.warnings.append((file, msg))

    def add_fix(self, file: str, old_val: str, new_val: str):
        self.fixes.append((file, old_val, new_val))

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_report(self):
        print("\n" + "=" * 70)
        print("SCADA 模板验证报告")
        print("=" * 70)

        if self.errors:
            print(f"\n[ERROR] 错误 ({len(self.errors)}项):")
            for file, msg in self.errors:
                print(f"  [{file}] {msg}")

        if self.warnings:
            print(f"\n[WARNING] 警告 ({len(self.warnings)}项):")
            for file, msg in self.warnings:
                print(f"  [{file}] {msg}")

        if self.fixes:
            print(f"\n[FIX] 可修复项 ({len(self.fixes)}项):")
            for file, old_val, new_val in self.fixes:
                print(f"  [{file}]")
                print(f"    旧值: {old_val}")
                print(f"    新值: {new_val}")

        if not self.errors and not self.warnings:
            print("\n[OK] 所有检查通过！")
            return True

        return False


def load_yaml(file_path: Path) -> Dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def validate_meta_structure(file_path: Path, data: Dict, result: ValidationResult):
    """验证meta结构的标准化"""
    meta = data.get('meta', {})

    if not meta:
        result.add_error(file_path.name, "缺少 meta 字段")
        return

    missing_fields = REQUIRED_META_FIELDS - set(meta.keys())
    if missing_fields:
        result.add_warning(file_path.name, f"meta缺少字段: {', '.join(missing_fields)}")

    if 'version' in meta:
        version = meta['version']
        if not isinstance(version, str):
            result.add_error(file_path.name, f"version应为字符串, 实际: {type(version).__name__}")
        elif not version.startswith('v'):
            result.add_warning(file_path.name, f"version应带v前缀, 当前: {version}")
        elif not validate_version_format(version):
            result.add_warning(file_path.name, f"version格式不规范: {version} (应为v1.0)")

    if 'status' in meta:
        status = meta['status']
        if status not in VALID_STATUSES:
            result.add_warning(file_path.name, f"status值不规范: {status} (应为: {', '.join(VALID_STATUSES)})")

    if 'source_docs' in meta:
        if not isinstance(meta['source_docs'], list):
            result.add_warning(file_path.name, "source_docs应为列表, 实际使用了source_doc(单数)")

    date_fields = ['created', 'updated']
    for field in date_fields:
        if field in meta:
            if not validate_date_format(meta[field]):
                result.add_warning(file_path.name, f"{field}格式应为YYYY-MM-DD, 当前: {meta[field]}")


def validate_version_format(version: str) -> bool:
    """验证版本格式 v1.0, v2.1.3 等"""
    if not version.startswith('v'):
        return False
    parts = version[1:].split('.')
    return len(parts) >= 2 and all(p.isdigit() for p in parts)


def validate_date_format(date_str: str) -> bool:
    """验证日期格式 YYYY-MM-DD"""
    if not isinstance(date_str, str):
        return False
    parts = date_str.split('-')
    if len(parts) != 3:
        return False
    year, month, day = parts
    return (year.isdigit() and len(year) == 4 and
            month.isdigit() and 1 <= int(month) <= 12 and
            day.isdigit() and 1 <= int(day) <= 31)


def validate_section_references(file_path: Path, data: Dict, result: ValidationResult):
    """验证section引用的完整性"""
    section_refs = find_section_references(data)

    for ref in section_refs:
        if isinstance(ref, str):
            if ref in SECTION_CODES:
                continue
            elif ref in SECTION_NAMES.values():
                code = [k for k, v in SECTION_NAMES.items() if v == ref]
                result.add_warning(file_path.name,
                    f"使用中文名称'{ref}'而非代码'{code[0]}'")
            else:
                result.add_warning(file_path.name, f"未识别的section: {ref}")


def find_section_references(data: Any, path: str = "") -> List:
    """递归查找所有section引用"""
    refs = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key in ['section', 'section_code', 'section_codes', 'affected_section', 'affected_sections']:
                if isinstance(value, str):
                    refs.append(value)
                elif isinstance(value, list):
                    refs.extend(value)
            elif isinstance(value, (dict, list)):
                refs.extend(find_section_references(value, f"{path}.{key}"))

    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                refs.extend(find_section_references(item, f"{path}[{i}]"))

    return refs


def validate_yaml_syntax(file_path: Path, result: ValidationResult):
    """验证YAML语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.add_error(file_path.name, f"YAML语法错误: {str(e)[:100]}")
    except Exception as e:
        result.add_error(file_path.name, f"文件读取错误: {str(e)[:100]}")


def validate_template_file(file_path: Path, result: ValidationResult):
    """验证单个模板文件"""
    validate_yaml_syntax(file_path, result)

    try:
        data = load_yaml(file_path)
        validate_meta_structure(file_path, data, result)
        validate_section_references(file_path, data, result)
    except Exception as e:
        result.add_error(file_path.name, f"验证过程错误: {str(e)[:100]}")


def find_yaml_templates(root_dir: Path) -> List[Path]:
    """查找所有YAML模板文件"""
    yaml_files = []
    search_patterns = ['**/*.yaml', '**/*.yml']

    for pattern in search_patterns:
        yaml_files.extend(root_dir.glob(pattern))

    yaml_files = [f for f in yaml_files if '_generators' not in str(f)]

    return sorted(yaml_files)


def main():
    parser = argparse.ArgumentParser(description='SCADA 模板验证器')
    parser.add_argument('--path', default=str(DEFAULT_TEMPLATE_DIR),
                        help='模板目录路径')
    parser.add_argument('--fix', action='store_true',
                        help='自动修复可识别的问题')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细输出')

    args = parser.parse_args()

    template_dir = Path(args.path)
    if not template_dir.exists():
        print(f"错误: 目录不存在: {template_dir}")
        sys.exit(1)

    print(f"\nSCADA 模板验证器 v1.0")
    print(f"验证目录: {template_dir}")
    print("-" * 50)

    yaml_files = find_yaml_templates(template_dir)
    print(f"找到 {len(yaml_files)} 个YAML模板文件")

    if not yaml_files:
        print("未找到任何YAML文件")
        sys.exit(1)

    result = ValidationResult()

    for yaml_file in yaml_files:
        if args.verbose:
            print(f"验证: {yaml_file.relative_to(template_dir)}")
        validate_template_file(yaml_file, result)

    success = result.print_report()

    print("\n" + "=" * 70)
    print(f"总计: {len(yaml_files)} 个文件, {len(result.errors)} 错误, {len(result.warnings)} 警告")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
