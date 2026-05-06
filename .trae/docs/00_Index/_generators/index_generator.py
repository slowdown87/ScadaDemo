"""
文档索引清单自动生成器 (配置驱动版 v3.0)

功能：
- 读取 index_config.yaml 配置文件
- 自动遍历docs目录结构
- 读取各文档头部的版本信息
- 根据配置生成完整的文档索引清单
- 支持 auto/manual 子目录分类

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
    """扫描目录结构，返回按目录和子目录分组的文件列表"""
    categories_config = config.get('categories', {})
    file_descriptions = config.get('file_descriptions', {})

    structure = defaultdict(lambda: {'auto': [], 'manual': [], 'root': [], 'configs': []})

    for root, dirs, files in os.walk(base_path):
        if '_generators' in root or 'configs' in root.split(os.sep)[-1]:
            if 'configs' not in root.split(os.sep)[-1]:
                continue

        root_path = Path(root)
        rel_path = root_path.relative_to(base_path)
        parts = str(rel_path).split(os.sep)

        if len(parts) >= 2 and parts[0] in ['00_Index', '01_Spec', '02_Arch', '03_Device', '04_Process', '05_Product', '06_OM', '07_Engineering']:
            category = parts[0]
        elif len(parts) >= 1 and parts[0]:
            category = parts[0]
        else:
            category = ''

        last_dir = parts[-1] if len(parts) >= 1 else ''

        for file in files:
            if not (file.endswith('.md') or file.endswith('.yaml') or file.endswith('.yml') or file.endswith('.xlsx')):
                continue

            file_path = root_path / file

            if file.endswith('.md'):
                version, date = extract_version_from_markdown(file_path)
            else:
                version, date = extract_version_from_yaml(file_path)

            desc = file_descriptions.get(file, '')
            is_auto = "_auto" in file

            file_info = {
                'name': file,
                'path': file_path,
                'relative_path': str(rel_path / file),
                'version': version,
                'date': date,
                'desc': desc,
                'is_auto': is_auto
            }

            if last_dir == 'auto':
                structure[category]['auto'].append(file_info)
            elif last_dir == 'manual':
                structure[category]['manual'].append(file_info)
            elif last_dir == 'configs':
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
    lines.append("---\n")

    return "".join(lines)


def generate_directory_tree(structure, config):
    """生成目录树（带auto/manual分类）"""
    categories_config = config.get('categories', {})
    root_files_config = config.get('root_files', [])
    core_config = config.get('core_config', {})

    lines = []
    lines.append("## 📁 文档目录结构\n")
    lines.append("```")
    lines.append("docs/")
    lines.append("│")
    lines.append("├── 00_Index/")
    lines.append("│   ├── 文档索引清单.md              ← 本文档")
    lines.append("│   ├── _generators/")
    lines.append("│   │   └── index_generator.py")
    lines.append("│   └── configs/")
    lines.append("│       └── index_config.yaml")
    lines.append("│")
    lines.append("├── 项目文档综合改进规划方案.md      ← 项目规划")
    lines.append("├── 状态快照.json")
    lines.append("│")

    sorted_cats = sorted(
        categories_config.items(),
        key=lambda x: x[1].get('priority', 99)
    )

    for cat_id, cat_info in sorted_cats:
        cat_data = structure.get(cat_id, {'root': [], 'auto': [], 'manual': [], 'configs': []})
        root_files = sorted(cat_data.get('root', []), key=lambda x: x['name'])
        auto_files = sorted(cat_data.get('auto', []), key=lambda x: x['name'])
        manual_files = sorted(cat_data.get('manual', []), key=lambda x: x['name'])
        config_files = sorted(cat_data.get('configs', []), key=lambda x: x['name'])

        if not root_files and not auto_files and not manual_files and not config_files:
            continue

        lines.append(f"├── {cat_id}/                          ← {cat_info['name']}")

        if root_files:
            for f in root_files:
                lines.append(f"│   └── {f['name']}")

        if auto_files:
            lines.append("│   └── auto/")
            for i, f in enumerate(auto_files):
                is_last = (i == len(auto_files) - 1) and not manual_files and not config_files
                prefix = "└──" if is_last else "├──"
                lines.append(f"│       {prefix} {f['name']}")

        if manual_files:
            is_last = not config_files
            prefix = "└──" if is_last else "├──"
            lines.append(f"│   └── manual/")
            for i, f in enumerate(manual_files):
                is_last_file = (i == len(manual_files) - 1) and not config_files
                prefix_file = "└──" if is_last_file else "├──"
                lines.append(f"│       {prefix_file} {f['name']}")

        if config_files:
            lines.append("│   └── configs/")
            for i, f in enumerate(config_files):
                is_last = (i == len(config_files) - 1)
                prefix = "└──" if is_last else "├──"
                lines.append(f"│       {prefix} {f['name']}")

    lines.append("│")
    lines.append("└── configs/                              ← ★核心配置系统")
    lines.append("    ├── system_config.yaml           ← ★单一真相源")
    lines.append("    ├── README.md")
    lines.append("    └── generators/")
    lines.append("        ├── PLC_Arch_generator.py")
    lines.append("        ├── TagCode_generator.py")
    lines.append("        ├── DeviceParam_generator.py")
    lines.append("        └── run_all_generators.py")
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


def generate_file_list_table(structure, config):
    """生成详细文件列表（按auto/manual分类）"""
    categories_config = config.get('categories', {})

    lines = []
    lines.append("## 📄 文档清单（按编辑方式分类）\n")

    sorted_cats = sorted(categories_config.items(), key=lambda x: x[1].get('priority', 99))

    for cat_id, cat_info in sorted_cats:
        cat_data = structure.get(cat_id, {'root': [], 'auto': [], 'manual': [], 'configs': []})
        root_files = cat_data.get('root', [])
        auto_files = cat_data.get('auto', [])
        manual_files = cat_data.get('manual', [])
        config_files = cat_data.get('configs', [])

        if not root_files and not auto_files and not manual_files and not config_files:
            continue

        lines.append(f"### {cat_id} {cat_info['name']}\n")

        if auto_files:
            lines.append("#### 🔧 自动生成文档 (auto/)\n")
            lines.append("| 文档 | 版本 | 更新日期 | 说明 |")
            lines.append("| ---- | ---- | -------- | ---- |")
            for f in sorted(auto_files, key=lambda x: x['name']):
                lines.append(f"| {f['name']} | v{f['version']} | {f['date']} | {f['desc']} |")
            lines.append("")

        if manual_files:
            lines.append("#### ✏️ 手动编辑文档 (manual/)\n")
            lines.append("| 文档 | 版本 | 更新日期 | 说明 |")
            lines.append("| ---- | ---- | -------- | ---- |")
            for f in sorted(manual_files, key=lambda x: x['name']):
                lines.append(f"| {f['name']} | v{f['version']} | {f['date']} | {f['desc']} |")
            lines.append("")

        if root_files:
            lines.append("| 其他文档 | 版本 | 更新日期 | 说明 |")
            lines.append("| ---- | ---- | -------- | ---- |")
            for f in sorted(root_files, key=lambda x: x['name']):
                lines.append(f"| {f['name']} | v{f['version']} | {f['date']} | {f['desc']} |")
            lines.append("")

        lines.append("---\n")

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
    lines.append("| 生成器 | 输入 | 输出 | 用途 |")
    lines.append("| ------ | ---- | ---- | ---- |")

    for g in generators:
        inputs_str = "<br>".join(g.get('inputs', []))
        outputs = g.get('outputs', [])
        if isinstance(outputs, list):
            outputs_str = "<br>".join(outputs)
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

    if 'core_config_modification' in rules:
        tm = rules['core_config_modification']
        lines.append(f"### 1. {tm['title']}\n")
        for step in tm.get('steps', []):
            lines.append(f"{step}\n")
        lines.append("\n")

    if 'device_config_modification' in rules:
        dm = rules['device_config_modification']
        lines.append(f"### 2. {dm['title']}\n")
        for step in dm.get('steps', []):
            lines.append(f"{step}\n")
        lines.append("\n")

    if 'manual_doc_modification' in rules:
        sc = rules['manual_doc_modification']
        lines.append(f"### 3. {sc['title']}\n")
        for content in sc.get('steps', []):
            lines.append(f"{content}\n")
        lines.append("\n")

    if 'version_rules' in rules:
        vr = rules['version_rules']
        lines.append(f"### 4. {vr['title']}\n")
        lines.append("| 文档类型 | 更新时机 | 版本号规则 |")
        lines.append("| ---- | ------ | ----------- |")
        for rule in vr.get('rules', []):
            lines.append(f"| {rule['doc_type']} | {rule['trigger']} | {rule['rule']} |")
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
    document.append(generate_file_list_table(structure, config))
    document.append(generate_dependency_matrix(config))
    document.append(generate_generator_table(config))
    document.append(generate_maintenance_rules(config))
    document.append(generate_change_log(config))

    return "".join(document)


def main():
    print("文档索引清单生成器 (配置驱动版 v3.0)")
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
