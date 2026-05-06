#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HMI_Screens_generator.py
茶饮料生产线SCADA系统 - HMI画面规格说明书生成器

功能: 从 hmi_screens_config.yaml 读取配置，自动生成完整的HMI画面规格说明书

使用方法:
    python HMI_Screens_generator.py

输入:
    01_Spec/configs/hmi_screens_config.yaml - HMI画面配置

输出:
    01_Spec/auto/HMI_Screens_auto.md - HMI画面规格说明书

依赖:
    - PyYAML
"""

import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

# ============================================================================
# 配置
# ============================================================================
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_FILE = PROJECT_ROOT / "01_Spec" / "configs" / "hmi_screens_config.yaml"
OUTPUT_FILE = PROJECT_ROOT / "01_Spec" / "auto" / "茶饮料_HMI画面规格_auto.md"

# ============================================================================
# 工具函数
# ============================================================================
def log_info(msg):
    print(f"[INFO] {msg}")

def log_success(msg):
    print(f"[SUCCESS] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}")

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

# ============================================================================
# 文档生成函数
# ============================================================================
def generate_header(config):
    meta = config.get('meta', {})
    now = datetime.now().strftime('%Y-%m-%d')
    return f"""# 茶饮料生产线SCADA画面规格说明书

> 文档版本: {meta.get('version', 'v1.0')}
> 创建日期: {meta.get('created', now)}
> 更新日期: {now}
> 数据来源: SCADA系统功能规格说明书、监控点表
> 项目名称: {meta.get('project_name', '茶饮料生产线SCADA监控系统')}
> 产品类型: {meta.get('product_type', '纯茶饮料')}
> 产能: {meta.get('capacity', '50000B/H')}

---

## 文档关系说明

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          本文档: HMI画面规格说明书                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  定位: SCADA系统功能规格说明书的界面实现层                               │
│                                                                             │
│  上游文档: SCADA系统功能规格说明书.md                                       │
│  └── 定义了: 功能ID、位号、报警阈值、控制回路                                │
│  └── 本文档继承并实现:                                                      │
│       ├── 功能ID → 画面功能                         │                      │
│       ├── 位号 → 控件数据绑定                       │                      │
│       ├── 报警等级 → 颜色/声音/闪烁                 │                      │
│       ├── 控制回路 → 操作控件                        │                      │
│       └── 数据规格 → 显示格式(小数位/单位)           │                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

"""

def generate_navigation_tree(config):
    screens = config.get('screens', [])
    priority_defs = config.get('priority_definitions', {})

    nav_lines = ["SCADA监控系统"]
    for screen in screens:
        priority = screen.get('priority', '')
        nav_lines.append(f"│")
        nav_lines.append(f"├── {screen['id']}: {screen['name']} [{priority}]")
        nav_lines.append(f"│   └── {screen.get('description', '')}")
    tree = "\n".join(nav_lines)

    priority_rows = []
    for p_level, p_info in sorted(priority_defs.items()):
        response_time = p_info.get('response_time', '')
        if response_time and response_time.endswith('s'):
            response_time = response_time + '刷新'
        elif response_time and response_time != '按需':
            response_time = response_time + 's刷新'
        else:
            response_time = '按需刷新' if response_time == '按需' else response_time
        priority_rows.append(f"| {p_level} | {p_info.get('count', 0)}个 | {response_time} | {p_info.get('description', '')} |")

    output = f"""## 1. 画面架构

### 1.1 画面导航树

```
{tree}
```

### 1.2 画面优先级

| 优先级 | 画面数量 | 响应要求 | 说明 |
|--------|----------|----------|------|
"""
    for row in priority_rows:
        output += row + "\n"

    output += """
---

"""

    return output

def generate_control_library(config):
    lib = config.get('control_library', {})

    return f"""## 2. 控件库规格

### 2.1 基础控件

#### 2.1.1 数值显示控件 (NumericDisplay)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | NumericDisplay | 数值显示 |
| 字体 | {lib.get('numeric_display', {}).get('font', 'Consolas')} | 等宽字体 |
| 字号 | {lib.get('numeric_display', {}).get('font_size', 16)}pt | 主值显示 |
| 小数位 | {lib.get('numeric_display', {}).get('decimal_places', '1-2')} | 可配置 |
| 单位 | 右下标 | 自动附加单位 |
| 颜色 | {lib.get('numeric_display', {}).get('colors', {}).get('normal', '白')}/{lib.get('numeric_display', {}).get('colors', {}).get('warning', '黄')}/{lib.get('numeric_display', {}).get('colors', {}).get('alarm', '红')} | 正常/警告/报警 |

#### 2.1.2 液位条控件 (LevelIndicator)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | LevelIndicator | 液位显示 |
| 方向 | {lib.get('level_indicator', {}).get('direction', '垂直')} | 从下往上填充 |
| 高度 | {lib.get('level_indicator', {}).get('height', 100)}px | 标准尺寸 |
| 宽度 | {lib.get('level_indicator', {}).get('width', 30)}px | 标准尺寸 |
| 填充色 | {lib.get('level_indicator', {}).get('fill_color', '#0066FF')} | 蓝色 |
| 背景色 | {lib.get('level_indicator', {}).get('bg_color', '#2a3a5a')} | 深蓝灰 |
| 高液位 | {lib.get('level_indicator', {}).get('high_alarm', '#FF6600')} | 橙色预警 |
| 低液位 | {lib.get('level_indicator', {}).get('low_alarm', '#00CCFF')} | 浅蓝预警 |
| 超限 | {lib.get('level_indicator', {}).get('over_limit', '#FF0000')} | 红色报警 |

**位置规格**:
```
┌────┐  ← 100% (HH报警线)
│████│
│████│
│░░░░│  ← 液位填充
│░░░░│
└────┘  ← 0% (LL报警线)
```

#### 2.1.3 阀门控件 (ValveSymbol)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | ValveSymbol | 阀门状态显示 |
| 形状 | 菱形 | {lib.get('valve_symbol', {}).get('size', '16×16px')} |
| 打开状态 | {lib.get('valve_symbol', {}).get('open_color', '#00FF00')} | 绿色填充 |
| 关闭状态 | {lib.get('valve_symbol', {}).get('closed_color', '#808080')} | 灰色边框 |
| 故障状态 | {lib.get('valve_symbol', {}).get('fault_color', '#FF0000')} | 红色填充 |
| 中间状态 | {lib.get('valve_symbol', {}).get('transitioning_color', '#FFFF00')} | 黄色填充 |
| 开度指示 | 内部百分比 | 数字显示 |

**状态定义**:
```
┌─────────────────────────────┐
│ 状态    │ 颜色   │ 动画    │
├─────────┼────────┼─────────┤
│ 打开    │ 绿色   │ 无      │
│ 关闭    │ 灰色   │ 无      │
│ 打开中  │ 绿色   │ 脉冲    │
│ 关闭中  │ 灰色   │ 脉冲    │
│ 故障    │ 红色   │ 闪烁1Hz │
│ 联锁    │ 黄色   │ 闪烁1Hz │
└─────────────────────────────┘
```

#### 2.1.4 泵控件 (PumpSymbol)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | PumpSymbol | 泵状态显示 |
| 形状 | 圆形+三角形 | {lib.get('pump_symbol', {}).get('size', '24×24px')} |
| 运行状态 | 绿色+旋转动画 | {lib.get('pump_symbol', {}).get('animation', {}).get('fps', 25)}fps |
| 停止状态 | 灰色静态 | 无 |
| 故障状态 | 红色+闪烁 | 1Hz |
| 过载状态 | 黄色+闪烁 | 1Hz |

**旋转动画规格**:
```
运行状态时，显示旋转的三角形标记:
    ▲ → ↗ → → ↘ → ▼ → ↙ → ← → ↖ → ▲
   0°   45°  90°  135° 180° 225° 270° 315°
帧率: {lib.get('pump_symbol', {}).get('animation', {}).get('fps', 25)}fps (每帧36°旋转)
```

#### 2.1.5 管道流动控件 (PipelineFlow)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | PipelineFlow | 管道流动动画 |
| 管道宽度 | {lib.get('pipeline_flow', {}).get('pipe_width', 8)}px | 标准管道 |
| 液体颜色 | {lib.get('pipeline_flow', {}).get('liquid_color', '#0066FF')} | 蓝色 |
| 气体颜色 | {lib.get('pipeline_flow', {}).get('gas_color', '#FFCC00')} | 黄色 |
| 流动方向 | 沿管道方向 | 虚线移动 |
| 动画速度 | 与流量成正比 | - |
| 静止状态 | 实线 | 无动画 |

### 2.2 报警控件

#### 2.2.1 报警条控件 (AlarmBanner)

| 属性 | 规格 |
|------|------|
| 控件类型 | AlarmBanner |
| 高度 | {lib.get('alarm_banner', {}).get('height', 40)}px |
| 宽度 | 100% |
| HH报警 | 红色背景 + 白色文字 + 闪烁 |
| H报警 | 黄色背景 + 黑色文字 |
| L报警 | 黄色背景 + 黑色文字 |
| LL报警 | 红色背景 + 白色文字 + 闪烁 |
| D报警 | 蓝色背景 + 白色文字 |
| F报警 | 红色背景 + 白色文字 |
| 字体 | {lib.get('alarm_banner', {}).get('font', '微软雅黑 14pt')} |
| 声音 | HH/LL连续, H/L断续 |

**闪烁规格**:
```
闪烁频率: {lib.get('alarm_banner', {}).get('flash_frequency', '1Hz')} (0.5s亮, 0.5s灭)
优先级: 同时多个报警时显示最高优先级
自动滚动: 多条时从右向左滚动
```

#### 2.2.2 报警确认按钮 (AlarmAckButton)

| 属性 | 规格 |
|------|------|
| 控件类型 | AlarmAckButton |
| 尺寸 | {lib.get('alarm_ack_button', {}).get('size', '80×32px')} |
| 默认状态 | 灰色背景, 白色文字"确认" |
| 有未确认报警 | 黄色背景 |
| 点击效果 | 消除声音, 变灰 |
| 权限 | 操作员及以上 |

### 2.3 操作控件

#### 2.3.1 按钮控件 (Button)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | Button | 操作按钮 |
| 尺寸 | {lib.get('button', {}).get('size', '80×32px')} | 标准 |
| 字体 | {lib.get('button', {}).get('font', '微软雅黑 14pt')} | - |
| 默认状态 | {lib.get('button', {}).get('states', {}).get('default', {}).get('bg', '#2a3a5a')}背景, 白色文字 |
| 悬停状态 | {lib.get('button', {}).get('states', {}).get('hover', {}).get('bg', '#3a4a6a')}背景 |
| 按下状态 | {lib.get('button', {}).get('states', {}).get('pressed', {}).get('bg', '#1a2a4a')}背景 |
| 禁用状态 | {lib.get('button', {}).get('states', {}).get('disabled', {}).get('bg', '#1a1a1a')}背景, 灰色文字 |

**按钮类型**:
```
┌────────────────────────────────────────────────────────┐
│ 类型        │ 背景色     │ 文字色   │ 用途           │
├─────────────┼────────────┼──────────┼────────────────┤
│ 启动/打开   │ {lib.get('button', {}).get('types', {}).get('start', {}).get('bg', '#006600')}    │ 白色     │ 泵启动,阀打开  │
│ 停止/关闭   │ {lib.get('button', {}).get('types', {}).get('stop', {}).get('bg', '#660000')}    │ 白色     │ 泵停止,阀关闭  │
│ 复位        │ {lib.get('button', {}).get('types', {}).get('reset', {}).get('bg', '#665500')}    │ 白色     │ 故障复位       │
│ 确认        │ {lib.get('button', {}).get('types', {}).get('ack', {}).get('bg', '#005566')}    │ 白色     │ 报警确认       │
│ 操作        │ {lib.get('button', {}).get('types', {}).get('operate', {}).get('bg', '#2a3a5a')}    │ 白色     │ 一般操作       │
│ 紧急        │ {lib.get('button', {}).get('types', {}).get('emergency', {}).get('bg', '#CC0000')}    │ 白色     │ 紧急停止       │
└────────────────────────────────────────────────────────┘
```

#### 2.3.2 设定值输入控件 (SetpointInput)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | SetpointInput | 设定值输入 |
| 输入框尺寸 | {lib.get('setpoint_input', {}).get('size', '80×28px')} | 宽度可调 |
| 字体 | {lib.get('setpoint_input', {}).get('font', 'Consolas 14pt')} | 数值字体 |
| 默认背景 | {lib.get('setpoint_input', {}).get('bg_normal', '#1a2235')} |
| 聚焦背景 | {lib.get('setpoint_input', {}).get('bg_focused', '#2a3a5a')} |
| 越限处理 | 红色边框, 弹回原值 |
| 权限控制 | 灰色禁用+权限提示 |

### 2.4 图表控件

#### 2.4.1 趋势曲线控件 (TrendChart)

| 属性 | 规格 | 说明 |
|------|------|------|
| 控件类型 | TrendChart | 趋势曲线 |
| 画布高度 | {lib.get('trend_chart', {}).get('canvas_height', 300)}px | 标准高度 |
| 时间轴 | 水平, 右端为当前时间 |
| 数值轴 | 垂直, 自动刻度 |
| 网格线 | 可选显示 | 灰色虚线 |
| 曲线宽度 | {lib.get('trend_chart', {}).get('line_width', 2)}px |
| 曲线颜色 | 最多{lib.get('trend_chart', {}).get('max_colors', 8)}种颜色 |
| 采样周期 | {lib.get('trend_chart', {}).get('sample_period', '10s')} |
| 显示时长 | 1h/4h/8h/24h可选 |

#### 2.4.2 棒图控件 (BarChart)

| 属性 | 规格 |
|------|------|
| 控件类型 | BarChart |
| 用途 | 产量、统计数据显示 |
| 方向 | 垂直 |
| 柱宽 | {lib.get('bar_chart', {}).get('bar_width', 20)}px |
| 柱间距 | {lib.get('bar_chart', {}).get('bar_spacing', 8)}px |
| 数值显示 | 柱顶数字 |

---

"""

def generate_standard_layout(config):
    layout = config.get('standard_layout', {})
    header = layout.get('header', {})
    status_bar = layout.get('status_bar', {})

    return f"""## 3. 通用画面模板

### 3.1 标准画面布局

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│[Logo] 画面标题                                           [时间] [用户] [退出]     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ [返回] [总貌] │  {', '.join(layout.get('navigation_bar', {}).get('sections', ['WT', 'EX', 'FL', 'BL', 'HM', 'UH', 'PF', 'PK', 'CIP']))}  │  {', '.join(layout.get('navigation_bar', {}).get('right_items', ['趋势', '报警', '报表', '用户']))} │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │                          工艺流程/状态区域                                  │   │
│  │                          (占画面60%高度)                                    │   │
│  │                                                                             │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────────────┐   │
│  │      设备状态面板          │  │              参数监控面板                    │   │
│  │      (占左30%)             │  │              (占右70%)                     │   │
│  │                             │  │                                             │   │
│  │  泵状态列表                 │  │  关键参数表格                               │   │
│  │  阀状态列表                 │  │  ├── 参数名/值/单位                        │   │
│  │  电机状态                   │  │  ├── 颜色指示                             │   │
│  │                             │  │  └── 点击可进入趋势                        │   │
│  └─────────────────────────────┘  └─────────────────────────────────────────────┘   │
│                                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────────┐   │
│  │  [操作按钮1] [操作按钮2] [操作按钮3] [配方选择▼] [启动] [停止] [复位]      │   │
│  └─────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ 状态栏: 连接状态:● | PLC-1:● PLC-2:● PLC-3:● | 当前批次:BL-20260429-001       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 画面标题栏规格

| 元素 | 位置 | 规格 |
|------|------|------|
| Logo | 左上角 | {header.get('logo', {}).get('size', '32×32px')}, 企业Logo |
| 画面标题 | 标题区中央 | 微软雅黑 24pt 白色 |
| 当前时间 | 右上 | 格式: "{header.get('time_format', 'YYYY-MM-DD HH:mm:ss')}" |
| 当前用户 | 时间左侧 | 格式: "{header.get('user_format', '角色:用户名')}" |
| 用户退出 | 最右 | 按钮 "退出" |

### 3.3 状态栏规格

| 元素 | 规格 |
|------|------|
| 位置 | 画面最下方 |
| 高度 | {status_bar.get('height', 24)}px |
| 背景色 | {status_bar.get('bg_color', '#1a2235')} |
| 连接状态指示 | ●绿色=正常, ●红色=断开 |
| PLC状态 | ●绿色=运行, ●黄色=警告, ●红色=故障 |
| 当前批次 | 显示当前执行批次号 |
| 字体 | {status_bar.get('font', '微软雅黑 11pt')} {status_bar.get('font_color', '白色')} |

---

"""

def generate_screen_details(config):
    screens = config.get('screens', [])
    ccp_points = config.get('ccp_points', [])

    output = "## 4. 画面详细规格\n\n"

    for screen in screens:
        screen_id = screen.get('id', '')
        screen_name = screen.get('name', '')
        priority = screen.get('priority', '')
        is_ccp = screen.get('is_ccp', False)
        section = screen.get('section', '')
        functions = screen.get('functions', [])

        output += f"""### {screen_id} {screen_name}

#### 画面基本信息

| 项目 | 内容 |
|------|------|
| 画面ID | {screen_id} |
| 画面名称 | {screen_name} |
| 优先级 | {priority} |
| 所属工段 | {section.upper() if section else '通用'} |
| 是否CCP | {'是' if is_ccp else '否'} |
| 关联功能ID | {', '.join(functions) if functions else '-'} |

"""

        if is_ccp:
            output += "#### CCP监控配置\n\n"
            for ccp in ccp_points:
                if ccp.get('section', '').upper() == section.upper():
                    output += f"| 位号 | {ccp.get('tag', '')} |\n"
                    output += f"| 描述 | {ccp.get('description', '')} |\n"
                    output += "| 报警等级 | 阈值 | 联锁动作 |\n"
                    output += "|----------|------|----------|\n"
                    for level, info in ccp.get('alarm_levels', {}).items():
                        output += f"| {level} | {info.get('threshold', '')} | {info.get('interlock_action', '')} |\n"
                    output += "\n"

        output += "---\n\n"

    return output

def generate_interaction_spec(config):
    interaction = config.get('interaction_specs', {})
    permissions = config.get('permission_checks', {})
    performance = config.get('performance_specs', {})

    mouse_lines = []
    for item in interaction.get('mouse', []):
        mouse_lines.append(f"| {item.get('action', '')} | {item.get('target', '')} | {item.get('response', '')} |")

    keyboard_lines = []
    for item in interaction.get('keyboard', []):
        keyboard_lines.append(f"| {item.get('key', '')} | {item.get('function', '')} |")

    perm_lines = []
    for op, info in permissions.items():
        perm_lines.append(f"| {op} | {info.get('required_level', '')} | {info.get('denied_response', '')} |")

    response_lines = []
    for item, time in performance.get('response_times', {}).items():
        response_lines.append(f"| {item} | {time} |")

    refresh_lines = []
    for level, info in performance.get('refresh_strategies', {}).items():
        refresh_lines.append(f"| {level} | {info.get('mode', '')} | {info.get('period', info.get('trigger', ''))} |")

    return f"""## 5. 交互规格

### 5.1 鼠标交互

| 操作 | 目标控件 | 响应 |
|------|----------|------|
{"".join([f"{line}" for line in mouse_lines])}

### 5.2 键盘快捷键

| 快捷键 | 功能 |
|--------|------|
{"".join([f"{line}" for line in keyboard_lines])}

### 5.3 权限验证

| 操作 | 权限等级 | 无权限响应 |
|------|----------|------------|
{"".join([f"{line}" for line in perm_lines])}

---

## 6. 性能规格

### 6.1 响应时间

| 操作 | 最大响应时间 | 说明 |
|------|------------|------|
{"".join([f"{line}" for line in response_lines])}

### 6.2 刷新策略

| 数据类型 | 刷新方式 | 周期 |
|----------|----------|------|
{"".join([f"{line}" for line in refresh_lines])}

---

## 7. 跨文档引用

### 7.1 被本文档引用

| 文档 | 引用内容 |
|------|----------|
| SCADA系统功能规格说明书.md | 功能ID、位号规格、报警阈值、控制回路、权限定义 |

### 7.2 本文档引用

| 引用目标 | 说明 |
|----------|------|
| SCADA系统功能规格说明书.md 第3章 | 监控点位规格 |
| SCADA系统功能规格说明书.md 第4.2节 | 报警功能需求 |
| SCADA系统功能规格说明书.md 第4.3节 | 控制功能需求 |
| PLC_Architecture.md | 设备控制逻辑 |
| FB_Spec_Template.yaml | 功能块接口定义 |

---

**文档状态**: 自动生成
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据来源**: `01_Spec/configs/hmi_screens_config.yaml`
**生成器脚本**: `docs/_generators/HMI_Screens_generator.py`

**版本历史**:
- v1.0 ({datetime.now().strftime('%Y-%m-%d')}): 初始版本，基于配置自动生成
"""

# ============================================================================
# 主函数
# ============================================================================
def main():
    log_info("=" * 60)
    log_info("HMI_Screens_generator.py - HMI画面规格说明书生成器")
    log_info("=" * 60)

    log_info(f"读取配置文件: {CONFIG_FILE}")
    config = load_yaml(CONFIG_FILE)
    log_success(f"配置加载成功: {config.get('meta', {}).get('version', 'N/A')}")

    log_info("生成HMI画面规格说明书...")

    content = generate_header(config)
    content += generate_navigation_tree(config)
    content += generate_control_library(config)
    content += generate_standard_layout(config)
    content += generate_screen_details(config)
    content += generate_interaction_spec(config)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    log_success(f"文档生成成功: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
