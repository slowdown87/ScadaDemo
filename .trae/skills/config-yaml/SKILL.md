---
name: "config-yaml"
description: "YAML配置管理技能。管理茶饮料SCADA系统的配置文件，包括system_config、fb_spec、hmi_config、recipe_templates等。激活场景：读取配置、验证配置格式、修改配置参数、理解配置依赖关系。"
---

# YAML 配置管理技能

管理茶饮料SCADA系统的配置文件，提供配置读取、验证和修改指导。

## 配置文件清单

| 配置文件 | 路径 | 用途 |
|----------|------|------|
| **system_config.yaml** | 01_Spec/configs/ | 系统核心配置（PLC定义、工段定义、工艺流程、设备清单） |
| **fb_spec_config.yaml** | 01_Spec/configs/ | PLC功能块规格（输入输出接口、参数、诊断码） |
| **hmi_config.yaml** | 01_Spec/configs/ | HMI画面配置 |
| **process_recipe_templates.yaml** | 01_Spec/configs/ | 工艺配方和CIP程序模板 |
| **product_recipe_templates.yaml** | 01_Spec/configs/ | 产品配方模板 |
| **comm_templates.yaml** | 01_Spec/configs/ | 通讯接口配置 |
| **interlock_templates.yaml** | 01_Spec/configs/ | 联锁逻辑模板 |
| **index_config.yaml** | 01_Spec/configs/ | 文档索引配置 |
| **cabinet_bom.yaml** | 01_Spec/configs/ | 电控柜BOM配置 |
| **instrument_list.yaml** | 01_Spec/configs/ | 仪表清单配置 |
| **terminal_assignments.yaml** | 01_Spec/configs/ | 端子定义配置 |
| **cable_list.yaml** | 01_Spec/configs/ | 电缆清单配置 |

## 配置结构解析

### system_config.yaml 结构

```
meta                    # 元信息（版本、作者、项目名）
├── version
├── project_name
├── capacity
└── base_ip_subnet

plcs                    # 16个PLC定义
├── PLC-1 ~ PLC-16
│   ├── name, section, cpu
│   ├── ip, io_estimate
│   └── role, process_order

sections                # 16个工段定义
├── WT, TH, EX, FL, BL
├── HM, UH, BF, PF, CG
├── LI, CI, LB, CA, PK, CP
│   ├── prefix, plc
│   ├── upstream, downstream
│   └── process_flow

process_flow            # 工艺流程
├── liquid_line         # 液料生产线
├── packaging_line      # 包装生产线
└── independent_systems # 独立系统

high_speed_sync         # 高速同步配置
plc_comm_matrix         # PLC间通讯矩阵
scada_components        # SCADA组件IP
ob_config               # 中断组织块配置
critical_control_points # CCP关键控制点
control_levels          # 控制级别定义
io_summary              # I/O统计
material_balance         # 物料平衡
devices                 # 设备清单（按工段）
```

### fb_spec_config.yaml 结构

```
meta                    # 元信息
├── version
├── programming_standard  # IEC 61131-3

basic_function_blocks   # 基础控制功能块
├── FB_Valve_Control     # 阀门控制
├── FB_Pump_Control      # 泵控制
└── FB_PID_Control      # PID控制

process_function_blocks # 工艺控制功能块
├── FB_Level_Control     # 液位控制
├── FB_Temperature_Control
├── FB_Pressure_Control
├── FB_Flow_Control
├── FB_Brix_Control      # 糖度控制
└── FB_PH_Control        # pH控制

batch_function_blocks   # 批次控制
└── FB_Batch_Control    # 调配批次控制

uht_function_blocks     # UHT杀菌专用
└── FB_UHT_Temperature_Profile

filling_function_blocks # 灌装系统专用
├── FB_Speed_Sync       # 高速速度同步
└── FB_Capping_Torque   # 旋盖扭矩控制
```

## 常用操作

### 1. 读取配置

使用 Python 读取 YAML 配置：

```python
import yaml
from pathlib import Path

def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 读取系统配置
config = load_yaml('docs/01_Spec/configs/system_config.yaml')

# 访问PLC配置
plc_1 = config['plcs']['PLC-1']
print(f"PLC-1: {plc_1['name']}, IP: {plc_1['ip']}")

# 访问设备清单
wt_devices = config['devices']['WT']
for device in wt_devices:
    print(f"{device['id']}: {device['name']}")
```

### 2. 遍历所有工段的设备

```python
for section_code, devices in config['devices'].items():
    print(f"\n=== {section_code} ===")
    for device in devices:
        print(f"  {device['id']}: {device['name']}")
```

### 3. 查找特定设备

```python
def find_device(config, device_id):
    for section, devices in config['devices'].items():
        for device in devices:
            if device['id'] == device_id:
                return device
    return None

device = find_device(config, 'UH-101')
```

### 4. 验证配置格式

```python
import yaml

def validate_yaml(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"✓ {file_path} 格式正确")
        return True, data
    except yaml.YAMLError as e:
        print(f"✗ {file_path} 格式错误: {e}")
        return False, None
```

## 配置依赖关系

```
system_config.yaml (基础)
    ├── fb_spec_config.yaml (引用PLC定义生成功能块)
    ├── hmi_config.yaml (引用工段定义)
    ├── process_recipe_templates.yaml (引用工艺参数)
    └── → 生成文档 ← (被生成器读取)

生成器输入:
    system_config.yaml → PLC架构、位号、监控点表、设备参数
    fb_spec_config.yaml → 功能块规格书
    hmi_config.yaml → HMI画面规格
    process_recipe_templates.yaml → 工艺配方、CIP程序
```

## 修改配置注意事项

### ⚠️ 修改前检查

1. **版本兼容性**：检查 meta.version 是否需要更新
2. **依赖关系**：确认修改不会影响依赖此配置的其他文件
3. **数据一致性**：确保关键字段（如IP、名称）全局唯一
4. **备份**：重要修改前先备份

### ⚠️ 关键字段

| 字段 | 说明 | 修改风险 |
|------|------|----------|
| `plcs[].ip` | PLC IP地址 | 高 - 影响通讯 |
| `plcs[].section` | PLC所属工段 | 高 - 影响工艺流程 |
| `sections[].plc` | 工段对应的PLC | 高 - 影响控制逻辑 |
| `devices[].id` | 设备编码 | 高 - 影响位号生成 |
| `control_levels` | 控制级别定义 | 中 - 影响报警逻辑 |

### ✅ 安全修改范围

以下字段可相对安全地修改：
- `meta` 中的描述性字段（不影响系统运行）
- `devices` 中的规格、供应商等辅助信息
- `control_templates` 中的PID参数初值（需现场调试）
- 注释和文档字段

## 自检清单

修改配置前：
```
[ ] 明确修改目的和预期效果
[ ] 备份原始文件
[ ] 检查配置语法（YAML格式）
[ ] 验证关键字段唯一性
[ ] 确认依赖关系未被破坏
```

修改配置后：
```
[ ] 运行 template_validator.py 验证
[ ] 如有需要，重新生成受影响文档
[ ] 更新相关文档的版本号
[ ] 记录变更内容
```

## 故障排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| YAML解析错误 | 缩进不一致、TAB字符 | 使用空格缩进，检查格式 |
| 字段缺失 | 配置不完整 | 对照模板补全 |
| 引用无效 | 引用了不存在的key | 检查拼写和层级 |
| 数据不一致 | 多处定义了同名项 | 合并或删除重复项 |
