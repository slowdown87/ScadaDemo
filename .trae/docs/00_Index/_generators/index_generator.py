"""
文档索引清单自动生成器 (配置驱动版)

功能：
- 读取 index_config.yaml 配置文件
- 自动遍历docs目录结构
- 读取各文档头部的版本信息
- 根据配置生成完整的文档索引清单

使用方法:
    python index_generator.py
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent.resolve()
GENERATORS_DIR = SCRIPT_DIR
DOCS_DIR = SCRIPT_DIR.parent
CONFIG_FILE = GENERATORS_DIR.parent / "configs" / "index_config.yaml"
OUTPUT_FILE = SCRIPT_DIR.parent / "文档索引清单.md"


def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_version_from_markdown(file_path):
    """从Markdown文件头部提取版本信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(500)
            version_match = re.search(r'文档版本[:：]\s*[vV]?(\d+\.\d+)', content)
            date_match = re.search(r'更新日期[:：]\s*(\d{4}-\d{2}-\d{2})', content)
            version = version_match.group(1) if version_match else "-"
            date = date_match.group(1) if date_match else "-"
            return version, date
    except Exception:
        return "-", "-"


def extract_version_from_yaml(file_path):
    """从YAML文件提取版本信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if data and 'meta' in data:
                meta = data['meta']
                version = meta.get('version', '-')
                updated = meta.get('updated', meta.get('update', '-'))
                return version, updated
            return "-", "-"
    except Exception:
        return "-", "-"


def scan_directory_structure(base_path, config):
    """扫描目录结构，返回按目录分组的文件列表"""
    categories = config.get('categories', {})
    file_descriptions = config.get('file_descriptions', {})

    structure = defaultdict(lambda: {'root': [], 'configs': []})

    for root, dirs, files in os.walk(base_path):
        if '_generators' in root:
            continue

        root_path = Path(root)
        rel_path = root_path.relative_to(base_path)
        parts = str(rel_path).split(os.sep)

        if len(parts) >= 2 and parts[0] == 'docs':
            category = parts[1]
        elif len(parts) >= 1 and parts[0]:
            category = parts[0]
        else:
            category = ''

        for file in files:
            if not (file.endswith('.md') or file.endswith('.yaml') or file.endswith('.yml')):
                continue

            file_path = root_path / file

            if file.endswith('.md'):
                version, date = extract_version_from_markdown(file_path)
            else:
                version, date = extract_version_from_yaml(file_path)

            desc = file_descriptions.get(file, '')
            marker = " ← 自动生成" if "_auto" in file else ""

            file_info = {
                'name': file,
                'path': file_path,
                'version': version,
                'date': date,
                'desc': desc,
                'marker': marker
            }

            if 'configs' in parts:
                structure[category]['configs'].append(file_info)
            else:
                structure[category]['root'].append(file_info)

    return structure


def generate_header(config):
    """生成文档头部"""
    now = datetime.now().strftime("%Y-%m-%d")
    meta = config.get('meta', {})

    lines = []
    lines.append("# 文档索引清单\n")
    lines.append(f"> 文档版本: v{meta.get('version', '1.0')}")
    lines.append(f"> 创建日期: {meta.get('created', '2026-04-29')}")
    lines.append(f"> 更新日期: {now}")
    lines.append(f"> 项目名称: {meta.get('project_name', '茶饮料生产线文档体系')}")
    lines.append(f"> **自动生成**: 本文档由 index_generator.py 自动生成\n")
    lines.append("***\n")

    return "".join(lines)


def generate_directory_tree(structure, config):
    """生成目录树"""
    categories_config = config.get('categories', {})
    root_files_config = config.get('root_files', [])

    lines = []
    lines.append("## 📁 文档目录结构\n")
    lines.append("```")
    lines.append("docs/")
    lines.append("│")

    lines.append("├── 00_Index/                          ← 文档索引")
    lines.append("│   ├── 文档索引清单.md              ← 本文档")
    lines.append("│   ├── _generators/")
    lines.append("│   │   └── index_generator.py       ← 生成器脚本")
    lines.append("│   └── configs/")
    lines.append("│       └── index_config.yaml       ← 配置文件")
    lines.append("│")

    for rf in root_files_config:
        lines.append(f"├── {rf['name']}          ← {rf['desc']}")
    lines.append("│")

    sorted_cats = sorted(
        categories_config.items(),
        key=lambda x: x[1].get('priority', 99)
    )

    for cat_id, cat_info in sorted_cats:
        cat_data = structure.get(cat_id, {'root': [], 'configs': []})
        root_files = sorted(cat_data.get('root', []), key=lambda x: x['name'])
        config_files = sorted(cat_data.get('configs', []), key=lambda x: x['name'])

        if not root_files and not config_files:
            continue

        lines.append(f"├── {cat_id}/                          ← {cat_info['name']}")

        for i, f in enumerate(root_files):
            is_last = (i == len(root_files) - 1) and not config_files
            prefix = "└──" if is_last else "├──"
            lines.append(f"│   {prefix} {f['name']}{f['marker']}")

        if config_files:
            lines.append("│   └── configs/")
            for i, f in enumerate(config_files):
                is_last = (i == len(config_files) - 1)
                prefix = "└──" if is_last else "├──"
                lines.append(f"│       {prefix} {f['name']}")

    lines.append("```\n")
    return "\n".join(lines)


def generate_category_table(config):
    """生成文档分类说明表格"""
    categories = config.get('categories', {})

    lines = []
    lines.append("## 📋 文档分类说明\n")
    lines.append("| 目录 | 文档类型 | 说明 | 编辑方式 |")
    lines.append("| ---- | ---- | ------------------- | ------------ |")

    sorted_cats = sorted(categories.items(), key=lambda x: x[1].get('priority', 99))
    for cat_id, cat_info in sorted_cats:
        lines.append(f"| {cat_id} | {cat_info['name']} | {cat_info['desc']} | {cat_info['edit_mode']} |")

    lines.append("\n")
    return "\n".join(lines)


def generate_dependency_matrix(config):
    """生成文档依赖关系矩阵"""
    dependencies = config.get('dependencies', [])

    lines = []
    lines.append("## 📊 文档依赖关系矩阵\n")
    lines.append("| 文档 | 依赖文档 | 说明 |")
    lines.append("| ---- | -------- | ---- |")

    for dep in dependencies:
        doc_name = dep['doc']
        deps_list = dep.get('dependencies', [])

        for i, d in enumerate(deps_list):
            if i == 0:
                lines.append(f"| **{doc_name}** | {d['name']} | {d['desc']} |")
            else:
                lines.append(f"| <br /> | {d['name']} | {d['desc']} |")

    lines.append("\n")
    return "\n".join(lines)


def generate_generator_table(config):
    """生成生成器与输出文件对照表"""
    generators = config.get('generators', [])

    lines = []
    lines.append("## 🔗 生成器与输出文件对照表\n")
    lines.append("| 生成器 | 输入模板 | 输出文档 | 用途 |")
    lines.append("| ------ | -------- | -------- | ---- |")

    for g in generators:
        inputs_str = ", ".join(g.get('inputs', []))
        outputs = g.get('outputs', [])
        if isinstance(outputs, list):
            outputs_str = ", ".join(outputs)
        else:
            outputs_str = str(outputs)

        lines.append(f"| {g['generator']} | {inputs_str} | {outputs_str} | {g['desc']} |")

    lines.append("\n")
    return "\n".join(lines)


def generate_maintenance_rules(config):
    """生成维护规则"""
    rules = config.get('maintenance_rules', {})

    lines = []
    lines.append("## ⚙️ 维护规则\n")

    if 'template_modification' in rules:
        tm = rules['template_modification']
        lines.append(f"### 1. {tm['title']}\n")
        lines.append("```")
        for step in tm.get('steps', []):
            lines.append(f"{step}")
        lines.append("```\n")

    if 'section_control' in rules:
        sc = rules['section_control']
        lines.append(f"### 2. {sc['title']}\n")
        for content in sc.get('content', []):
            lines.append(f"{content}\n")

    if 'version_rules' in rules:
        vr = rules['version_rules']
        lines.append(f"### 3. {vr['title']}\n")
        lines.append("| 文档类型 | 更新时机 | 版本号规则 |")
        lines.append("| ---- | ------ | ----------- |")
        for rule in vr.get('rules', []):
            lines.append(f"| {rule['doc_type']} | {rule['trigger']} | {rule['rule']} |")
        lines.append("\n")

    return "\n".join(lines)


def generate_version_table(structure, config):
    """生成文档版本管理表格"""
    lines = []
    lines.append("## 📝 文档版本管理\n")
    lines.append("| 文档 | 当前版本 | 最后更新 |")
    lines.append("| ---- | ---- | ---------- |")

    all_files = []
    for cat, data in structure.items():
        for f in data.get('root', []) + data.get('configs', []):
            all_files.append(f)

    all_files.sort(key=lambda x: x['name'])

    for f in all_files:
        lines.append(f"| {f['name']} | v{f['version']} | {f['date']} |")

    lines.append("\n")
    return "\n".join(lines)


def generate_change_log(config):
    """生成变更记录"""
    version_history = config.get('version_history', [])
    now = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append("---\n")
    lines.append("**文档状态**: 自动生成\n")
    lines.append(f"**生成时间**: {now}\n")
    lines.append("**版本历史**:\n")

    for v in version_history:
        lines.append(f"- v{v['version']} ({v['date']}): {v['desc']}")

    return "\n".join(lines)


def generate_full_index():
    """生成完整的索引文档"""
    config = load_config()
    structure = scan_directory_structure(DOCS_DIR, config)

    document = []
    document.append(generate_header(config))
    document.append(generate_directory_tree(structure, config))
    document.append(generate_category_table(config))
    document.append(generate_dependency_matrix(config))
    document.append(generate_maintenance_rules(config))
    document.append(generate_generator_table(config))
    document.append(generate_version_table(structure, config))
    document.append(generate_change_log(config))

    return "".join(document)


def main():
    print("文档索引清单生成器 (配置驱动版)")
    print("-" * 40)
    print(f"配置文件: {CONFIG_FILE}")
    print(f"输出文件: {OUTPUT_FILE}")
    print("-" * 40)

    document = generate_full_index()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(document)

    print("\n完成!")


if __name__ == '__main__':
    main()
