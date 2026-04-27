# SCADA数字孪生系统 - Phase 4/5 补全实施计划

> 文档版本: v1.0
> 创建日期: 2026-04-27
> 状态: 待执行

---

## 一、问题诊断

### 1.1 代码审查发现的问题

| 问题 | 严重程度 | 影响 | 现状 |
|------|----------|------|------|
| MaterialTracker 未集成到 Plant3D | 🔴 严重 | 物料3D动画不可见 | Phase 3 只有框架 |
| 仿真无物理模型循环 | 🔴 严重 | 故障注入后数值不变 | Phase 4 只有30% |
| 仿真与3D场景隔离 | 🟡 中等 | 看不到设备状态变化 | Phase 4 只有30% |
| 无预置培训场景 | 🟡 中等 | 只能手动注入故障 | Phase 4 只有30% |

### 1.2 各Phase完成度评估

| Phase | 完成度 | 说明 |
|-------|--------|------|
| Phase 0 | 90% | 架构完整 |
| Phase 1 | 95% | 3D建模完整 |
| Phase 2 | 90% | 交互功能完整 |
| Phase 3 | 60% | 缺少3D集成 |
| Phase 4 | 30% | 只有框架 |
| Phase 5 | 90% | 集成完成 |

---

## 二、解决方案

### 2.1 解决方案总览

| 问题 | 解决方案 | 技术依据 |
|------|----------|----------|
| MaterialTracker 未集成 | 在 Plant3D 初始化时创建 MaterialTracker 实例 | 架构设计.md §2.3 |
| 无物理模型循环 | 添加 updatePhysics() 方法实现热量积累、压力变化等 | 架构设计.md §4.1, 性能优化.md §6.1 |
| 仿真与3D隔离 | 在 simulationStore 中添加强制同步方法 syncToPlantStore | 架构设计.md §3.1 |
| 无预置培训场景 | 添加 PRESET_SCENARIOS 配置并实现 loadScenario() | 架构设计.md §4.1 |

---

## 三、实施计划

### 3.1 任务拆解

```
P0 - 紧急（影响核心功能）
├── T1.1: 集成 MaterialTracker 到 Plant3D
│   ├── 修改 Plant3D.js，导入 MaterialTracker
│   ├── 在 initScene 中创建实例
│   └── 在 animate 循环中调用 updateAnimations
│
├── T1.2: 验证物料3D动画显示
│   ├── 检查 MaterialTracker.updateLotMesh
│   └── 验证 animate 循环调用
│
P1 - 重要（核心功能）
├── T2.1: 添加物理模型 updatePhysics
│   ├── 温度模型：热量积累 formula: T += rate * dt
│   ├── 压力模型：压力积累 formula: P += rate * dt
│   ├── 液位模型：进料 - 出料 formula: L += (in - out) * dt
│   └── 故障影响：数值持续变化
│
├── T2.2: 实现仿真循环 tick()
│   ├── 使用 requestAnimationFrame
│   ├── 100ms 间隔更新（节流控制）
│   └── recordState() 状态录制
│
├── T2.3: 添加预置培训场景
│   ├── basic_operation: 基础操作训练
│   ├── emergency_response: 故障应急处理
│   └── loadScenario() 场景加载方法
│
├── T2.4: 仿真数据同步到 plantStore
│   ├── syncToPlantStore() 强制同步方法
│   └── 在 SimulationView 中调用
│
P2 - 建议（优化项）
├── T3.1: 添加脏检查优化渲染
│   ├── needsUpdate 标记
│   └── 按需渲染
│
└── T3.2: 添加 useRAF/useInterval
    ├── useRAF.ts
    └── useInterval.ts
```

### 3.2 执行顺序

```
T1.1 MaterialTracker集成
    ↓
T1.2 验证显示
    ↓
T2.1 物理模型
    ↓
T2.2 仿真循环 ────┐
    ↓            │
T2.3 预置场景    │ (可并行)
    ↓            │
T2.4 数据同步 ────┘
    ↓
T3.1 脏检查优化
    ↓
T3.2 Composables
```

### 3.3 时间估算

| 任务 | 工作量 | 优先级 |
|------|--------|--------|
| T1.1 + T1.2 | 2小时 | P0 |
| T2.1 + T2.2 | 4小时 | P1 |
| T2.3 | 2小时 | P1 |
| T2.4 | 2小时 | P1 |
| T3.1 | 1小时 | P2 |
| T3.2 | 2小时 | P2 |
| **总计** | **13小时** | - |

---

## 四、技术方案

### 4.1 MaterialTracker 集成

**目标**：让物料3D动画在 Plant3D 场景中可见

**修改文件**：`src/three/Plant3D.js`

```javascript
// 1. 导入
import MaterialTracker from './material/MaterialTracker'

class Plant3D {
  constructor() {
    // ... 其他初始化
    this.materialTracker = null
  }

  initScene() {
    // ... 现有初始化代码

    // 2. 初始化 MaterialTracker
    this.materialTracker = new MaterialTracker(this.scene)
  }

  animate() {
    // ... 其他更新

    // 3. 更新物料动画（按需渲染优化）
    if (this.needsUpdate && this.materialTracker) {
      this.materialTracker.updateAnimations()
    }
  }

  dispose() {
    // ... 其他清理

    // 4. 清理 MaterialTracker
    if (this.materialTracker) {
      this.materialTracker.dispose()
    }
  }
}
```

### 4.2 物理模型

**目标**：让设备指标根据物理规律动态变化

**修改文件**：`src/mock/simulationEngine.js`

```javascript
class SimulationEngine {
  constructor() {
    // ... 现有属性
    this.lastUpdate = 0
    this.updateInterval = 100  // 100ms
    this.isSimulating = false
  }

  // 物理模型更新
  updatePhysics(deltaTime) {
    this.equipment.forEach(eq => {
      // ===== 温度模型 =====
      // 热量积累：运行中温度逐渐上升
      if (eq.state === EquipmentState.RUNNING && !eq.isFaulty) {
        // 每秒上升0.1度，有热损耗
        const heatGain = 0.1 * (deltaTime / 1000)
        const heatLoss = (eq.metrics.temperature - 25) * 0.01 * (deltaTime / 1000)
        eq.metrics.temperature += heatGain - heatLoss
        eq.metrics.temperature = Math.max(25, Math.min(eq.settings.tempMax, eq.metrics.temperature))
      }

      // 故障影响：温度持续上升
      if (eq.activeFault?.type === FaultType.TEMPERATURE_HIGH) {
        eq.metrics.temperature += 0.5 * (deltaTime / 1000)
        if (eq.metrics.temperature > 120) {
          this.injectFault(eq.id, 'PRESSURE_HIGH', FaultSeverity.CRITICAL)
        }
      }

      // ===== 压力模型 =====
      if (eq.state === EquipmentState.RUNNING && !eq.isFaulty) {
        const pressureGain = 0.05 * (deltaTime / 1000)
        const pressureLoss = (eq.metrics.pressure - 1.0) * 0.02 * (deltaTime / 1000)
        eq.metrics.pressure += pressureGain - pressureLoss
        eq.metrics.pressure = Math.max(0.5, Math.min(eq.settings.pressureMax, eq.metrics.pressure))
      }

      // ===== 液位模型 =====
      if (eq.state === EquipmentState.RUNNING && !eq.isFaulty) {
        const inflow = eq.settings.flowMax * 0.8
        const outflow = eq.settings.flowMin * 0.3
        eq.metrics.level += (inflow - outflow) * 0.01 * (deltaTime / 1000)
        eq.metrics.level = Math.max(0, Math.min(100, eq.metrics.level))
      }

      // ===== 流量模型 =====
      if (eq.state === EquipmentState.RUNNING && !eq.isFaulty) {
        eq.metrics.flow = eq.settings.flowMax * (0.8 + Math.sin(Date.now() / 1000) * 0.2)
      }
    })
  }

  // 仿真循环
  tick(timestamp) {
    if (!this.isSimulating) return

    if (this.lastUpdate === 0) this.lastUpdate = timestamp
    const deltaTime = timestamp - this.lastUpdate

    if (deltaTime >= this.updateInterval) {
      this.updatePhysics(deltaTime)
      this.recordState()
      this.notifyListeners('tick', { simulationTime: this.simulationTime })
      this.lastUpdate = timestamp
      this.simulationTime += deltaTime
    }

    requestAnimationFrame((t) => this.tick(t))
  }

  start() {
    this.isSimulating = true
    this.lastUpdate = 0
    requestAnimationFrame((t) => this.tick(t))
  }

  stop() {
    this.isSimulating = false
  }
}
```

### 4.3 预置培训场景

**目标**：提供可用的培训场景

**修改文件**：`src/mock/simulationEngine.js`

```javascript
const PRESET_SCENARIOS = {
  basic_operation: {
    id: 'basic_operation',
    name: '基础操作训练',
    description: '学习反应釜的启停操作',
    initialEquipment: {
      'R-101': { state: 'idle', metrics: { temperature: 25, pressure: 1.0, level: 50 } }
    },
    steps: [
      { title: '检查状态', description: '确认设备空闲', expectedAction: 'check', timeout: 10 },
      { title: '启动预热', description: '启动搅拌器', expectedAction: 'start', timeout: 30 },
      { title: '监控温度', description: '观察温度上升', expectedAction: 'monitor', timeout: 60 },
      { title: '正常停机', description: '逐步降温停机', expectedAction: 'stop', timeout: 45 }
    ],
    scoring: {
      responseTime: { max: 30, weight: 0.3 },
      accuracy: { weight: 0.5 },
      faultHandling: { weight: 0.2 }
    }
  },

  emergency_response: {
    id: 'emergency_response',
    name: '故障应急处理',
    description: '处理温度过高紧急情况',
    injectedFaults: [
      { equipmentId: 'R-101', type: 'TEMPERATURE_HIGH', severity: 'critical', delay: 5000 }
    ],
    steps: [
      { title: '发现报警', description: '温度超过80°C', expectedAction: 'check_alarm', timeout: 15 },
      { title: '确认故障', description: '检查设备状态', expectedAction: 'diagnose', timeout: 20 },
      { title: '采取行动', description: '停止设备', expectedAction: 'emergency_stop', timeout: 30 },
      { title: '记录报告', description: '填写事故报告', expectedAction: 'report', timeout: 45 }
    ],
    scoring: {
      responseTime: { max: 60, weight: 0.4 },
      accuracy: { weight: 0.4 },
      faultHandling: { weight: 0.2 }
    }
  }
}

// 加载预置场景
function loadScenario(scenarioId) {
  const scenario = PRESET_SCENARIOS[scenarioId]
  if (!scenario) return null

  // 设置初始设备状态
  Object.entries(scenario.initialEquipment).forEach(([id, config]) => {
    const eq = this.equipment.get(id)
    if (eq) {
      eq.state = config.state
      eq.metrics = { ...config.metrics }
    }
  })

  // 延迟注入故障
  if (scenario.injectedFaults) {
    scenario.injectedFaults.forEach(fault => {
      setTimeout(() => {
        this.injectFault(fault.equipmentId, fault.type, fault.severity)
      }, fault.delay)
    })
  }

  return scenario
}
```

### 4.4 数据同步

**目标**：让仿真数据与3D场景互通

**修改文件**：`src/stores/simulationStore.js`

```javascript
function syncToPlantStore() {
  const plantStore = usePlantStore()

  this.equipment.forEach(eq => {
    // 同步设备状态
    plantStore.updateDevice(eq.id, {
      temperature: eq.metrics.temperature,
      pressure: eq.metrics.pressure,
      level: eq.metrics.level,
      status: eq.state
    })
  })
}

// 在 simulationStore 中暴露
return {
  // ... 现有导出
  syncToPlantStore
}
```

---

## 五、规范依据

| 规范文档 | 引用章节 | 用途 |
|----------|----------|------|
| 架构设计.md | §2.3 目录结构 | MaterialTracker 集成位置 |
| 架构设计.md | §3.1 数据流 | 数据同步方案 |
| 架构设计.md | §4.1 PlantSimulator | 物理模型设计 |
| 性能优化.md | §3.1 脏检查 | 按需渲染优化 |
| 性能优化.md | §6.1 节流控制 | 仿真循环更新间隔 |

---

## 六、验证标准

### 6.1 MaterialTracker 集成验证

- [ ] Plant3D 初始化时创建 MaterialTracker 实例
- [ ] animate 循环中调用 updateAnimations
- [ ] 物料批次在3D场景中可见
- [ ] 物料移动时有动画效果

### 6.2 物理模型验证

- [ ] 设备运行时温度逐渐上升
- [ ] 故障注入后温度持续上升
- [ ] 设备运行时液位逐渐变化
- [ ] 设备运行时压力逐渐变化

### 6.3 预置场景验证

- [ ] 可加载 basic_operation 场景
- [ ] 可加载 emergency_response 场景
- [ ] 场景步骤可按顺序执行
- [ ] 场景结束可计算评分

### 6.4 数据同步验证

- [ ] 仿真数据可同步到 plantStore
- [ ] 3D场景可反映仿真设备状态
- [ ] 报警可触发设备状态变化

---

## 七、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 修改 Plant3D 影响现有功能 | 高 | 先备份，逐步验证 |
| 物理模型参数不合理 | 中 | 可配置参数，调整方便 |
| 与现有 PlantSimulator 冲突 | 中 | 区分两个模拟器职责 |

---

## 八、交付物

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `src/three/Plant3D.js` | 修改 | 集成 MaterialTracker |
| `src/mock/simulationEngine.js` | 修改 | 添加物理模型、预置场景 |
| `src/stores/simulationStore.js` | 修改 | 添加数据同步方法 |
| `docs/implementation_plan.md` | 新增 | 本文档 |

---

**文档状态**: 待执行
**下次更新**: 开始实施前确认
**版本历史**:
- v1.0 (2026-04-27): 初始版本
