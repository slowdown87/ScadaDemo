# GitHub Pages 部署说明

## 当前状态

本项目包含：
- ✅ **前端** (React + TypeScript) - 可部署到 GitHub Pages
- ❌ **后端** (FastAPI + Python) - 需要独立服务器
- ❌ **AI 服务** (Python ML) - 需要 GPU/ML 运行环境

## 部署前端到 GitHub Pages

### 1. 修改 Vite 配置
创建 `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: './',  // 重要：使用相对路径
  plugins: [react()],
  // ...
})
```

### 2. 修改 API 地址
创建 `src/config/demo.ts`:

```typescript
export const API_BASE = '';  // 使用相对路径
```

### 3. 启用 GitHub Actions
创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run build
        env:
          VITE_API_URL: ''
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

### 4. 启用 GitHub Pages
1. 进入仓库 Settings → Pages
2. Source: GitHub Actions

## 完整部署架构

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Pages                          │
│              (仅前端静态页面)                            │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                 │
│  │ 主监控   │  │数字孪生 │  │ 历史记录 │                 │
│  └─────────┘  └─────────┘  └─────────┘                 │
└────────────────────┬──────────────────────────────────┘
                     │ (API调用)
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │FastAPI  │  │  Redis  │  │ PostgreSQL│
   │ Backend │  │  Cache  │  │ Database │
   └─────────┘  └─────────┘  └─────────┘
        │            │            │
        └────────────┴────────────┘
                     │
                     ▼
              ┌───────────┐
              │   PLC     │
              │ S7-1500   │
              └───────────┘
```

## 实际生产部署建议

| 环境 | 方案 | 说明 |
|------|------|------|
| 开发/测试 | Docker Compose | 本地运行全部服务 |
| 演示 | GitHub Pages + 云服务 | 前端在 GitHub，API 在云服务器 |
| 生产 | Kubernetes + 云服务 | 完整容器化部署 |

## 当前项目已完成

所有代码已提交到 GitHub：
https://github.com/slowdown87/ScadaDemo
