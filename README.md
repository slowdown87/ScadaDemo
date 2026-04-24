# ScadaDemo - SCADA数字孪生系统

> 工业4.0数字孪生演示系统，基于Vue3 + Three.js + ECharts构建

[在线预览](https://slowdown87.github.io/ScadaDemo/) | [升级方案](./.trae/documents/SCADA数字孪生专业级升级方案.md)

---

## 功能特性

| 模块 | 说明 | 状态 |
|------|------|------|
| 工业组态 | SVG工艺流程监控 | ✅ 已完成 |
| 数字孪生 | Three.js 3D工厂可视化 | ✅ 已完成 |
| 性能监控 | ECharts实时数据面板 | ✅ 已完成 |
| 报警管理 | 实时报警与历史记录 | 🚧 进行中 |
| 物料追踪 | 批次管理与流程追踪 | 📋 规划中 |
| 仿真推演 | 故障注入与培训场景 | 📋 规划中 |

---

## 快速开始

### 环境要求

- Node.js >= 18
- npm >= 9

### 安装

```bash
npm install
```

### 开发

```bash
npm run dev
```

### 构建

```bash
npm run build
```

### 预览构建结果

```bash
npm run preview
```

---

## 项目结构

```
scada-demo/
├── src/
│   ├── assets/              # 静态资源（SVG、图片）
│   ├── components/          # Vue组件
│   │   ├── common/          # 公共组件
│   │   ├── plant/           # 工厂组件
│   │   └── charts/          # 图表组件
│   ├── mock/                # Mock数据
│   │   ├── plantMock.js     # 工厂数据模拟
│   │   ├── plcMock.js       # PLC数据模拟
│   │   └── highFreqMock.js  # 高频数据模拟
│   ├── router/              # 路由配置
│   ├── stores/               # Pinia状态管理
│   │   ├── plantStore.js    # 工厂数据状态
│   │   └── plcStore.js      # PLC数据状态
│   ├── three/                # Three.js模块
│   │   └── Plant3D.js       # 3D场景主模块
│   ├── views/                # 页面视图
│   ├── App.vue               # 根组件
│   └── main.js               # 入口文件
├── public/                   # 公共资源
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Pages部署
├── vite.config.js            # Vite配置
└── package.json
```

---

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue3 | 3.4+ |
| 构建 | Vite | 5.0+ |
| 状态 | Pinia | 2.1+ |
| 3D | Three.js | 0.160+ |
| 图表 | ECharts | 5.4+ |
| 路由 | Vue Router | 4.0+ |

---

## 文档

| 文档 | 说明 |
|------|------|
| [升级方案](./.trae/documents/SCADA数字孪生专业级升级方案.md) | 专业级升级路线图 |
| [任务清单](./.trae/documents/History/SCADA升级任务清单.md) | 详细任务分解 |
| [状态快照](./.trae/documents/History/状态快照.json) | 项目状态跟踪 |
| [开发日志](./.trae/documents/History/开发日志.md) | 开发历史记录 |

---

## 升级计划

当前版本为基础版，计划升级为专业级：

```
Phase 0: 架构搭建 (Week 1)
Phase 1: 基础3D+Mock数据 (Week 2-3)
Phase 2: 交互功能 (Week 4-5)
Phase 3: 物料追踪 (Week 6-7)
Phase 4: 仿真推演 (Week 8-9)
Phase 5: 系统集成 (Week 10)
```

详见 [SCADA数字孪生专业级升级方案](./.trae/documents/SCADA数字孪生专业级升级方案.md)

---

## 部署

项目使用GitHub Pages进行部署，每次推送到main分支会自动部署。

部署地址: https://slowdown87.github.io/ScadaDemo/

---

## 贡献

欢迎提交Issue和Pull Request。

---

## 许可

MIT
