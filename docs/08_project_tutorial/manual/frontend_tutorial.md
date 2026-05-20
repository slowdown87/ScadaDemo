# CIP SCADA 前端完整教程

## 目录

1. [前端是什么？](#1-前端是什么)
2. [技术栈介绍](#2-技术栈介绍)
3. [项目结构](#3-项目结构)
4. [核心概念](#4-核心概念)
5. [代码详解](#5-代码详解)
6. [启动项目](#6-启动项目)
7. [API通信](#7-api通信)
8. [状态管理](#8-状态管理)
9. [WebSocket实时通信](#9-websocket实时通信)
10. [项目实战练习](#10-项目实战练习)
11. [调试方法](#11-调试方法)
12. [常见问题](#12-常见问题)
13. [术语表](#13-术语表)
14. [学习路径建议](#14-学习路径建议)

---

## 1. 前端是什么？

### 1.1 生活中的比喻

想象你去银行办事：

```
你（用户）→ 银行柜员（前端）→ 后台系统（后端+PLC）
```

- **你** → 操作界面："我要查看账户余额"
- **银行柜员** → 接收请求，格式化显示
- **后台系统** → 真正处理业务的地方

**前端就是那个"银行柜员"，负责接收用户操作、显示数据、与后台交互。**

### 1.2 前端在CIP系统中的角色

```
┌─────────────────────────────────────────────────────────┐
│                     用户浏览器                            │
└─────────────────────────┬───────────────────────────────────┘
                          │ 操作/点击
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   CIP SCADA 前端                         │
│                                                         │
│   1. 显示清洗区域状态 (温度/流量/步骤)                     │
│   2. 接收用户控制命令 (启动/停止/暂停)                     │
│   3. 实时报警展示                                        │
│   4. 配方管理和批次记录                                  │
│   5. WebSocket实时数据更新                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP REST API + WebSocket
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Python后端 (FastAPI)                    │
│                   - 数据转发                              │
│                   - 协议转换                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ S7协议 (Snap7库)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      PLC (S7-1500)                       │
└─────────────────────────────────────────────────────────┘
```

### 1.3 前端能做什么？

| 功能 | 示例 |
|------|------|
| 数据显示 | 仪表盘、实时数值、趋势图 |
| 用户交互 | 按钮点击、表单输入 |
| 命令下发 | 启动清洗、暂停、复位 |
| 实时更新 | WebSocket推送、状态同步 |
| 报警展示 | 报警列表、声音提醒 |
| 配方管理 | 查看配方、切换配方 |

### 1.4 为什么选择React？

| 特性 | React优势 |
|------|----------|
| 组件化 | 可复用UI组件，提高开发效率 |
| 虚拟DOM | 高效渲染，减少性能消耗 |
| 生态丰富 | 大量第三方库支持 |
| TypeScript | 类型安全，减少错误 |
| 社区活跃 | 文档完善，问题易解决 |

### 1.5 系统界面预览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CIP清洗系统 - 主界面                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  [🔗 已连接]                               [👤 操作员]                      │ ← 顶部导航栏
├─────────────────────────────────────────────────────────────┬───────────────┤
│                                                             │               │
│  ┌─────────────────────────────────────────────────────┐   │   活跃报警     │
│  │                  清洗区域状态                           │   │               │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │   │  🔴 L1 温度过高 │
│  │  │ Zone1   │ │ Zone2   │ │ Zone3   │ │ Zone4   │    │   │  🔴 L1 无流量   │
│  │  │ 水处理   │ │ 茶叶    │ │ 调配    │ │ UHT    │    │   │  🟡 L2 液位低  │
│  │  │ [●]待机  │ │[●]清洗中│ │[●]就绪  │ │[●]暂停  │    │   │               │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘    │   │               │
│  └─────────────────────────────────────────────────────┘   │               │
│                                                             │   系统状态     │
│  ┌─────────────────────────────────────────────────────┐   │               │
│  │            Zone3 调配 - 详细信息                      │   │   状态: 运行中 │
│  │  ┌────────┬────────┬────────┬────────┐             │   │   模式: 自动   │
│  │  │状态    │当前步骤 │当前介质│ 温度   │             │   │   急停: 正常   │
│  │  │清洗中  │3/5     │碱洗    │78.5℃✓│             │   │               │
│  │  └────────┴────────┴────────┴────────┘             │   │               │
│  │  温度设定: 85.0℃  │ 电导率: 1250μS/cm              │   │               │
│  │  流量: 2.35m³/h   │ 泵状态: 运行中 ✓               │   │               │
│  │  ━━━━━━━━━━━━━━━━━━━━━━━━░░░░░░ 60%                │   │               │
│  │  剩余时间: 2分30秒                                   │   │               │
│  └─────────────────────────────────────────────────────┘   │               │
│                                                             │               │
│  ┌─────────────────────────────────────────────────────┐   │               │
│  │  [▶启动] [⏸暂停] [⏹停止] [🔄复位]    [配方▼]       │   │               │
│  └─────────────────────────────────────────────────────┘   │               │
│                                                             │               │
└─────────────────────────────────────────────────────────────┴───────────────┘
```

---

## 2. 技术栈介绍

### 2.1 核心技术

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           前端技术栈                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              框架层                                         │
│                                                                             │
│   ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐    │
│   │      React        │   │      Vite        │   │     TypeScript    │    │
│   │   组件化UI框架     │   │   快速构建工具    │   │   类型安全语言    │    │
│   │   v18.x           │   │   v5.x            │   │   v5.x            │    │
│   └───────────────────┘   └───────────────────┘   └───────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              UI层                                           │
│                                                                             │
│   ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐    │
│   │    Ant Design    │   │     ECharts       │   │     Recharts      │    │
│   │   企业级UI组件    │   │   图表库         │   │   趋势图/饼图    │    │
│   │   v5.x           │   │   v5.x           │   │   v2.x            │    │
│   └───────────────────┘   └───────────────────┘   └───────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              状态管理                                        │
│                                                                             │
│   ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐    │
│   │     Zustand      │   │    React Query    │   │    Context API    │    │
│   │   轻量状态管理    │   │   数据获取/缓存   │   │   跨组件通信     │    │
│   │   v4.x           │   │   v5.x           │   │   内置           │    │
│   └───────────────────┘   └───────────────────┘   └───────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              通信层                                         │
│                                                                             │
│   ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐    │
│   │      Axios       │   │    WebSocket      │   │      STOMP       │    │
│   │   HTTP客户端     │   │   实时通信        │   │   消息协议       │    │
│   │   v1.x           │   │   原生API         │   │   (可选)         │    │
│   └───────────────────┘   └───────────────────┘   └───────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 依赖包说明

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| react | ^18.3 | UI框架 |
| react-dom | ^18.3 | DOM渲染 |
| typescript | ^5.5 | 类型检查 |
| vite | ^5.4 | 构建工具 |
| antd | ^5.x | UI组件库 |
| axios | ^1.7 | HTTP请求 |
| zustand | ^4.5 | 状态管理 |
| dayjs | ^1.11 | 日期处理 |

---

## 3. 项目结构

### 3.1 目录结构

```
project/frontend/
├── public/                 # 静态资源
│   ├── favicon.svg        # 网站图标
│   └── icons.svg          # 图标集
├── src/                    # 源代码
│   ├── assets/            # 资源文件
│   │   ├── hero.png       # 背景图
│   │   ├── react.svg      # React Logo
│   │   └── vite.svg       # Vite Logo
│   ├── components/        # 公共组件 (可选)
│   │   ├── Header.tsx    # 顶部导航
│   │   ├── Sidebar.tsx   # 侧边栏
│   │   └── Footer.tsx    # 底部
│   ├── pages/             # 页面组件
│   │   ├── MainDashboard.tsx  # 主仪表盘
│   │   └── MainDashboard.css  # 样式
│   ├── services/          # 服务层
│   │   ├── api.ts        # HTTP API
│   │   ├── websocket.ts   # WebSocket服务
│   │   └── index.ts      # 导出
│   ├── store/             # 状态管理
│   │   ├── cipStore.ts   # CIP状态
│   │   └── index.ts      # 导出
│   ├── types/             # 类型定义
│   │   ├── cip.ts        # CIP相关类型
│   │   └── index.ts      # 导出
│   ├── App.tsx           # 根组件
│   ├── main.tsx          # 入口文件
│   ├── index.css         # 全局样式
│   └── vite-env.d.ts     # Vite类型声明
├── .gitignore            # Git忽略
├── eslint.config.js      # ESLint配置
├── index.html            # HTML模板
├── package-lock.json     # 依赖锁定
├── package.json          # 依赖配置
├── tsconfig.app.json     # TS应用配置
├── tsconfig.json         # TS基础配置
├── tsconfig.node.json    # TS Node配置
└── vite.config.ts        # Vite配置
```

### 3.2 架构分层图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           前端架构分层                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              视图层 (View)                                  │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │                     pages/MainDashboard.tsx                          │  │
│   │                                                                      │  │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │  │
│   │   │ 区域卡片  │  │ 统计卡片  │  │ 报警列表  │  │    控制按钮     │   │  │
│   │   └──────────┘  └──────────┘  └──────────┘  └──────────────────┘   │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            状态管理层 (Store)                                │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │                      store/cipStore.ts                              │  │
│   │                                                                      │  │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │  │
│   │   │ zones   │  │ alarms  │  │ recipes │  │ system  │  │ loading │  │  │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            服务层 (Services)                                 │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │                                                                      │  │
│   │   ┌───────────────┐              ┌───────────────┐                │  │
│   │   │    api.ts     │              │ websocket.ts  │                │  │
│   │   │  HTTP API调用  │              │  实时数据通信   │                │  │
│   │   └───────┬───────┘              └───────┬───────┘                │  │
│   │           │                            │                         │  │
│   └───────────┼────────────────────────────┼───────────────────────────┘  │
└───────────────┼────────────────────────────┼───────────────────────────────┘
                │                            │
                ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            通信层                                           │
│                                                                             │
│   ┌───────────────────┐              ┌───────────────────┐                │
│   │      Axios        │              │    WebSocket       │                │
│   │   HTTP/HTTPS      │              │   ws:// / wss://   │                │
│   │   GET/POST/PUT    │              │   实时双向通信      │                │
│   └───────────────────┘              └───────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘
                │                            │
                └──────────────┬─────────────┘
                               ▼
                    ┌───────────────────┐
                    │   Python后端API    │
                    │   FastAPI Server   │
                    └───────────────────┘
```

### 3.3 数据流向图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              数据流向                                        │
└─────────────────────────────────────────────────────────────────────────────┘

    用户操作                    WebSocket推送                HTTP轮询
       │                            │                           │
       ▼                            ▼                           ▼
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│  按钮点击   │              │  实时数据   │              │  API请求    │
│  区域选择   │              │  zone_data  │              │  getZones   │
│  命令发送   │              │  alarm_new  │              │  getAlarms  │
└──────┬──────┘              └──────┬──────┘              └──────┬──────┘
       │                           │                           │
       ▼                           ▼                           ▼
┌─────────────┐              ┌─────────────┐              ┌─────────────┐
│ sendCommand │              │ handleWSMsg │              │ fetchZones  │
│ zoneApi     │              │ 更新Store   │              │ zoneApi     │
└──────┬──────┘              └──────┬──────┘              └──────┬──────┘
       │                           │                           │
       ▼                           ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Zustand Store                                   │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │  set({ zones: [...], alarms: [...], systemStatus: {...} })         │  │
│   │                                                                      │  │
│   │  state = {                                                           │  │
│   │    zones: ZoneStatus[],     // 5个清洗区数据                          │  │
│   │    alarms: AlarmInfo[],     // 报警列表                              │  │
│   │    recipes: RecipeInfo[],   // 配方列表                              │  │
│   │    systemStatus: {...},     // 系统状态                              │  │
│   │    selectedZones: number[],  // 选中的区域                           │  │
│   │    wsConnected: boolean,     // 连接状态                             │  │
│   │  }                                                                   │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              React组件重渲染                                 │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐  │
│   │  useCIPStore() → 读取zones/alarms → 自动更新UI                      │  │
│   │                                                                      │  │
│   │  <ZoneCard zone={zone} /> ← zones.map()                             │  │
│   │  <AlarmList alarms={alarms} /> ← alarms.map()                       │  │
│   │                                                                      │  │
│   └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 核心概念

### 4.1 React组件

**组件是UI的构建块**：

```tsx
// ZoneCard.tsx - 区域卡片组件
import React from 'react';
import { Card, Tag, Badge } from 'antd';
import type { ZoneStatus } from '@/types';

interface Props {
  zone: ZoneStatus;
  selected?: boolean;
  onClick?: () => void;
}

const ZoneCard: React.FC<Props> = ({ zone, selected, onClick }) => {
  return (
    <Card
      size="small"
      onClick={onClick}
      style={{
        borderColor: selected ? '#1890ff' : '#d9d9d9',
        cursor: 'pointer'
      }}
    >
      <div>{zone.zone_name}</div>
      <Badge status={getStatusBadge(zone.state)} text={zone.state} />
    </Card>
  );
};
```

### 4.2 TypeScript类型

**类型确保代码安全**：

```typescript
// types/cip.ts

// 清洗状态枚举
export type CleanState = 'IDLE' | 'READY' | 'STEP_EXEC' | 'PAUSE' | 'FAULT' | 'COMPLETE';

// 区域状态
export interface ZoneStatus {
  zone_id: number;           // 区域ID
  zone_name: string;         // 区域名称
  state: CleanState;         // 当前状态
  current_step: number;      // 当前步骤
  total_steps: number;       // 总步骤数
  current_media: string;     // 当前介质
  temp_pv: number;          // 当前温度
  temp_sp: number;          // 设定温度
  temp_reached: boolean;    // 温度是否达标
  conductivity: number;      // 电导率
  flow_pv: number;          // 当前流量
  pump_running: boolean;    // 泵运行状态
  step_time_remaining: number; // 剩余时间(秒)
}

// 报警信息
export interface AlarmInfo {
  alarm_id: number;
  zone_id: number;
  level: 'L0' | 'L1' | 'L2';  // 报警等级
  code: number;               // 报警代码
  alarm_text: string;         // 报警文本
  occur_time: string;         // 发生时间
  acked: boolean;             // 是否确认
}

// 控制命令
export interface ControlCommand {
  zone_id: number;
  command: 'START' | 'STOP' | 'PAUSE' | 'RESUME' | 'RESET';
}
```

### 4.3 Hooks (钩子)

**Hooks让函数组件有状态**：

```typescript
// useEffect - 副作用操作
useEffect(() => {
  // 组件挂载时执行
  fetchZones();
  
  // 可选：组件卸载时清理
  return () => {
    cleanup();
  };
}, []);  // 空数组：只在挂载/卸载时执行

// useState - 状态管理
const [count, setCount] = useState(0);
<button onClick={() => setCount(count + 1)}>+1</button>

// useSelector (配合Zustand)
const zones = useCIPStore((state) => state.zones);
```

### 4.4 Zustand状态管理

**轻量级状态管理库**：

```typescript
// store/cipStore.ts
import { create } from 'zustand';

interface CIPState {
  zones: ZoneStatus[];
  alarms: AlarmInfo[];
  wsConnected: boolean;
  
  fetchZones: () => Promise<void>;
  setWSConnected: (connected: boolean) => void;
}

export const useCIPStore = create<CIPState>((set) => ({
  zones: [],
  alarms: [],
  wsConnected: false,
  
  fetchZones: async () => {
    const zones = await zoneApi.getAllZones();
    set({ zones });
  },
  
  setWSConnected: (connected) => {
    set({ wsConnected: connected });
  },
}));
```

### 4.5 条件渲染

**根据状态显示不同内容**：

```tsx
// 报警列表
{alarms.length === 0 ? (
  <Text type="secondary">暂无报警</Text>
) : (
  alarms.map((alarm) => (
    <div key={alarm.alarm_id}>
      <Tag color={getLevelColor(alarm.level)}>
        {alarm.level}
      </Tag>
      <Text>{alarm.alarm_text}</Text>
    </div>
  ))
)}
```

---

## 5. 代码详解

### 5.1 入口文件 (main.tsx)

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**作用**：
- 创建React根节点
- 渲染App组件
- 启用StrictMode开发检查

### 5.2 根组件 (App.tsx)

```tsx
import React from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { MainDashboard } from '@/pages';
import './App.css';

const App: React.FC = () => {
  return (
    // 配置Ant Design中文语言
    <ConfigProvider locale={zhCN}>
      <MainDashboard />
    </ConfigProvider>
  );
};

export default App;
```

**作用**：
- 全局配置（语言、主题）
- 路由（当前单页面）
- 提供者组件包裹

### 5.3 主仪表盘 (MainDashboard.tsx)

```tsx
import React, { useEffect } from 'react';
import { Layout, Card, Row, Col, Statistic } from 'antd';
import { useCIPStore } from '@/store';

const { Header, Content } = Layout;

const MainDashboard: React.FC = () => {
  // 从Store获取状态和方法
  const { zones, alarms, wsConnected, initialize, cleanup } = useCIPStore();

  // 组件挂载时初始化
  useEffect(() => {
    initialize();
    return () => cleanup();  // 卸载时清理
  }, [initialize, cleanup]);

  return (
    <Layout className="cip-dashboard">
      {/* 顶部导航 */}
      <Header className="dashboard-header">
        <h2>CIP清洗系统控制</h2>
        <Badge status={wsConnected ? 'success' : 'error'} text="连接状态" />
      </Header>

      <Content className="dashboard-content">
        <Row gutter={16}>
          {/* 左侧：区域卡片 */}
          <Col span={16}>
            <Card title="清洗区域状态">
              <Row gutter={16}>
                {zones.map((zone) => (
                  <Col span={4} key={zone.zone_id}>
                    <ZoneCard zone={zone} />
                  </Col>
                ))}
              </Row>
            </Card>
          </Col>

          {/* 右侧：报警 */}
          <Col span={8}>
            <Card title="活跃报警">
              {alarms.map((alarm) => (
                <AlarmItem key={alarm.alarm_id} alarm={alarm} />
              ))}
            </Card>
          </Col>
        </Row>
      </Content>
    </Layout>
  );
};
```

### 5.4 状态常量映射

```tsx
// 状态颜色映射
const stateColors: Record<CleanState, string> = {
  IDLE: '#8c8c8c',         // 灰色 - 待机
  READY: '#1890ff',        // 蓝色 - 就绪
  STEP_EXEC: '#52c41a',    // 绿色 - 执行中
  PAUSE: '#faad14',        // 黄色 - 暂停
  FAULT: '#ff4d4f',        // 红色 - 故障
  COMPLETE: '#722ed1',     // 紫色 - 完成
};

// 状态文本映射
const stateText: Record<CleanState, string> = {
  IDLE: '待机',
  READY: '就绪',
  STEP_EXEC: '清洗中',
  PAUSE: '暂停',
  FAULT: '故障',
  COMPLETE: '完成',
};

// 介质文本映射
const mediaText: Record<string, string> = {
  PURE_WATER: '纯水',
  CAUSTIC: '碱液',
  ACID: '酸液',
  HOT_WATER: '热水',
  DISINFECTANT: '消毒液',
};
```

---

## 6. 启动项目

### 6.1 安装依赖

```bash
cd project/frontend
npm install
```

### 6.2 开发模式启动

```bash
npm run dev
```

**输出**：

```
  VITE v5.4.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h + enter to show help
```

### 6.3 访问页面

1. 打开浏览器
2. 访问 http://localhost:5173
3. 看到CIP清洗系统主界面

### 6.4 环境变量配置

```bash
# 创建 .env 文件
cp .env.example .env
```

**配置项**：

```bash
# .env
VITE_API_URL=http://localhost:8000      # 后端API地址
VITE_WS_URL=ws://localhost:8000/ws/zones  # WebSocket地址
```

### 6.5 构建生产版本

```bash
npm run build
```

**输出到 `dist/` 目录**：

```
dist/
├── index.html
├── assets/
│   ├── index-[hash].js
│   └── index-[hash].css
└── ...
```

### 6.6 预览构建结果

```bash
npm run preview
```

---

## 7. API通信

### 7.1 Axios实例创建

```typescript
// services/api.ts
import axios from 'axios';

// 创建实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加token等
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

### 7.2 Zone API

```typescript
// 获取所有Zone状态
export const getAllZones = async (): Promise<ZoneStatus[]> => {
  const response = await api.get('/api/v1/zones');
  return response.data;
};

// 获取单个Zone状态
export const getZone = async (zoneId: number): Promise<ZoneStatus> => {
  const response = await api.get(`/api/v1/zones/${zoneId}`);
  return response.data;
};

// 发送控制命令
export const sendCommand = async (command: ControlCommand): Promise<{ status: string }> => {
  const response = await api.post('/api/v1/zones/command', command);
  return response.data;
};
```

### 7.3 Alarm API

```typescript
// 获取活跃报警
export const getActiveAlarms = async (): Promise<AlarmInfo[]> => {
  const response = await api.get('/api/v1/alarms');
  return response.data;
};

// 确认报警
export const ackAlarm = async (alarmId: number, user: string): Promise<boolean> => {
  const response = await api.post(`/api/v1/alarms/${alarmId}/ack`, { user });
  return response.data.status === 'ok';
};
```

### 7.4 Recipe API

```typescript
// 获取所有配方
export const getAllRecipes = async (): Promise<RecipeInfo[]> => {
  const response = await api.get('/api/v1/recipes');
  return response.data;
};

// 执行配方
export const executeRecipe = async (zoneId: number, recipeId: number): Promise<{ status: string }> => {
  const response = await api.post('/api/v1/recipes/execute', {
    zone_id: zoneId,
    recipe_id: recipeId,
  });
  return response.data;
};
```

### 7.5 调用示例

```tsx
// 在组件中调用API
const fetchData = async () => {
  try {
    // 获取数据
    const zones = await zoneApi.getAllZones();
    setZones(zones);
    
    // 发送命令
    await zoneApi.sendCommand({ zone_id: 1, command: 'START' });
    
    // 处理结果
    message.success('命令发送成功');
  } catch (error) {
    message.error('操作失败');
  }
};
```

---

## 8. 状态管理

### 8.1 Zustand Store定义

```typescript
// store/cipStore.ts
import { create } from 'zustand';
import type { ZoneStatus, AlarmInfo, RecipeInfo } from '@/types';
import { zoneApi, alarmApi, recipeApi } from '@/services';

interface CIPState {
  // 数据
  zones: ZoneStatus[];
  alarms: AlarmInfo[];
  recipes: RecipeInfo[];
  
  // UI状态
  selectedZones: number[];
  wsConnected: boolean;
  loading: boolean;
  
  // 操作
  fetchZones: () => Promise<void>;
  fetchAlarms: () => Promise<void>;
  fetchRecipes: () => Promise<void>;
  sendCommand: (zoneId: number, command: string) => Promise<boolean>;
  toggleZone: (zoneId: number) => void;
  setWSConnected: (connected: boolean) => void;
  initialize: () => void;
  cleanup: () => void;
}

export const useCIPStore = create<CIPState>((set, get) => ({
  // 初始状态
  zones: [],
  alarms: [],
  recipes: [],
  selectedZones: [],
  wsConnected: false,
  loading: false,

  // 获取所有Zone状态
  fetchZones: async () => {
    try {
      const zones = await zoneApi.getAllZones();
      set({ zones });
    } catch (error) {
      console.error('Failed to fetch zones:', error);
    }
  },

  // 获取报警列表
  fetchAlarms: async () => {
    try {
      const alarms = await alarmApi.getActiveAlarms();
      set({ alarms });
    } catch (error) {
      console.error('Failed to fetch alarms:', error);
    }
  },

  // 发送控制命令
  sendCommand: async (zoneId: number, command: string) => {
    try {
      const result = await zoneApi.sendCommand({
        zone_id: zoneId,
        command: command as 'START' | 'STOP' | 'PAUSE' | 'RESET',
      });
      if (result.status === 'ok') {
        await get().fetchZones();  // 刷新数据
        return true;
      }
      return false;
    } catch (error) {
      console.error('Failed to send command:', error);
      return false;
    }
  },

  // 选中/取消Zone
  toggleZone: (zoneId: number) => {
    const { selectedZones } = get();
    if (selectedZones.includes(zoneId)) {
      set({ selectedZones: selectedZones.filter(id => id !== zoneId) });
    } else {
      set({ selectedZones: [...selectedZones, zoneId] });
    }
  },

  // 初始化
  initialize: () => {
    get().fetchZones();
    get().fetchAlarms();
    get().fetchRecipes();
    // 连接WebSocket...
  },

  // 清理
  cleanup: () => {
    // 断开WebSocket...
  },
}));
```

### 8.2 组件中使用Store

```tsx
import { useCIPStore } from '@/store';

const MyComponent: React.FC = () => {
  // 获取状态
  const zones = useCIPStore((state) => state.zones);
  const alarms = useCIPStore((state) => state.alarms);
  
  // 获取方法
  const fetchZones = useCIPStore((state) => state.fetchZones);
  const sendCommand = useCIPStore((state) => state.sendCommand);
  
  // 处理启动
  const handleStart = async () => {
    const success = await sendCommand(1, 'START');
    if (success) {
      message.success('启动成功');
    }
  };
  
  return <button onClick={handleStart}>启动</button>;
};
```

### 8.3 Store切片模式

```typescript
// 为大项目准备的切片模式
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Zone切片
const useZoneStore = create(
  devtools((set) => ({
    zones: [],
    fetchZones: async () => {
      const zones = await zoneApi.getAllZones();
      set({ zones });
    },
  }), { name: 'zone-store' })
);

// Alarm切片
const useAlarmStore = create(
  devtools((set) => ({
    alarms: [],
    fetchAlarms: async () => {
      const alarms = await alarmApi.getActiveAlarms();
      set({ alarms });
    },
  }), { name: 'alarm-store' })
);

// 在组件中使用
const zones = useZoneStore((state) => state.zones);
const alarms = useAlarmStore((state) => state.alarms);
```

---

## 9. WebSocket实时通信

### 9.1 WebSocket服务

```typescript
// services/websocket.ts
import type { WSMessage, ZoneStatus, AlarmInfo } from '@/types';
import { useCIPStore } from '@/store';

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectTimer: number | null = null;
  private url: string;

  constructor(url: string) {
    this.url = url;
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        useCIPStore.getState().setWSConnected(true);
        
        // 清除重连计时器
        if (this.reconnectTimer) {
          clearTimeout(this.reconnectTimer);
          this.reconnectTimer = null;
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        useCIPStore.getState().setWSConnected(false);
        this.scheduleReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect:', error);
      this.scheduleReconnect();
    }
  }

  private handleMessage(message: WSMessage) {
    const store = useCIPStore.getState();

    switch (message.type) {
      case 'zone_data':
        // 更新Zone数据
        store.fetchZones();
        break;
        
      case 'alarm_new':
        // 新报警
        store.fetchAlarms();
        break;
        
      case 'alarm_cleared':
        // 报警清除
        store.fetchAlarms();
        break;
        
      case 'system_status':
        // 系统状态更新
        store.fetchSystemStatus();
        break;
    }
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    
    this.reconnectTimer = window.setTimeout(() => {
      console.log('Attempting to reconnect...');
      this.connect();
    }, 3000);  // 3秒后重连
  }

  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// 导出单例
export const wsService = new WebSocketService(
  import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/zones'
);
```

### 9.2 消息类型定义

```typescript
// types/cip.ts

export interface WSMessage {
  type: 'zone_data' | 'alarm_new' | 'alarm_cleared' | 'system_status';
  data?: any;
  timestamp: string;
}

export interface WSZoneData {
  type: 'zone_data';
  data: ZoneStatus[];
}

export interface WSAlarmNew {
  type: 'alarm_new';
  data: AlarmInfo;
}
```

### 9.3 在组件中使用

```tsx
import { useEffect } from 'react';
import { wsService } from '@/services';

const MyComponent: React.FC = () => {
  useEffect(() => {
    // 连接WebSocket
    wsService.connect();
    
    // 组件卸载时断开
    return () => {
      wsService.disconnect();
    };
  }, []);

  return <div>实时数据展示</div>;
};
```

---

## 10. 项目实战练习

### 练习1：添加新的状态显示

**目标**：在Zone卡片上显示"电导率"信息

**步骤**：

1. 在 `types/cip.ts` 中确认类型已存在：

```typescript
export interface ZoneStatus {
  // ... 其他字段
  conductivity: number;  // 电导率
}
```

2. 在 `MainDashboard.tsx` 中添加显示：

```tsx
// 在ZoneCard中添加电导率显示
const ZoneCard: React.FC<Props> = ({ zone }) => {
  return (
    <Card>
      <div>{zone.zone_name}</div>
      <Badge status={getStatusBadge(zone.state)} />
      {/* 新增：电导率显示 */}
      <div style={{ marginTop: 8 }}>
        <Text type="secondary">电导率:</Text>
        <Text strong>{zone.conductivity} μS/cm</Text>
      </div>
    </Card>
  );
};
```

### 练习2：添加控制按钮

**目标**：为选中区域添加强制停止按钮

**步骤**：

1. 添加按钮组件：

```tsx
const EmergencyStopButton: React.FC = () => {
  const sendCommand = useCIPStore((state) => state.sendCommand);
  const selectedZones = useCIPStore((state) => state.selectedZones);

  const handleEmergencyStop = async () => {
    for (const zoneId of selectedZones) {
      await sendCommand(zoneId, 'STOP');
    }
    message.warning('已发送停止命令');
  };

  return (
    <Button
      danger
      icon={<StopOutlined />}
      onClick={handleEmergencyStop}
      disabled={selectedZones.length === 0}
    >
      紧急停止
    </Button>
  );
};
```

2. 在页面中使用：

```tsx
<ButtonGroup>
  <EmergencyStopButton />
</ButtonGroup>
```

### 练习3：添加报警确认功能

**目标**：点击报警列表项确认报警

**步骤**：

1. 添加确认函数到Store：

```typescript
// store/cipStore.ts
acknowledgeAlarm: async (alarmId: number) => {
  try {
    await alarmApi.ackAlarm(alarmId, 'Operator');
    await get().fetchAlarms();
    return true;
  } catch (error) {
    console.error('Failed to ack alarm:', error);
    return false;
  }
},
```

2. 在组件中使用：

```tsx
const AlarmItem: React.FC<{ alarm: AlarmInfo }> = ({ alarm }) => {
  const ackAlarm = useCIPStore((state) => state.acknowledgeAlarm);

  const handleAck = async () => {
    const success = await ackAlarm(alarm.alarm_id);
    if (success) {
      message.success('报警已确认');
    }
  };

  return (
    <div className="alarm-item">
      <Tag color={getLevelColor(alarm.level)}>{alarm.level}</Tag>
      <Text>{alarm.alarm_text}</Text>
      {!alarm.acked && (
        <Button size="small" onClick={handleAck}>确认</Button>
      )}
    </div>
  );
};
```

### 练习4：添加趋势图

**目标**：显示温度变化趋势

**步骤**：

1. 安装图表库：

```bash
npm install echarts echarts-for-react
```

2. 添加趋势图组件：

```tsx
import ReactECharts from 'echarts-for-react';

// 温度趋势图
const TempTrendChart: React.FC<{ zoneId: number }> = ({ zoneId }) => {
  const zones = useCIPStore((state) => state.zones);
  const zone = zones.find(z => z.zone_id === zoneId);

  const option = {
    title: { text: '温度趋势' },
    xAxis: { type: 'category', data: ['9:00', '9:05', '9:10', '9:15', '9:20'] },
    yAxis: { type: 'value', name: '℃' },
    series: [{
      data: [25, 45, 65, 78, 85],
      type: 'line',
      smooth: true,
    }],
  };

  return <ReactECharts option={option} style={{ height: 300 }} />;
};
```

---

## 11. 调试方法

### 11.1 React DevTools

**安装Chrome扩展**：

1. Chrome应用商店搜索 "React Developer Tools"
2. 安装后重启浏览器
3. 按F12打开开发者工具
4. 选择 "Components" 或 "Profiler" 标签

**用途**：

- 查看组件树
- 检查Props和State
- 性能分析
- 定位问题组件

### 11.2 网络请求调试

**Network面板使用**：

```
1. F12 打开开发者工具
2. 选择 Network 标签
3. 刷新页面
4. 查看 XHR/Fetch 请求
5. 点击请求查看详情
   - Headers: 请求头、响应头
   - Payload: 请求数据
   - Preview/Response: 响应内容
```

### 11.3 Console日志

```tsx
// 调试Store
const zones = useCIPStore((state) => {
  console.log('Zones updated:', state.zones);  // 调试日志
  return state.zones;
});

// 调试API
zoneApi.getAllZones()
  .then(data => console.log('API Response:', data))
  .catch(error => console.error('API Error:', error));
```

### 11.4 常见问题排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 页面空白 | 路由错误/组件报错 | 检查控制台错误 |
| 数据不更新 | API调用失败 | 检查Network面板 |
| 按钮无响应 | 事件未绑定 | 检查onClick |
| 样式错乱 | CSS冲突 | 检查className |
| WebSocket断开 | 网络问题 | 检查连接状态 |

### 11.5 断点调试

```tsx
// 在代码中添加断点
const handleClick = () => {
  debugger;  // 浏览器会在此处暂停
  doSomething();
};
```

---

## 12. 常见问题

### Q1: 页面显示"未连接"？

**解答**：

1. 检查后端服务是否启动
2. 检查WebSocket地址配置

```bash
# 启动后端
cd project/backend
docker-compose up -d
```

```bash
# 检查 .env 配置
VITE_WS_URL=ws://localhost:8000/ws/zones
```

### Q2: 数据不更新？

**排查步骤**：

1. 检查网络请求是否成功（Network面板）
2. 检查Store状态是否正确更新
3. 检查组件是否正确订阅Store

```tsx
// 错误：没有订阅Store
const zones = zonesData;  // ❌ 直接使用

// 正确：订阅Store
const zones = useCIPStore((state) => state.zones);  // ✅
```

### Q3: 样式不生效？

**常见原因**：

| 原因 | 解决 |
|------|------|
| CSS优先级 | 使用更高优先级或 `!important` |
| 类名冲突 | 使用唯一类名 |
| 未导入CSS | 确认 `import './xxx.css'` |
| 样式覆盖 | 检查是否有全局样式影响 |

### Q4: TypeScript报错？

**常见错误**：

```typescript
// 错误1: 类型不匹配
const name: string = 123;  // ❌

// 正确
const name: string = '张三';  // ✅

// 错误2: 可能为null
const data = response.data;  // ❌ 可能为null

// 正确: 使用可选链或默认值
const data = response.data ?? [];
const name = response.data?.name ?? 'Unknown';
```

### Q5: 如何添加新页面？

**步骤**：

1. 创建页面组件：

```tsx
// pages/RecipeManagement.tsx
const RecipeManagement: React.FC = () => {
  return <div>配方管理页面</div>;
};
```

2. 添加路由（如果使用react-router）：

```tsx
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainDashboard from './pages/MainDashboard';
import RecipeManagement from './pages/RecipeManagement';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainDashboard />} />
        <Route path="/recipes" element={<RecipeManagement />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### Q6: 性能优化？

**方法**：

1. **使用React.memo**：

```tsx
const ZoneCard = React.memo<Props>(({ zone }) => {
  return <Card>{zone.name}</Card>;
});
```

2. **使用useMemo**：

```tsx
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);
```

3. **使用useCallback**：

```tsx
const handleClick = useCallback(() => {
  doSomething();
}, []);
```

---

## 13. 术语表

### 13.1 React相关

| 术语 | 说明 |
|------|------|
| Component | 组件，UI构建块 |
| Props | 属性，从父组件传递给子组件 |
| State | 状态，组件内部数据 |
| Hook | 钩子，函数组件的特殊函数 |
| JSX | JavaScript XML，React语法扩展 |
| Virtual DOM | 虚拟DOM，提升渲染性能 |
| Reconciliation | 协调，比较虚拟DOM差异 |

### 13.2 TypeScript相关

| 术语 | 说明 |
|------|------|
| Type | 类型，数据的形式 |
| Interface | 接口，对象结构定义 |
| Generic | 泛型，通用类型参数 |
| Union | 联合类型，多种可能 |
| Type Guard | 类型守卫，缩小类型范围 |

### 13.3 前端通用

| 术语 | 说明 |
|------|------|
| SPA | 单页应用 |
| CSR | 客户端渲染 |
| SSR | 服务端渲染 |
| API | 应用程序接口 |
| REST | RESTful API风格 |
| WebSocket | 双向通信协议 |

### 13.4 状态管理

| 术语 | 说明 |
|------|------|
| Store | 状态存储 |
| State | 状态数据 |
| Action | 动作，触发状态变更 |
| Reducer | reducer函数，处理状态变更 |
| Middleware | 中间件，扩展功能 |

### 13.5 CIP系统相关

| 术语 | 说明 |
|------|------|
| Zone | 清洗区域 |
| Clean State | 清洗状态 |
| Media | 清洗介质 |
| Recipe | 清洗配方 |
| Alarm | 报警 |
| Conductivity | 电导率 |

---

## 14. 学习路径建议

### 14.1 学习阶段

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           前端学习路线                                        │
└─────────────────────────────────────────────────────────────────────────────┘

阶段1: 入门 (1-2周)
├── 理解HTML/CSS/JavaScript基础
├── 学习React组件编写
├── 理解TypeScript基础类型
└── 完成练习1-2

阶段2: 进阶 (2-4周)
├── 掌握Hooks (useState/useEffect/useCallback)
├── 学习Zustand状态管理
├── 理解HTTP/WebSocket通信
└── 完成练习3-4

阶段3: 实战 (4-8周)
├── 理解CIP清洗工艺
├── 分析本项目代码
├── 独立完成功能修改
└── 调试与优化

阶段4: 精通 (持续)
├── React源码学习
├── 性能优化
├── 架构设计
└── 团队协作
```

### 14.2 推荐学习资源

| 资源类型 | 推荐内容 |
|----------|----------|
| 官方文档 | React.dev, TypeScript官方文档 |
| 在线教程 | React Tutorial, Egghead.io |
| 视频课程 | B站React课程 |
| 实践项目 | 本CIP SCADA系统 |

### 14.3 进阶主题

| 主题 | 说明 | 推荐深入 |
|------|------|----------|
| 状态管理 | Redux, Zustand, Jotai | 状态管理库对比 |
| 路由 | React Router v6 | 路由守卫 |
| UI框架 | Ant Design, Chakra UI | 主题定制 |
| 图表 | ECharts, Recharts | 数据可视化 |
| 测试 | Vitest, React Testing Library | 单元测试 |
| 构建 | Vite, Webpack | 打包优化 |

### 14.4 项目实践建议

1. **从修改开始**：先修改现有代码，不要从头编写
2. **小步快跑**：每次只改一个功能，测试通过再继续
3. **善用DevTools**：React DevTools调试组件状态
4. **记录问题**：遇到问题记录下来，形成知识库
5. **代码审查**：写完后检查自己的代码

---

**文档信息**：

- 版本: v1.0
- 适用: React 18 + TypeScript 5 + Vite 5
- 最后更新: 2025-05-15
