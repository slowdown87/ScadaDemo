# CIP SCADA 前端项目

> 茶饮料生产线CIP清洗系统的Web SCADA前端

## 技术栈

- **框架**: React 19 + TypeScript 5
- **构建工具**: Vite 5
- **UI组件库**: Ant Design 6
- **状态管理**: Zustand 5
- **路由**: React Router 7
- **HTTP客户端**: Axios
- **图表**: ECharts 6
- **日期处理**: Day.js

## 项目结构

```
src/
├── pages/              # 页面组件
│   ├── MainLayout.tsx       # 主布局
│   ├── MainDashboard.tsx     # WS-010 主监控画面
│   ├── RecipePage.tsx        # WS-010-01 配方管理
│   ├── ChemicalsPage.tsx     # WS-010-02 清洗剂配置
│   ├── QueuePage.tsx         # WS-010-03 清洗队列
│   ├── HistoryPage.tsx        # WS-010-04 历史记录
│   └── AlarmPage.tsx         # WS-010-05 报警列表
├── services/          # 服务层
│   ├── api.ts               # HTTP API调用
│   └── websocket.ts         # WebSocket服务
├── store/             # 状态管理
│   └── cipStore.ts          # CIP状态Store
├── types/              # 类型定义
│   └── cip.ts              # CIP相关类型
├── App.tsx            # 根组件
└── main.tsx          # 入口文件
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/zones
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 4. 构建生产版本

```bash
npm run build
npm run preview
```

## 页面说明

| 页面 | 路由 | 说明 |
|------|------|------|
| WS-010 主监控 | `/` | 5区状态、实时数据、控制按钮 |
| WS-010-01 配方管理 | `/recipes` | 配方列表、执行配方 |
| WS-010-02 清洗剂配置 | `/chemicals` | 清洗剂参数配置 |
| WS-010-03 清洗队列 | `/queue` | 清洗队列管理 |
| WS-010-04 历史记录 | `/history` | 清洗历史查询、导出 |
| WS-010-05 报警列表 | `/alarms` | 报警确认、清除 |

## API对接

前端通过以下方式与后端通信：

1. **REST API** (Axios)
   - GET /api/v1/zones - 获取所有Zone状态
   - POST /api/v1/zones/command - 发送控制命令
   - GET /api/v1/alarms - 获取报警列表
   - GET /api/v1/recipes - 获取配方列表
   - GET /api/v1/batch - 获取批次记录

2. **WebSocket** (实时推送)
   - /ws/zones - Zone数据实时更新
   - 自动重连机制
   - 消息类型: zone_data, alarm_new, alarm_cleared

## 开发指南

### 添加新页面

1. 在 `pages/` 创建页面组件
2. 在 `App.tsx` 添加路由
3. 在侧边栏菜单添加链接

```tsx
// pages/MyPage.tsx
const MyPage: React.FC = () => {
  return <div>我的页面</div>;
};
export default MyPage;
```

### 添加API接口

在 `services/api.ts` 中添加：

```typescript
export const myApi = {
  getData: async () => {
    const response = await api.get('/api/v1/my-endpoint');
    return response.data;
  },
};
```

### 状态管理

使用Zustand管理全局状态：

```typescript
// store/myStore.ts
import { create } from 'zustand';

interface MyState {
  data: MyData[];
  fetchData: () => Promise<void>;
}

export const useMyStore = create<MyState>((set, get) => ({
  data: [],
  fetchData: async () => {
    const data = await myApi.getData();
    set({ data });
  },
}));
```

## 环境要求

- Node.js >= 18
- npm >= 9

## 相关文档

- [前端完整教程](../../docs/08_project_tutorial/manual/frontend_tutorial.md)
- [后端项目](../backend/README.md)
- [PLC程序](../plc/README.md)

## 版本历史

- v1.0 (2026-05-15): 初始版本，包含基础页面框架
