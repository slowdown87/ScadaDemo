# SCADA数字孪生系统 - 专业级升级方案

> 文档版本: v1.1
> 创建日期: 2026-04-23
> 更新日期: 2026-04-24
> 项目名称: ScadaDemo
> GitHub: https://github.com/slowdown87/ScadaDemo
> Pages: https://slowdown87.github.io/ScadaDemo/
> **部署方案: 方案1 - 纯前端（GitHub Pages）**

---

## 一、需求分析

### 1.1 现状评估

| 维度 | 当前状态 | 专业级差距 |
|------|----------|-----------|
| **3D模型** | 简单几何体堆砌（立方体、圆柱体组合） | 需要高精度BIM模型，PBR材质，真实纹理 |
| **视觉效果** | 基础金属材质，固定光照 | 需要实时光线追踪，AO贴图，环境反射 |
| **数据系统** | Mock静态数据，模拟温度升高 | 需要OPC-UA/Modbus实时对接，真实PLC通信 |
| **交互能力** | 仅旋转缩放视角 | 设备点击详情、参数控制、阀门操作 |
| **报警管理** | 简单的颜色变化 | 完整的报警确认、根因分析、趋势预判 |
| **物料追踪** | 无 | 从原料到成品的端到端追踪 |
| **仿真能力** | 无 | 工艺推演、故障模拟、预案沙盘 |

### 1.2 目标系统能力

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户层                                     │
├─────────────────────────────────────────────────────────────────┤
│  运维人员          │  管理人员          │  工艺工程师           │
│  - 实时监控        │  - KPI大屏         │  - 工艺仿真           │
│  - 设备控制        │  - 生产报表         │  - 参数优化           │
│  - 报警处理        │  - 产能分析         │  - 故障复盘           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    展示层 (Vue3 + Three.js + ECharts)           │
├─────────────────────────────────────────────────────────────────┤
│  四级导航    │  3D数字孪生  │  实时数据  │  报警中心  │  仿真推演  │
│  (园区→车间→产线→工位)      │  可视化    │  面板      │  模块      │
├─────────────────────────────────────────────────────────────────┤
│                   业务层 (Pinia Store + Mock数据)               │
├─────────────────────────────────────────────────────────────────┤
│  数据服务    │  Mock引擎    │  模拟WebSocket │ 仿真引擎  │  权限控制  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、系统架构

### 2.1 总体架构

```
scada-demo/
├── src/
│   ├── assets/               # 静态资源（SVG、贴图）
│   ├── components/           # 通用组件
│   │   ├── common/          # 公共组件（Header、SideNav）
│   │   ├── plant/           # 工厂组件
│   │   └── charts/          # 图表组件
│   ├── composables/         # 组合式函数
│   ├── three/               # Three.js模块
│   │   ├── Plant3D.js       # 3D场景主模块
│   │   └── models/          # 3D模型管理
│   ├── services/            # Mock数据服务
│   │   ├── mockData.js      # 模拟数据生成
│   │   └── dataSimulator.js # 数据模拟引擎
│   ├── stores/               # Pinia状态
│   │   ├── plantStore.js    # 工厂数据
│   │   ├── alarmStore.js    # 报警数据
│   │   └── perfStore.js     # 性能数据
│   ├── views/                # 页面视图
│   ├── router/               # 路由
│   └── App.vue
├── public/
│   └── models/               # GLTF/GLB模型文件（未来）
├── docs/                     # 文档
└── package.json
```

### 2.2 技术栈

| 层级 | 技术选型 | 版本 | 说明 |
|------|----------|------|------|
| **前端框架** | Vue3 | 3.4+ | 组合式API |
| **构建工具** | Vite | 5.0+ | 快速构建 |
| **状态管理** | Pinia | 2.1+ | TypeScript支持 |
| **3D引擎** | Three.js | 0.160+ | WebGL |
| **3D辅助** | OrbitControls | - | 相机控制 |
| **图表** | ECharts | 5.4+ | 高性能图表 |
| **样式** | SCSS + CSS Variables | - | 主题切换 |
| **路由** | Vue Router | 4.0+ | Hash模式 |
| **部署** | GitHub Pages | - | 前端托管 |

### 2.3 数据流设计

```
┌─────────────────────────────────────────────────────────────────┐
│                         模拟数据流                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Mock数据    │ ──► │   模拟引擎   │ ──► │  Pinia Store │    │
│  │  生成器      │     │  (100ms轮询) │     │              │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                      │           │
│                                                      ▼           │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      前端组件                                   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │ │
│  │  │ 3D场景   │  │ ECharts  │  │ 报警面板 │  │ 设备面板 │       │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、功能模块详细设计

### 3.1 模块清单

| 模块ID | 模块名称 | 优先级 | 工作量 | 依赖 |
|--------|----------|--------|--------|------|
| M01 | 精细3D建模 | P0 | 2周 | - |
| M02 | Mock数据系统 | P0 | 1周 | - |
| M03 | 设备交互 | P0 | 2周 | M01, M02 |
| M04 | 物料追踪 | P1 | 2周 | M02, M03 |
| M05 | 报警管理 | P1 | 1周 | M02 |
| M06 | 仿真推演 | P2 | 2周 | M03, M04 |
| M07 | 报表中心 | P2 | 1周 | M02, M04 |

### 3.2 M01: 精细3D建模

#### 3.2.1 模型清单

| 设备ID | 设备名称 | 模型类型 | 精细度 | 备注 |
|--------|----------|----------|--------|------|
| R-101 | 反应釜 | 反应器 | 高 | 含搅拌器内部结构 |
| TK-101 | 原料储罐A | 储罐 | 高 | 椭圆封头 |
| TK-102 | 原料储罐B | 储罐 | 高 | 椭圆封头 |
| TK-103 | 成品储罐 | 储罐 | 高 | 椭圆封头 |
| P-101 | 进料泵 | 泵 | 中 | 叶轮可见 |
| V-101 | 调节阀 | 阀门 | 中 | 可旋转手轮 |
| V-102 | 切断阀 | 阀门 | 中 | 可旋转手轮 |
| B-101 | 传送带 | 输送设备 | 高 | 皮带纹理 |
| E-101 | 换热器 | 换热设备 | 中 | 管束结构 |
| C-101 | 控制柜 | 电气设备 | 高 | 按钮指示灯 |

#### 3.2.2 材质规范

```javascript
const MATERIALS = {
  stainlessSteel: {
    color: 0xE8E8E8,
    roughness: 0.15,
    metalness: 0.95,
    envMapIntensity: 1.2
  },

  carbonSteel: {
    color: 0x707070,
    roughness: 0.4,
    metalness: 0.8
  },

  insulation: {
    color: 0x8B7355,
    roughness: 0.9,
    metalness: 0.1
  },

  safetyYellow: {
    color: 0xFFCC00,
    roughness: 0.5,
    metalness: 0.3,
    emissive: 0xFFCC00,
    emissiveIntensity: 0.1
  },

  statusRunning: {
    color: 0x36D399,
    emissive: 0x36D399,
    emissiveIntensity: 0.8
  },

  statusStopped: {
    color: 0x808080,
    emissive: 0x808080,
    emissiveIntensity: 0.2
  },

  statusAlarm: {
    color: 0xFF4757,
    emissive: 0xFF4757,
    emissiveIntensity: 1.0
  }
}
```

### 3.3 M02: Mock数据系统

#### 3.3.1 数据模拟策略

| 数据类型 | 模拟方式 | 更新频率 | 说明 |
|----------|----------|----------|------|
| 温度 | 随机游走 + 趋势 | 100ms | 带惯性延迟 |
| 压力 | 随机游走 + 限幅 | 100ms | 物理合理范围 |
| 液位 | 积分逻辑 | 200ms | 进料出料平衡 |
| 阀门 | 阶跃响应 | 500ms | 开度变化 |
| 流量 | 正弦波动 | 200ms | 带噪声 |
| 产量 | 累积计数 | 1000ms | 随时间递增 |

#### 3.3.2 数据点定义

```javascript
const DATA_POINTS = {
  'R-101.Temperature': {
    type: 'Float',
    unit: '°C',
    range: [0, 150],
    alarm: { high: 100, critical: 120 },
    initial: 75,
    variance: 2
  },
  'R-101.Pressure': {
    type: 'Float',
    unit: 'MPa',
    range: [0, 2.0],
    alarm: { high: 1.5, critical: 1.8 },
    initial: 1.0,
    variance: 0.1
  },
  'R-101.Level': {
    type: 'Float',
    unit: '%',
    range: [0, 100],
    alarm: { low: 20, high: 90 },
    initial: 65,
    variance: 1
  },
  'R-101.AgitationSpeed': {
    type: 'Integer',
    unit: 'RPM',
    range: [0, 1500],
    initial: 800,
    variance: 10
  },

  'TK-101.Level': { type: 'Float', unit: '%', range: [0, 100], initial: 80, variance: 0.5 },
  'TK-102.Level': { type: 'Float', unit: '%', range: [0, 100], initial: 60, variance: 0.5 },
  'TK-103.Level': { type: 'Float', unit: '%', range: [0, 100], initial: 40, variance: 0.5 },

  'V-101.Position': { type: 'Integer', unit: '%', range: [0, 100], initial: 50, variance: 0 },
  'V-102.Position': { type: 'Integer', unit: '%', range: [0, 100], initial: 80, variance: 0 },

  'B-101.Speed': { type: 'Float', unit: 'm/min', range: [0, 50], initial: 30, variance: 1 },
  'B-101.Products': { type: 'Integer', unit: 'pcs', range: [0, 9999], initial: 0, variance: 0 }
}
```

### 3.4 M03: 设备交互

#### 3.4.1 交互类型

| 交互类型 | 设备 | 操作 | 反馈 |
|----------|------|------|------|
| 点击选择 | 所有设备 | 左键单击 | 高亮+弹出详情面板 |
| 参数查看 | 所有设备 | 详情面板 | 实时数据显示 |
| 远程控制 | 阀门、电机 | 面板操作 | 状态变化动画 |
| 视角聚焦 | 所有设备 | 右键菜单 | 相机移动到设备 |
| 趋势查看 | 测量仪表 | 详情面板 | 历史曲线图 |

#### 3.4.2 设备详情面板结构

```
┌─────────────────────────────────────────────────────────┐
│  [图标] R-101 反应釜                            [×]    │
├─────────────────────────────────────────────────────────┤
│  实时数据                                      操作人员：张三  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                │
│  │ 温度     │ │ 压力     │ │ 液位     │                │
│  │ 78.5 °C  │ │ 1.2 MPa  │ │ 65.3 %   │                │
│  │ ▲ +0.2   │ │ ● 正常   │ │ ▼ -1.2   │                │
│  └──────────┘ └──────────┘ └──────────┘                │
├─────────────────────────────────────────────────────────┤
│  控制面板                                      [授权操作]   │
│  ┌──────────────────────────────────────────────┐     │
│  │ 搅拌速度  [═══════●═══] 800 RPM              │     │
│  └──────────────────────────────────────────────┘     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  [启动]  │  │  [停止]  │  │  [复位]  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
├─────────────────────────────────────────────────────────┤
│  趋势曲线                              [1小时] [24小时]   │
│  ┌──────────────────────────────────────────────┐     │
│  │     ╱╲    ╱╲                                   │     │
│  │    ╱  ╲  ╱  ╲  ╱╲                             │     │
│  │ ──╱────╲╱────╲╱──                             │     │
│  └──────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────┤
│  报警历史                                                  │
│  ┌──────────────────────────────────────────────┐     │
│  │ 🔴 10:23:45  温度超限 78.5°C > 75°C  [未确认] │     │
│  │ 🟡 09:15:30  液位低报 15.2% < 20%     [已确认] │     │
│  └──────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 3.5 M04: 物料追踪

#### 3.5.1 物料批次模型

```typescript
interface MaterialLot {
  id: string;
  materialId: string;
  materialName: string;
  quantity: number;
  unit: string;
  status: LotStatus;
  source: string;
  currentLocation: string;
  batchDate: Date;
  expiryDate?: Date;
  quality: QualityResult;
  history: LocationHistory[];
  attributes: Record<string, any>;
}

enum LotStatus {
  IN_TRANSIT = 'in_transit',
  STORED = 'stored',
  IN_PROCESS = 'in_process',
  QC_PENDING = 'qc_pending',
  QC_PASSED = 'qc_passed',
  QC_REJECTED = 'qc_rejected',
  COMPLETED = 'completed',
  SCRAPPED = 'scrapped'
}
```

#### 3.5.2 工艺流程定义

```
原料入库 ──► 原料检验 ──► 备料 ──► 混合反应 ──► 冷却 ──► 过滤 ──► 成品
   │            │           │         │          │        │       │
   ▼            ▼           ▼         ▼          ▼        ▼       ▼
TANK-101    QC-101      P-101      R-101      E-101    F-101   TK-103
                                              │
                                              ▼
                                          B-101 ──► 包装 ──► 出库
```

### 3.6 M05: 报警管理

#### 3.6.1 报警等级

| 等级 | 名称 | 颜色 | 声音 | 处理时限 | 示例 |
|------|------|------|------|----------|------|
| 5 | 紧急 | 红色闪烁 | 持续 | 即时 | 泄漏、火灾 |
| 4 | 严重 | 红色 | 1次 | 5分钟 | 温度>120°C |
| 3 | 警告 | 橙色 | - | 15分钟 | 温度>100°C |
| 2 | 注意 | 黄色 | - | 1小时 | 液位<30% |
| 1 | 提示 | 蓝色 | - | 班次 | 维护到期 |

#### 3.6.2 报警处理流程

```
触发 ──► 推送 ──► 确认 ──► 处理 ──► 记录 ──► 分析
 │       │        │        │        │        │
 ▼       ▼        ▼        ▼        ▼        ▼
报警    声音    操作员    现场     记录     根因
产生    弹窗    确认     处理     日志     分析
                 │        │
                 ▼        ▼
              转移   ──► 升级
              处理
```

### 3.7 M06: 仿真推演

#### 3.7.1 仿真场景类型

| 场景 | 描述 | 用途 | 复杂度 |
|------|------|------|--------|
| 正常工况 | 额定参数运行 | 培训 | 低 |
| 启停操作 | 开停车步骤 | SOP培训 | 中 |
| 故障注入 | 模拟各类故障 | 应急演练 | 高 |
| 参数优化 | 调整参数观察效果 | 工艺优化 | 中 |
| 产能分析 | 不同工况产能 | 规划分析 | 中 |

#### 3.7.2 故障模型

```typescript
interface FaultScenario {
  id: string;
  name: string;
  description: string;
  affectedEquipment: string[];
  faultType: FaultType;
  symptoms: Symptom[];
  sequence: FaultEvent[];
  requiredActions: Action[];
  expectedDuration: number;
}

enum FaultType {
  EQUIPMENT_FAILURE = 'equipment_failure',
  SENSOR_DRIFT = 'sensor_drift',
  BLOCKAGE = 'blockage',
  OVERLOAD = 'overload',
  LEAK = 'leak',
  CONTROL_FAILURE = 'control_failure'
}
```

---

## 四、实施计划

### 4.0 战略定位：演示级精品策略

**核心理念**：不追求大而全，追求**小而精、亮点多、体验好**

```
┌─────────────────────────────────────────────────────────────────┐
│                    演示级精品策略                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   放弃 ❌                    聚焦 ✅                              │
│   ├─ 复杂的物料批次追踪      ├─ 设备点击交互 + 详情面板          │
│   ├─ 完整的故障仿真引擎      ├─ 实时报警 + 确认处理流程          │
│   ├─ 多用户协作系统          ├─ 精细3D模型 + PBR材质            │
│   └─ 报表生成系统            └─ 流畅动画 + 粒子特效              │
│                                                                  │
│   目标：4-6周打造一个"让人眼前一亮"的数字孪生演示系统             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.1 阶段划分

| 阶段 | 名称 | 时间 | 目标 |
|------|------|------|------|
| **Phase 0** | 架构完善与性能优化 | 0.5周 | 修复已知问题，完善基础设施 |
| **Phase 1** | 设备交互 + 报警系统 | 2周 | 核心演示功能 |
| **Phase 2** | 精细3D + 视觉效果 | 2周 | 视觉冲击力 |
| **Phase 3** | 优化与上线 | 1周 | 流畅体验，GitHub Pages发布 |

**总工期：5.5周（约1个半月）**

---

## 四、详细任务分解

### Phase 0: 架构完善与性能优化 (0.5周)

```
Phase 0: 架构完善与性能优化
│
├── T0.1 性能问题修复
│   ├── 修复Plant3D阴影配置（4096→2048）
│   ├── 实现autoUpdate=false手动控制
│   ├── 添加脏检查渲染优化
│   └── 验证：FPS稳定 > 30
│
├── T0.2 创建Composables基础设施
│   ├── 创建 src/composables/useThree.ts
│   ├── 创建 src/composables/useECharts.ts
│   ├── 创建 src/composables/useInterval.ts
│   └── 创建 src/composables/useRAF.ts
│
├── T0.3 完善Pinia Stores
│   ├── alarmStore (从plantStore拆分)
│   ├── plcStore完善
│   └── perfStore创建
│
└── T0.4 里程碑: 架构稳定，无明显性能问题
```

**T0.1 性能问题修复详细方案**（基于性能优化专项文档）：

```javascript
// Plant3D.js 优化配置
setupLights() {
  // ... 主方向光配置
  mainLight.shadow.mapSize.width = 2048   // 4096 → 2048
  mainLight.shadow.mapSize.height = 2048  // 4096 → 2048
  // ... 其他配置
}

// 添加手动阴影更新
renderer.shadowMap.autoUpdate = false  // 手动控制

// 脏检查渲染
let needsShadowUpdate = false
function markShadowDirty() { needsShadowUpdate = true }

// 在animate中
if (needsShadowUpdate) {
  renderer.shadowMap.update()
  needsShadowUpdate = false
}
```

**T0.2 Composables创建**（基于composables规范文档）：

| 文件 | 职责 | 优先级 |
|------|------|--------|
| useThree.ts | Three.js场景封装 | P0 |
| useECharts.ts | ECharts封装+高频优化 | P0 |
| useInterval.ts | 定时器封装 | P0 |
| useRAF.ts | requestAnimationFrame封装 | P1 |
| usePlantData.ts | 工厂数据订阅 | P1 |
| useAlarm.ts | 报警管理 | P1 |

---

### Phase 1: 设备交互 + 报警系统 (2周)

```
Phase 1: 设备交互 + 报警系统
│
├── T1.1 设备点击交互
│   ├── Raycaster点击检测
│   ├── 设备高亮效果（选中时）
│   ├── 设备聚焦动画（相机移动）
│   └── 点击空白取消选择
│
├── T1.2 设备详情面板
│   ├── 弹出动画效果
│   ├── 实时数据展示
│   ├── 趋势曲线图（ECharts）
│   └── 操作按钮（启动/停止/复位）
│
├── T1.3 报警系统完善
│   ├── 报警等级定义（5级）
│   ├── 报警触发逻辑
│   ├── 报警声音提醒
│   ├── 报警闪烁效果
│   └── 报警确认流程
│
├── T1.4 控制功能
│   ├── 阀门开度控制
│   ├── 电机启停控制
│   └── 参数调节滑块
│
└── T1.5 里程碑: 核心交互功能完整
```

**T1.1 设备点击交互详细设计**（基于组件规范文档）：

```vue
<!-- 设备详情面板示例 -->
<template>
  <Transition name="panel">
    <div v-if="selectedDevice" class="device-panel">
      <div class="device-panel__header">
        <span class="device-icon">{{ getDeviceIcon() }}</span>
        <span class="device-name">{{ selectedDevice.name }}</span>
        <button class="close-btn" @click="closePanel">×</button>
      </div>

      <div class="device-panel__body">
        <!-- 实时数据 -->
        <div class="data-grid">
          <div v-for="item in displayData" :key="item.key" class="data-item">
            <span class="data-item__label">{{ item.label }}</span>
            <span class="data-item__value">{{ item.value }}</span>
            <span class="data-item__trend" :class="item.trendClass">
              {{ item.trend }}
            </span>
          </div>
        </div>

        <!-- 趋势图 -->
        <div class="chart-container">
          <RealtimeChart :data="historyData" :height="150" />
        </div>

        <!-- 控制面板 -->
        <div class="control-section" v-if="isControllable">
          <div class="control-slider">
            <label>{{ controlParam.label }}</label>
            <input type="range" v-model="controlValue" />
            <span>{{ controlValue }}{{ controlParam.unit }}</span>
          </div>
          <div class="control-buttons">
            <button @click="sendCommand('start')">启动</button>
            <button @click="sendCommand('stop')">停止</button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>
```

**T1.3 报警系统设计**（基于架构设计文档alarmStore）：

```javascript
// 报警等级定义
const ALARM_LEVELS = {
  5: { name: '紧急', color: '#FF0000', sound: true, flash: true },
  4: { name: '严重', color: '#FF4757', sound: true, flash: false },
  3: { name: '警告', color: '#FF9F43', sound: false, flash: false },
  2: { name: '注意', color: '#Feca57', sound: false, flash: false },
  1: { name: '提示', color: '#54a0ff', sound: false, flash: false }
}

// 报警触发器配置（基于升级方案M02数据模拟）
const ALARM_RULES = [
  { id: 'A001', device: 'R-101', param: 'Temperature', high: 100, critical: 120, level: 3 },
  { id: 'A002', device: 'R-101', param: 'Pressure', high: 1.5, critical: 1.8, level: 4 },
  { id: 'A003', device: 'R-101', param: 'Level', low: 20, high: 90, level: 2 },
  { id: 'A004', device: 'TK-101', param: 'Level', low: 10, level: 3 },
  { id: 'A005', device: 'TK-102', param: 'Level', high: 95, level: 3 }
]
```

---

### Phase 2: 精细3D + 视觉效果 (2周)

```
Phase 2: 精细3D + 视觉效果
│
├── T2.1 PBR材质升级
│   ├── 不锈钢材质优化（envMap）
│   ├── 保温层材质（凹凸贴图）
│   ├── 玻璃材质（透明+反射）
│   ├── 设备状态材质（发光效果）
│   └── 安全标识材质
│
├── T2.2 灯光效果升级
│   ├── 环境光遮蔽（SSAO）
│   ├── 体积光效果（God Rays）
│   ├── 设备局部照明
│   └── 后期处理调色
│
├── T2.3 粒子特效升级
│   ├── 管道流体粒子
│   ├── 烟雾/蒸汽特效
│   ├── 火花/液滴特效
│   └── 产品传送动画
│
├── T2.4 场景氛围
│   ├── 天气效果（可选）
│   ├── 昼夜循环（可选）
│   ├── 背景音乐（可选）
│   └── 工业环境音
│
└── T2.5 里程碑: 视觉效果达到专业级
```

**T2.1 PBR材质配置**（基于升级方案3.2.2材质规范）：

```javascript
// 材质库配置
const MATERIALS = {
  // 不锈钢 - 工业设备主材质
  stainlessSteel: {
    color: 0xE8E8E8,
    roughness: 0.15,
    metalness: 0.95,
    envMapIntensity: 1.2,
    normalScale: new THREE.Vector2(0.3, 0.3)  // 凹凸细节
  },

  // 保温层 - 储罐/管道
  insulation: {
    color: 0x8B7355,
    roughness: 0.9,
    metalness: 0.1,
    bumpMap: 'textures/insulation_bump.jpg'  // 纹理细节
  },

  // 玻璃观察窗
  glass: {
    color: 0x88ccff,
    transparent: true,
    opacity: 0.3,
    roughness: 0.05,
    metalness: 0.3,
    envMapIntensity: 1.5
  },

  // 状态运行 - 绿色发光
  statusRunning: {
    color: 0x36D399,
    emissive: 0x36D399,
    emissiveIntensity: 0.8,
    roughness: 0.3,
    metalness: 0.5
  },

  // 状态停止
  statusStopped: {
    color: 0x808080,
    emissive: 0x808080,
    emissiveIntensity: 0.2,
    roughness: 0.5,
    metalness: 0.3
  },

  // 状态报警 - 红色闪烁
  statusAlarm: {
    color: 0xFF4757,
    emissive: 0xFF4757,
    emissiveIntensity: 1.0,
    roughness: 0.2,
    metalness: 0.5
  },

  // 安全黄色标识
  safetyYellow: {
    color: 0xFFCC00,
    roughness: 0.5,
    metalness: 0.3,
    emissive: 0xFFCC00,
    emissiveIntensity: 0.1
  }
}
```

**T2.2 后期处理配置**（基于性能优化专项文档）：

```javascript
// PostProcessing配置
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js'
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js'
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'

setupPostProcessing() {
  this.composer = new EffectComposer(this.renderer)

  // 基础渲染
  const renderPass = new RenderPass(this.scene, this.camera)
  this.composer.addPass(renderPass)

  // 抗锯齿（性能友好）
  const smaaPass = new SMAAPass(
    this.container.clientWidth,
    this.container.clientHeight
  )
  this.composer.addPass(smaaPass)

  // 发光效果（仅限重要设备）
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(this.container.clientWidth, this.container.clientHeight),
    0.5,   // strength
    0.4,   // radius
    0.85   // threshold
  )
  this.composer.addPass(bloomPass)

  // 输出
  const outputPass = new OutputPass()
  this.composer.addPass(outputPass)
}
```

---

### Phase 3: 优化与上线 (1周)

```
Phase 3: 优化与上线
│
├── T3.1 性能优化
│   ├── LOD分级（视距优化）
│   ├── 帧率稳定测试
│   ├── 内存泄漏检查
│   └── 加载速度优化
│
├── T3.2 GitHub Pages部署
│   ├── Vite配置检查
│   ├── CI/CD流程验证
│   ├── 域名/自定义域名
│   └── 性能监控
│
├── T3.3 演示内容完善
│   ├── 演示引导流程
│   ├── 功能说明卡片
│   └── 截图/录屏准备
│
└── T3.4 里程碑: 稳定上线
```

---

## 五、验收标准

### 5.1 功能验收

| 功能模块 | 验收条件 | 完成标准 |
|----------|----------|----------|
| **设备交互** | 点击设备弹出详情面板 | 响应 < 300ms，动画流畅 |
| **报警系统** | 模拟超限时报警触发 | 声音+闪烁+弹窗，流程完整 |
| **控制功能** | 阀门/电机可远程控制 | 状态反馈及时 |
| **3D展示** | 场景渲染精美 | FPS > 30，材质真实 |
| **粒子特效** | 流体/烟雾动画 | 视觉冲击力强 |

### 5.2 性能指标

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| 首屏加载 | < 5秒 | Lighthouse |
| 3D场景帧率 | > 30 FPS | Three.js Stats |
| 数据更新延迟 | < 100ms | Performance API |
| 设备点击响应 | < 300ms | 体感测试 |
| 内存占用 | < 500MB | Chrome DevTools |

### 5.3 演示效果标准

```
┌─────────────────────────────────────────────────────────────────┐
│                    演示效果检查清单                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✅ 3D场景打开即震撼，材质精细                                    │
│  ✅ 设备点击交互流畅，详情面板精美                               │
│  ✅ 报警系统完整，声音+视觉效果到位                              │
│  ✅ 控制功能可用，反馈及时                                        │
│  ✅ 无明显性能问题，加载流畅                                      │
│  ✅ GitHub Pages访问稳定                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 六、技术规范执行清单

### 6.1 代码规范执行（代码规范.md）

- [ ] 组件使用 `<script setup>` 组合式API
- [ ] Props使用 `defineProps` 详细定义
- [ ] Emit使用 `defineEmits` 验证
- [ ] 样式使用 BEM 命名 + scoped
- [ ] 常量使用 UPPER_SNAKE_CASE
- [ ] 禁止 console.log（生产环境）

### 6.2 组件规范执行（组件规范.md）

| 组件 | 规范 |
|------|------|
| 设备详情面板 | 按规范创建，使用Slots |
| 报警面板 | 5级颜色+声音+闪烁 |
| 实时图表 | 使用ECharts，manual-update模式 |
| 控制组件 | BEM命名，状态反馈 |

### 6.3 Composables规范执行（composables规范.md）

| 文件 | 状态 | 用途 |
|------|------|------|
| useThree.ts | 待创建 | 3D场景封装 |
| useECharts.ts | 待创建 | 图表封装+高频优化 |
| useInterval.ts | 待创建 | 定时器封装 |
| useRAF.ts | 待创建 | RAF封装 |
| usePlantData.ts | 待创建 | 数据订阅 |
| useAlarm.ts | 待创建 | 报警管理 |

### 6.4 GitHub Pages优化执行（GitHubPages优化.md）

- [ ] vite.config.js base路径 `/ScadaDemo/`
- [ ] 代码分割（three/echarts分开）
- [ ] 路由懒加载
- [ ] 模型Draco压缩
- [ ] 骨架屏Loading

### 6.5 性能优化执行（性能优化专项.md）

- [ ] 阴影地图 2048×2048
- [ ] autoUpdate = false 手动控制
- [ ] ECharts manual-update模式
- [ ] shallowRef 大数据量
- [ ] dispose资源清理

---

## 七、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 3D性能不足 | 演示卡顿 | 降级LOD，关闭后期处理 |
| 报警声音无法播放 | 功能缺失 | 使用Web Audio API，添加静音选项 |
| GitHub Pages加载慢 | 用户流失 | 代码分割，模型压缩，CDN |
| 跨浏览器兼容 | 显示异常 | Chrome/Firefox/Safari测试 |
| 触控交互不支持 | 移动端体验差 | 添加触摸事件，简化移动端UI |

---

## 八、资源估算

### 8.1 人力需求

| 角色 | 工作量 | 说明 |
|------|--------|------|
| 前端开发 | 5.5周 | 全栈开发 |
| 3D美术 | 1周 | 材质/特效指导 |
| 测试 | 0.5周 | 验收测试 |

### 8.2 技术栈清单

| 类别 | 技术 | 用途 |
|------|------|------|
| 框架 | Vue 3.4+ | 前端框架 |
| 构建 | Vite 5.0+ | 构建工具 |
| 状态 | Pinia 2.1+ | 状态管理 |
| 3D | Three.js 0.160+ | WebGL渲染 |
| 图表 | ECharts 5.4+ | 数据可视化 |
| 样式 | SCSS + CSS Variables | 主题样式 |
| 部署 | GitHub Pages | 静态托管 |

---

**文档状态**: 已更新 v1.2
**下次更新**: 待用户确认后更新
**版本历史**:
- v1.0 (2026-04-23): 初始版本
- v1.1 (2026-04-24): 调整为纯前端方案（方案1），移除后端相关任务
- v1.2 (2026-04-24): 重新规划为"演示级精品策略"，5.5周实施计划，聚焦设备交互+报警+视觉效果
