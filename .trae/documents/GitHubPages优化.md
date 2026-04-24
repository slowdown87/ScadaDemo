# SCADA数字孪生系统 - GitHub Pages优化

> 文档版本: v1.0
> 创建日期: 2026-04-24
> 部署方案: 方案1 - 纯前端（GitHub Pages）

---

## 一、GitHub Pages限制分析

### 1.1 硬性限制

| 限制项 | 数值 | 影响 |
|--------|------|------|
| 仓库大小 | 1GB | 需要控制资源大小 |
| 单文件大小 | 100MB | 模型文件不能超过 |
| 带宽 | 100GB/月 | 流量大的话会限制 |
| 软限制建议 | 50MB | 最佳实践 |

### 1.2 架构约束

```
┌─────────────────────────────────────────────────────────────────┐
│                     GitHub Pages 约束                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ❌ 无法运行服务端代码（Node.js、Python等）                      │
│  ❌ 无法使用WebSocket服务端                                       │
│  ❌ 无法连接数据库                                               │
│  ❌ 无法使用服务端渲染(SSR)                                       │
│                                                                  │
│  ✅ 纯静态文件托管                                                │
│  ✅ HTML/CSS/JS                                                  │
│  ✅ 图片、视频、字体                                              │
│  ✅ GLTF/GLB 3D模型                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、部署架构

### 2.1 当前架构

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
        ├── npm install
        ├── npm run build
        │
        ▼
   dist/ (构建产物)
        │
        ▼
GitHub Pages
https://slowdown87.github.io/ScadaDemo/
```

### 2.2 Vite配置

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  // GitHub Pages路径
  base: '/ScadaDemo/',

  plugins: [vue()],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },

  build: {
    // 输出目录
    outDir: 'dist',

    // assets目录
    assetsDir: 'assets',

    // 关闭sourcemap减少体积
    sourcemap: false,

    // gzip压缩
    brotliSize: true,

    // 分块配置
    rollupOptions: {
      output: {
        manualChunks: {
          'three': ['three'],
          'echarts': ['echarts', 'vue-echarts']
        }
      }
    }
  },

  // 开发服务器配置
  server: {
    port: 5173,
    open: true
  }
})
```

---

## 三、CI/CD配置

### 3.1 deploy.yml

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: 'pages'
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}

    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build
        env:
          NODE_ENV: production

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './dist'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## 四、模型文件优化

### 4.1 模型大小限制

| 模型类型 | 建议大小 | 最大限制 |
|----------|----------|----------|
| 高模(LOD0) | 2-5MB | 10MB |
| 中模(LOD1) | 500KB-2MB | 5MB |
| 低模(LOD2) | 100-500KB | 1MB |
| **总模型大小** | **< 30MB** | **50MB** |

### 4.2 GLTF/GLB压缩

```bash
# 安装gltf-pipeline
npm install -g gltf-pipeline

# Draco压缩
gltf-pipeline -i model.gltf -o model-compressed.gltf -d

# 转换为glb并压缩
gltf-pipeline -i model.gltf -o model.glb -d
```

### 4.3 模型加载策略

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'

class ModelLoader {
  constructor() {
    this.gltfLoader = new GLTFLoader()
    this.dracoLoader = new DRACOLoader()

    // 使用Draco压缩
    this.dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/')
    this.gltfLoader.setDRACOLoader(this.dracoLoader)
  }

  async loadModel(url) {
    try {
      const gltf = await this.gltfLoader.loadAsync(url)
      return gltf.scene
    } catch (error) {
      console.error('Model loading failed:', error)
      return null
    }
  }

  dispose() {
    this.dracoLoader.dispose()
  }
}
```

### 4.4 LOD分级加载

```javascript
import * as THREE from 'three'
import { LOD } from 'three/examples/jsm/objects/LOD.js'

class LODModelLoader {
  constructor() {
    this.loader = new ModelLoader()
    this.cache = new Map()
  }

  async loadWithLOD(highUrl, mediumUrl, lowUrl) {
    const lod = new LOD()

    // 根据距离加载不同精度模型
    const [high, medium, low] = await Promise.all([
      this.loader.loadModel(highUrl),
      this.loader.loadModel(mediumUrl),
      this.loader.loadModel(lowUrl)
    ])

    lod.addLevel(high, 0)      // 0-20m 高模
    lod.addLevel(medium, 20)    // 20-50m 中模
    lod.addLevel(low, 50)       // 50m+ 低模

    return lod
  }
}
```

---

## 五、代码分割

### 5.1 Vite分块策略

```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 框架
          'vue-vendor': ['vue', 'vue-router', 'pinia'],

              // 3D引擎 - 单独chunk
          'three': ['three'],

              // 图表 - 单独chunk
          'echarts': ['echarts', 'vue-echarts'],

              // 其他 vendor
          'vendor': ['lodash-es', 'dayjs']
        }
      }
    }
  }
})
```

### 5.2 路由懒加载

```javascript
// router/index.js
const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import(/* webpackChunkName: "home" */ '@/views/HomeView.vue')
  },
  {
    path: '/twin',
    name: 'Twin',
    component: () => import(/* webpackChunkName: "twin" */ '@/views/TwinView.vue')
  },
  {
    path: '/perf',
    name: 'Perf',
    component: () => import(/* webpackChunkName: "perf" */ '@/views/PerfView.vue')
  }
]
```

### 5.3 组件懒加载

```vue
<template>
  <Suspense>
    <template #default>
      <AsyncAlarmPopup v-if="showPopup" />
    </template>
    <template #fallback>
      <LoadingSpinner />
    </template>
  </Suspense>
</template>

<script setup>
import { defineAsyncComponent } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

const AsyncAlarmPopup = defineAsyncComponent(() =>
  import('./AlarmPopup.vue')
)
</script>
```

---

## 六、资源优化

### 6.1 图片优化

| 类型 | 格式 | 压缩工具 |
|------|------|----------|
| 照片 | WebP | cwebp |
| 图标 | SVG | svgo |
| 背景 | PNG/SVG | pngquant |

```bash
# 批量压缩PNG
find . -name "*.png" -exec pngquant --quality=65-80 --output {} {} \;

# 转换图片为WebP
cwebp -q 80 input.png -o output.webp
```

### 6.2 字体优化

```css
/* 使用系统字体作为后备 */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
  'Helvetica Neue', Arial, sans-serif;

/* 预加载关键字体 */
<link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>
```

### 6.3 SVG内联

```vue
<!-- 避免使用img标签 -->
<template>
  <!-- ❌ 外部请求 -->
  <img src="/icons/alarm.svg" />

  <!-- ✅ 内联SVG -->
  <svg viewBox="0 0 24 24">
    <path d="M12 2L2 22h20L12 2z" />
  </svg>
</template>
```

---

## 七、缓存策略

### 7.1 静态资源缓存

GitHub Pages自动为静态资源添加缓存，但可以通过文件名hash实现版本控制。

```javascript
// vite.config.js - 添加contenthash
export default defineConfig({
  build: {
    assetFileNames: 'assets/[name]-[hash][extname]',
    chunkFileNames: 'assets/[name]-[hash].js',
    entryFileNames: 'assets/[name]-[hash].js'
  }
})
```

### 7.2 构建输出

```
dist/
├── index.html                    # 无hash，便于缓存
├── assets/
│   ├── home-a1b2c3d4.js         # 有hash，永久缓存
│   ├── twin-e5f6g7h8.js
│   ├── three-i9j0k1l2.js
│   └── echarts-m3n4o5p6.js
```

---

## 八、加载优化

### 8.1 首屏加载策略

```
┌─────────────────────────────────────────────────────────────────┐
│                      首屏加载流程                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. HTML下载      ████░░░░░░░░░░░░░░░░░░░░░  10%                │
│  2. CSS下载       ████████░░░░░░░░░░░░░░░░░░  20%                │
│  3. JS下载(框架)  ████████████████░░░░░░░░░░  40%                │
│  4. JS执行        ████████████████████░░░░░  60%                │
│  5. 路由渲染      ████████████████████████░  80%                │
│  6. 3D场景加载    ██████████████████████████ 100%                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Loading骨架屏

```vue
<template>
  <div class="app">
    <LoadingSkeleton v-if="isLoading" />

    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<style>
/* 骨架屏样式 */
.skeleton {
  background: linear-gradient(90deg, #1a1f3a 25%, #2d3748 50%, #1a1f3a 75%);
  background-size: 200% 100%;
  animation: skeleton-loading 1.5s infinite;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

### 8.3 预加载关键资源

```html
<!-- index.html -->
<head>
  <!-- 预连接 -->
  <link rel="preconnect" href="https://slowdown87.github.io">

  <!-- 预加载关键CSS -->
  <link rel="preload" href="/assets/main.css" as="style">

  <!-- 预加载关键JS -->
  <link rel="modulepreload" href="/assets/main.js">

  <!-- DNS预解析 -->
  <link rel="dns-prefetch" href="//fonts.googleapis.com">
</head>
```

---

## 九、监控与调试

### 9.1 Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse

on: [push]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run build

      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v10
        with:
          urls: https://slowdown87.github.io/ScadaDemo/
          budgetPath: ./lighthouse-budget.json
          uploadArtifacts: true
```

### 9.2 Lighthouse预算

```json
// lighthouse-budget.json
{
  " budgets": [
    {
      "resourceSizes": [
        { "resourceType": "total", "budget": 500 },
        { "resourceType": "script", "budget": 200 },
        { "resourceType": "image", "budget": 100 }
      ]
    }
  ]
}
```

---

## 十、检查清单

### 部署前检查

- [ ] `vite.config.js` base路径正确
- [ ] `deploy.yml` workflow配置正确
- [ ] 模型文件 < 50MB
- [ ] 构建产物 < 100MB
- [ ] 路由使用懒加载
- [ ] 关键资源添加preload

### 构建验证

- [ ] `npm run build` 成功
- [ ] `npm run preview` 本地正常
- [ ] GitHub Actions 部署成功
- [ ] GitHub Pages 可访问
- [ ] 所有路由正常跳转

### 性能验证

- [ ] Lighthouse Performance > 80
- [ ] First Contentful Paint < 3s
- [ ] Largest Contentful Paint < 5s
- [ ] 3D场景加载 < 5s

---

**文档状态**: 草稿
**版本历史**:
- v1.0 (2026-04-24): 初始版本
