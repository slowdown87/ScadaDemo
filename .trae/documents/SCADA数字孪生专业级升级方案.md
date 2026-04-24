# SCADA数字孪生系统 - 专业级升级方案

> 文档版本: v3.0
> 创建日期: 2026-04-24
> 更新日期: 2026-04-24
> 部署方案: 方案1 - 纯前端（GitHub Pages）
> GitHub仓库: https://github.com/slowdown87/ScadaDemo
> GitHub Pages: https://slowdown87.github.io/ScadaDemo/
> 状态快照: 状态快照.json (v2.3) 为准

---

## 一、项目愿景与目标

### 1.1 项目定位

打造一个**专业级工业数字孪生演示平台**，具备：

| 核心能力 | 当前状态 | 目标状态 |
|----------|---------|---------|
| 3D可视化 | 基础几何体+材质 | PBR材质+精细模型+LOD分级 |
| 数据采集 | Mock静态数据 | Mock动态模拟（随机游走+趋势） |
| 设备交互 | 仅查看 | 点击交互+控制操作 |
| 报警管理 | 颜色变化 | 完整报警系统（规则引擎+声音+视觉） |
| 物料追踪 | 无 | 端到端追踪+3D动画 |
| 仿真推演 | 无 | 故障注入+培训场景 |
| 性能指标 | 待优化 | 首屏<3s, FPS>30, 更新<100ms |

### 1.2 成功标准

| 指标 | 目标值 | 验证方式 | 优先级 |
|------|--------|----------|--------|
| 首屏加载 | < 4秒 | Lighthouse | P0 |
| 3D帧率 | > 30 FPS | PerfView监控 | P0 |
| 交互响应 | < 100ms | Performance API | P0 |
| Lighthouse性能分 | > 80 | Lighthouse CI | P1 |
| 模型加载 | < 3秒 | Network面板 | P1 |
| GitHub Pages | 可访问 | URL直接访问 | P0 |

### 1.3 技术栈

```
┌─────────────────────────────────────────────────────────────────┐
│                        浏览器环境                                  │
├─────────────────────────────────────────────────────────────────┤
│  Vue 3.4+ (Composition API + Pinia 2.1+)                         │
│    ├── Router 4.0+ (Hash Mode)                                  │
│    ├── Pinia 2.1+ (State Management)                            │
│    └── Components (SFC)                                         │
├─────────────────────────────────────────────────────────────────┤
│  Three.js 0.184+ (WebGL 3D)                                     │
│    ├── Scene / Camera / Renderer                                │
│    ├── Controls (OrbitControls)                                 │
│    ├── Lights / Materials / Meshes                              │
│    ├── EffectComposer (Post-processing)                         │
│    └── LOD (Level of Detail)                                    │
├─────────────────────────────────────────────────────────────────┤
│  ECharts 5.5+ (Charts)                                          │
│    ├── Line Chart (实时曲线)                                     │
│    ├── Gauge Chart (仪表盘)                                      │
│    └── manual-update模式                                         │
├─────────────────────────────────────────────────────────────────┤
│  构建与部署                                                     │
│    ├── Vite 5.0+ (Build Tool)                                    │
│    └── GitHub Pages (CI/CD)                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、阶段规划（以状态快照为准）

### 2.1 总体阶段划分

```
Phase 0: 架构搭建 (Week 1) ████████████████████ 85% → 100%
    │
    ▼
Phase 1: 基础3D建模+Mock数据 (Week 2-3) ░░░░░░░░░░░░░░░░░░░░░ 40%
    │
    ▼
Phase 2: 交互功能 (Week 4-5) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
    │
    ▼
Phase 3: 物料追踪 (Week 6-7) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
    │
    ▼
Phase 4: 仿真推演 (Week 8-9) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
    │
    ▼
Phase 5: 系统集成 (Week 10) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%
```

### 2.2 里程碑定义

| 里程碑 | 验收条件 | 状态 |
|--------|---------|------|
| Phase 0 里程碑 | 技术验证全部通过 + GitHub Pages可访问 | pending |
| Phase 1 里程碑 | 3D模型加载<3s + Mock数据实时更新无卡顿 | pending |
| Phase 2 里程碑 | 设备点击响应<500ms + 报警及时推送 | pending |
| Phase 3 里程碑 | 物料批次全流程追踪 + 3D动画流畅 | pending |
| Phase 4 里程碑 | 仿真场景可运行 + 培训流程完整 | pending |
| Phase 5 里程碑 | GitHub Pages可访问 + 性能指标达标 | pending |

---

## 三、Phase 0: 架构搭建（收尾阶段）

### 3.1 当前状态

**进度: 85%**

已完成:
- ✅ 文档体系完善（架构设计.md, 代码规范.md, 性能优化专项.md, composables规范.md, GitHubPages优化.md）
- ✅ Mock数据服务架构验证
- ✅ Three.js性能优化测试
- ✅ ECharts高频更新测试
- ✅ Vue Router Hash模式验证
- ✅ CI/CD流程配置
- ✅ Bug修复: alarmEngine数据不通
- ✅ Bug修复: RenderPass导入错误

待完成:
- ⏳ Phase 0 里程碑验收

### 3.2 收尾任务清单

| 任务 | 验收标准 | 优先级 |
|------|---------|--------|
| T0.4.1 构建验证 | `npm run build` 通过，无error | P0 |
| T0.4.2 GitHub Pages验证 | https://slowdown87.github.io/ScadaDemo/ 可访问 | P0 |
| T0.4.3 Lighthouse基线 | Performance > 70（基线测试） | P1 |
| T0.4.4 文档更新 | 状态快照.json更新Phase 0为completed | P2 |

### 3.3 验收检查清单

```markdown
## Phase 0 里程碑验收检查

### 基础设施
- [ ] npm run build 成功
- [ ] dist/ 目录正确生成
- [ ] vite.config.js base路径正确 (/ScadaDemo/)
- [ ] deploy.yml workflow正确配置

### 文档完整性
- [ ] 架构设计.md 存在且完整
- [ ] 代码规范.md 存在且完整
- [ ] 性能优化专项.md 存在且完整
- [ ] composables规范.md 存在且完整
- [ ] GitHubPages优化.md 存在且完整
- [ ] 状态快照.json 与实际一致

### 技术验证
- [ ] Three.js场景渲染正常
- [ ] ECharts图表显示正常
- [ ] Pinia stores工作正常
- [ ] Mock数据模拟正常
- [ ] 报警引擎工作正常
- [ ] 设备交互响应正常

### GitHub Pages
- [ ] GitHub Actions构建成功
- [ ] GitHub Pages部署成功
- [ ] URL可访问: https://slowdown87.github.io/ScadaDemo/
- [ ] 所有路由正常跳转（Hash模式）
```

---

## 四、Phase 1: 基础3D建模+Mock数据

### 4.1 目标

完成工厂3D场景搭建和Mock数据引擎，实现实时数据模拟。

### 4.2 任务分解

#### T1.1 3D模型完善

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T1.1.1 | R-101反应釜精细模型 | 圆底反应釜+搅拌器+液位指示器 | HIGH | pending |
| T1.1.2 | TK-101/102/103储罐模型 | 立式储罐+浮顶+液位计 | HIGH | pending |
| T1.1.3 | 管道系统模型 | 主管+支管+法兰+弯头 | HIGH | pending |
| T1.1.4 | 阀门V-101/V-102模型 | 球阀+开度指示 | MED | pending |
| T1.1.5 | 传送带B-101模型 | 框架+滚筒+传送带+产品 | MED | pending |

#### T1.2 材质与灯光

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T1.2.1 | 不锈钢PBR材质 | roughness: 0.3, metalness: 0.9 | HIGH | pending |
| T1.2.2 | 碳钢PBR材质 | roughness: 0.6, metalness: 0.7 | MED | pending |
| T1.2.3 | 设备状态材质 | 运行(绿)/停止(灰)/报警(红) | HIGH | pending |
| T1.2.4 | 工业照明模拟 | 区域照明+投光灯 | MED | pending |
| T1.2.5 | 动态阴影优化 | autoUpdate=false, 手动控制 | MED | pending |

#### T1.3 数据模拟引擎

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T1.3.1 | Mock数据服务验证 | 100ms间隔更新正常 | HIGH | pending |
| T1.3.2 | 实时数据更新 | 无卡顿，CPU<50% | HIGH | pending |
| T1.3.3 | 设备状态模拟 | 运行/停止/报警状态切换 | HIGH | pending |
| T1.3.4 | 报警数据生成 | 基于规则的报警触发 | HIGH | pending |

### 4.3 交付标准

- [ ] 3D场景加载时间 < 3秒
- [ ] Mock数据实时更新无卡顿（100ms间隔）
- [ ] 所有设备模型可正确显示
- [ ] PBR材质正确渲染（金属感+反射）
- [ ] 设备状态变化有视觉反馈
- [ ] Build通过，无错误

### 4.4 技术规范参考

**性能优化专项.md**:
- Three.js脏检查优化（T3.1节）
- PBR材质使用（T3.3节）
- 阴影优化配置（T3.6节）
- 内存管理规范（T5节）

**composables规范.md**:
- usePlantData封装（T4节）
- useRAF/useInterval高频更新（T6/T7节）

**代码规范.md**:
- 组件结构（T3.1节）
- 命名规范（T1节）

---

## 五、Phase 2: 交互功能

### 5.1 目标

实现设备点击交互、详情查看、控制操作和报警管理。

### 5.2 任务分解

#### T2.1 设备点击交互

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T2.1.1 | Raycaster点击检测 | 精确检测设备对象 | HIGH | pending |
| T2.1.2 | 设备高亮效果 | Hover时发光边缘 | HIGH | pending |
| T2.1.3 | 视角聚焦动画 | 双击设备，相机移动 | MED | pending |
| T2.1.4 | Group对象点击穿透 | 修复Group点击无效 | HIGH | pending |

#### T2.2 设备详情面板

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T2.2.1 | DevicePanel组件完善 | 数据显示+控制按钮 | HIGH | pending |
| T2.2.2 | 趋势曲线图集成 | ECharts实时曲线 | HIGH | pending |
| T2.2.3 | ECharts增量更新 | manual-update模式 | MED | pending |
| T2.2.4 | 控制按钮集成 | 启动/停止/调速 | HIGH | pending |

#### T2.3 报警系统

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T2.3.1 | 报警规则引擎完善 | 多规则+多阈值 | HIGH | pending |
| T2.3.2 | 报警确认处理 | 确认/全部确认 | HIGH | pending |
| T2.3.3 | 声音提醒 | 蜂鸣声（可开关） | MED | pending |
| T2.3.4 | 报警历史记录 | 最多100条 | MED | pending |

### 5.3 交付标准

- [ ] 设备点击可查看详情
- [ ] 控制操作响应 < 500ms
- [ ] 报警及时推送（< 1秒）
- [ ] 操作日志完整

### 5.4 技术规范参考

**性能优化专项.md**:
- ECharts manual-update模式（T2.1节）
- 数据采样（T2.2节）
- Vue响应式优化（T4节）

**组件规范.md**:
- 组件API设计（T4节）
- DataPanel组件规范（T5.1节）
- AlarmPanel组件规范（T5.2节）

---

## 六、Phase 3: 物料追踪

### 6.1 目标

实现物料批次全流程追踪和3D动画展示。

### 6.2 任务分解

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T3.1 | 批次数据结构设计 | 批次号+物料+位置+状态 | HIGH | pending |
| T3.2 | 状态机定义 | in_transit/stored/in_process等 | HIGH | pending |
| T3.3 | 位置更新服务 | 实时位置追踪 | HIGH | pending |
| T3.4 | 历史轨迹展示 | 轨迹线/热力图 | MED | pending |
| T3.5 | 物料3D动画 | 移动+旋转+缩放 | MED | pending |
| T3.6 | 工艺步骤配置 | SOP定义 | MED | pending |

### 6.3 交付标准

- [ ] 物料批次全流程追踪
- [ ] 3D动画流畅（> 30 FPS）
- [ ] 工艺步骤可配置

### 6.4 技术规范参考

**架构设计.md**:
- 物料批次数据模型（T3.2.3节）
- 状态机定义（T3.2.3节）

---

## 七、Phase 4: 仿真推演

### 7.1 目标

实现仿真引擎和培训场景。

### 7.2 任务分解

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T4.1 | 设备仿真模型 | 启停+故障模拟 | HIGH | pending |
| T4.2 | 故障注入机制 | 温度/压力/液位异常 | MED | pending |
| T4.3 | 场景编辑器 | 培训场景配置 | MED | pending |
| T4.4 | 播放/暂停/回溯 | 时间控制 | HIGH | pending |
| T4.5 | 培训SOP | 操作指导 | MED | pending |
| T4.6 | 评分系统 | 操作评估 | MED | pending |

### 7.3 交付标准

- [ ] 仿真场景可运行
- [ ] 培训流程完整
- [ ] 评估系统可用

---

## 八、Phase 5: 系统集成

### 8.1 目标

完成系统集成测试和GitHub Pages部署。

### 8.2 任务分解

| 任务 | 描述 | 验收标准 | 优先级 | 状态 |
|------|------|---------|--------|------|
| T5.1 | 模块集成 | 所有模块联调正常 | HIGH | pending |
| T5.2 | 数据流验证 | Mock→Store→UI数据流 | HIGH | pending |
| T5.3 | 渲染优化 | FPS>30, 内存稳定 | MED | pending |
| T5.4 | GitHub Pages发布 | 正式环境部署 | HIGH | pending |
| T5.5 | 最终验证 | Lighthouse>80 | HIGH | pending |

### 8.3 交付标准

- [ ] GitHub Pages可访问
- [ ] 性能指标达标（Lighthouse > 80）
- [ ] 演示功能完整

---

## 九、技术规范总览

### 9.1 性能优化（详见 性能优化专项.md）

| 优化项 | 策略 | 实现位置 |
|--------|------|---------|
| ECharts高频更新 | manual-update + 数据采样 | DevicePanel.vue |
| Three.js脏检查 | needsUpdate标志位 | Plant3D.js |
| 材质复用 | 共享MeshStandardMaterial | materials.js |
| 阴影优化 | autoUpdate=false + 手动更新 | Plant3D.js |
| LOD分级 | 距离分级模型加载 | 待实现 |
| Vue响应式 | shallowRef + v-memo | 组件级别 |
| 内存管理 | dispose清理 | Plant3D.js dispose() |

### 9.2 Composables规范（详见 composables规范.md）

| Composable | 用途 | 状态 |
|------------|------|------|
| useThree | Three.js场景管理 | ✅ 已实现 |
| usePlantData | 工厂数据获取 | ✅ 已实现 |
| useAlarm | 报警管理 | ✅ 已实现 |
| useECharts | ECharts封装 | ✅ 已实现 |
| useInterval | 定时器（页面隐藏问题） | ✅ 已实现 |
| useRAF | requestAnimationFrame封装 | ✅ 已实现 |

### 9.3 代码规范（详见 代码规范.md）

| 规范项 | 要求 |
|--------|------|
| 命名 | camelCase变量, PascalCase组件, UPPER_SNAKE_CASE常量 |
| CSS | kebab-case类名, BEM命名, CSS Variables |
| 组件 | Props定义, Emits定义, Composables使用 |
| Git | feat/fix/docs前缀, 原子化commit |

### 9.4 组件规范（详见 组件规范.md）

| 组件类型 | 命名规则 | 示例 |
|----------|---------|------|
| 页面组件 | XxxView.vue | TwinView.vue |
| 面板组件 | XxxPanel.vue | AlarmPanel.vue |
| 弹窗组件 | XxxPopup.vue | AlarmPopup.vue |
| 布局组件 | TheXxx.vue | TheHeader.vue |

### 9.5 GitHub Pages优化（详见 GitHubPages优化.md）

| 优化项 | 配置 |
|--------|------|
| 代码分割 | three/echarts单独chunk |
| 资源压缩 | Terser压缩, brotliSize |
| 模型压缩 | Draco压缩GLTF/GLB |
| 路由懒加载 | defineAsyncComponent |
| 缓存策略 | contenthash文件名 |

---

## 十、GitHub Pages部署验证

### 10.1 部署架构

```
GitHub Repository (slowdown87/ScadaDemo)
        │
        ▼
   main branch push
        │
        ▼
  GitHub Actions
     deploy.yml
        │
        ├── npm ci
        ├── npm run build
        │
        ▼
     dist/
        │
        ▼
  GitHub Pages
https://slowdown87.github.io/ScadaDemo/
```

### 10.2 CI/CD配置要求

根据 GitHubPages优化.md，deploy.yml必须包含：

```yaml
permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: true
```

### 10.3 部署前检查清单

- [ ] vite.config.js base路径: `/ScadaDemo/`
- [ ] vite.config.js 代码分割: three/echarts分开
- [ ] deploy.yml workflow存在且正确
- [ ] 模型文件总大小 < 50MB
- [ ] 构建产物总大小 < 100MB
- [ ] 所有资源使用相对路径或正确base路径

### 10.4 部署后验证清单

- [ ] GitHub Pages URL可访问
- [ ] 首页加载正常
- [ ] TwinView 3D场景正常
- [ ] 所有路由跳转正常（Hash模式）
- [ ] Lighthouse Performance > 80
- [ ] 无控制台Error

---

## 十一、文档清单

| 文档 | 路径 | 版本 | 状态 |
|------|------|------|------|
| SCADA数字孪生专业级升级方案.md | .trae/documents/ | v3.0 | ✅ |
| 状态快照.json | .trae/documents/ | v2.3 | ✅ |
| 架构设计.md | .trae/documents/ | v1.0 | ✅ |
| 代码规范.md | .trae/documents/ | v1.0 | ✅ |
| 组件规范.md | .trae/documents/ | v1.0 | ✅ |
| 性能优化专项.md | .trae/documents/ | v1.0 | ✅ |
| composables规范.md | .trae/documents/ | v1.0 | ✅ |
| GitHubPages优化.md | .trae/documents/ | v1.0 | ✅ |

---

## 十二、版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-04-23 | 初始版本 |
| v2.0 | 2026-04-24 | 以状态快照为准重写 |
| v3.0 | 2026-04-24 | 高标准版本，整合全部参考文档 |

---

**文档状态**: 正式版
**下次更新**: Phase 0验收完成后
**维护责任人**: AI Assistant
