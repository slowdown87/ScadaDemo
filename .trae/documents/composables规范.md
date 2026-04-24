# SCADA数字孪生系统 - Composables规范

> 文档版本: v1.0
> 创建日期: 2026-04-24
> 部署方案: 方案1 - 纯前端（GitHub Pages）

---

## 一、概述

### 1.1 什么是Composables

Composables（组合式函数）是Vue3 Composition API的核心特性，用于封装和复用有状态的逻辑。

```javascript
// 传统方式：逻辑分散
export default {
  data() { return { count: 0 } },
  methods: { increment() { this.count++ } }
}

// Composable方式：逻辑集中
function useCounter() {
  const count = ref(0)
  function increment() { count.value++ }
  return { count, increment }
}
```

### 1.2 为什么要用Composables

| 优势 | 说明 |
|------|------|
| **逻辑复用** | 跨组件复用有状态逻辑 |
| **代码组织** | 相关逻辑集中，易于维护 |
| **类型推导** | 更好的TypeScript支持 |
| **Tree-shaking** | 未使用的函数不打包 |

---

## 二、目录结构

```
src/
├── composables/                 # 组合式函数目录
│   ├── useThree.ts            # Three.js场景管理
│   ├── usePlantData.ts        # 工厂数据
│   ├── useAlarm.ts            # 报警管理
│   ├── useECharts.ts          # ECharts封装
│   ├── useInterval.ts         # 定时器
│   └── useRAF.ts              # requestAnimationFrame
│
└── types/
    └── composables.ts         # 类型定义
```

---

## 三、useThree.ts - Three.js场景管理

### 3.1 设计目标

封装Three.js的初始化、渲染循环、资源管理，提供简洁的API。

### 3.2 实现规范

```typescript
// src/composables/useThree.ts

import { ref, shallowRef, onMounted, onUnmounted, type Ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export interface UseThreeOptions {
  container: Ref<HTMLElement | null>
  antialias?: boolean
  alpha?: boolean
  shadowMapEnabled?: boolean
}

export function useThree(options: UseThreeOptions) {
  // 1. 状态 - 使用shallowRef避免深度响应
  const scene = shallowRef<THREE.Scene | null>(null)
  const camera = shallowRef<THREE.PerspectiveCamera | null>(null)
  const renderer = shallowRef<THREE.WebGLRenderer | null>(null)
  const controls = shallowRef<OrbitControls | null>(null)

  // 2. 内部状态
  let animationId: number | null = null
  let isDisposed = false

  // 3. 初始化
  function initScene() {
    const { container, antialias = true, alpha = true, shadowMapEnabled = true } = options

    if (!container.value) {
      console.warn('[useThree] Container is null')
      return
    }

    // 场景
    scene.value = new THREE.Scene()
    if (alpha) {
      scene.value.background = null
    }

    // 相机
    camera.value = new THREE.PerspectiveCamera(
      60,
      container.value.clientWidth / container.value.clientHeight,
      0.1,
      1000
    )
    camera.value.position.set(0, 10, 20)

    // 渲染器
    renderer.value = new THREE.WebGLRenderer({
      antialias,
      alpha,
      powerPreference: 'high-performance'
    })
    renderer.value.setSize(container.value.clientWidth, container.value.clientHeight)
    renderer.value.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    container.value.appendChild(renderer.value.domElement)

    // 阴影
    if (shadowMapEnabled) {
      renderer.value.shadowMap.enabled = true
      renderer.value.shadowMap.type = THREE.PCFSoftShadowMap
    }

    // 控制器
    controls.value = new OrbitControls(camera.value, renderer.value.domElement)
    controls.value.enableDamping = true
    controls.value.dampingFactor = 0.05
  }

  // 4. 渲染循环 - 脏检查优化
  function startRenderLoop() {
    if (isDisposed) return

    const render = () => {
      animationId = requestAnimationFrame(render)

      if (controls.value) {
        controls.value.update()
      }

      if (renderer.value && scene.value && camera.value) {
        renderer.value.render(scene.value, camera.value)
      }
    }

    render()
  }

  // 5. 响应容器大小变化
  function handleResize() {
    if (!container.value || !camera.value || !renderer.value) return

    camera.value.aspect = container.value.clientWidth / container.value.clientHeight
    camera.value.updateProjectionMatrix()
    renderer.value.setSize(container.value.clientWidth, container.value.clientHeight)
  }

  // 6. 清理资源
  function dispose() {
    isDisposed = true

    if (animationId !== null) {
      cancelAnimationFrame(animationId)
    }

    if (controls.value) {
      controls.value.dispose()
    }

    if (renderer.value) {
      renderer.value.dispose()
      renderer.value.forceContextLoss()
      if (options.container.value && renderer.value.domElement) {
        options.container.value.removeChild(renderer.value.domElement)
      }
    }

    scene.value?.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.geometry?.dispose()
        if (Array.isArray(object.material)) {
          object.material.forEach(m => m.dispose())
        } else {
          object.material?.dispose()
        }
      }
    })

    scene.value?.clear()
    scene.value = null
    camera.value = null
    renderer.value = null
    controls.value = null
  }

  // 7. 生命周期
  onMounted(() => {
    initScene()
    startRenderLoop()
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    dispose()
    window.removeEventListener('resize', handleResize)
  })

  // 8. 返回API
  return {
    scene,
    camera,
    renderer,
    controls,
    dispose
  }
}
```

### 3.3 使用示例

```vue
<template>
  <div ref="containerRef" class="three-container" />
</template>

<script setup>
import { ref } from 'vue'
import { useThree } from '@/composables/useThree'
import * as THREE from 'three'

const containerRef = ref(null)

const { scene, camera, renderer, dispose } = useThree({
  container: containerRef,
  antialias: true,
  shadowMapEnabled: true
})

// 添加自定义对象
onMounted(() => {
  const geometry = new THREE.BoxGeometry(1, 1, 1)
  const material = new THREE.MeshStandardMaterial({ color: 0x2196F3 })
  const cube = new THREE.Mesh(geometry, material)
  scene.value?.add(cube)
})
</script>
```

---

## 四、usePlantData.ts - 工厂数据

### 4.1 设计目标

封装工厂数据的获取、订阅、更新逻辑。

### 4.2 实现规范

```typescript
// src/composables/usePlantData.ts

import { ref, computed, onUnmounted, type Ref } from 'vue'
import { usePlantStore } from '@/stores/plantStore'

export interface PlantData {
  temperature: number
  pressure: number
  level: number
  flowRate: number
}

export function usePlantData() {
  const store = usePlantStore()

  // 响应式数据
  const data = computed(() => ({
    temperature: parseFloat(store.reactorTemp),
    pressure: parseFloat(store.reactorPressure),
    level: parseFloat(store.tankLevel),
    flowRate: parseFloat(store.flowRate)
  }))

  // 运行状态
  const isRunning = computed(() => store.isRunning)

  // 报警状态
  const hasAlarms = computed(() => store.hasAlarms)
  const alarms = computed(() => store.alarms)

  // 历史数据
  const temperatureHistory = computed(() => store.temperatureHistory)
  const pressureHistory = computed(() => store.pressureHistory)
  const levelHistory = computed(() => store.levelHistory)

  // 操作方法
  function startPlant() {
    store.startSimulation()
  }

  function stopPlant() {
    store.stopSimulation()
  }

  function resetPlant() {
    store.resetSimulation()
  }

  return {
    data,
    isRunning,
    hasAlarms,
    alarms,
    temperatureHistory,
    pressureHistory,
    levelHistory,
    startPlant,
    stopPlant,
    resetPlant
  }
}
```

### 4.3 使用示例

```vue
<template>
  <div class="plant-data">
    <div>温度: {{ data.temperature.toFixed(1) }}°C</div>
    <div>压力: {{ data.pressure.toFixed(2) }}MPa</div>
    <div>液位: {{ data.level.toFixed(1) }}%</div>
    <button @click="isRunning ? stopPlant() : startPlant()">
      {{ isRunning ? '停止' : '启动' }}
    </button>
  </div>
</template>

<script setup>
import { usePlantData } from '@/composables/usePlantData'

const { data, isRunning, startPlant, stopPlant } = usePlantData()
</script>
```

---

## 五、useECharts.ts - ECharts封装

### 5.1 设计目标

封装ECharts的创建、更新、销毁逻辑，支持高频更新优化。

### 5.2 实现规范

```typescript
// src/composables/useECharts.ts

import { ref, shallowRef, onMounted, onUnmounted, watch, type Ref, type ShallowRef } from 'vue'
import * as echarts from 'echarts'

export interface UseEChartsOptions {
  renderer?: 'canvas' | 'svg'
  autoresize?: boolean
}

export function useECharts(
  containerRef: Ref<HTMLElement | null>,
  options: UseEChartsOptions = {}
) {
  const { renderer = 'canvas', autoresize = true } = options

  // 使用shallowRef避免深度响应
  const chartInstance = shallowRef<echarts.ECharts | null>(null)
  const isReady = ref(false)

  // 初始化
  function initChart() {
    if (!containerRef.value) {
      console.warn('[useECharts] Container is null')
      return
    }

    chartInstance.value = echarts.init(containerRef.value, undefined, {
      renderer,
      width: autoresize ? undefined : containerRef.value.clientWidth,
      height: autoresize ? undefined : containerRef.value.clientHeight
    })

    isReady.value = true
  }

  // 设置配置
  function setOption(option: echarts.EChartsCoreOption, notMerge = false) {
    if (!chartInstance.value) return
    chartInstance.value.setOption(option, { notMerge })
  }

  // 响应容器大小变化
  function handleResize() {
    if (!chartInstance.value || !autoresize) return
    chartInstance.value.resize()
  }

  // 清理
  function dispose() {
    if (chartInstance.value) {
      chartInstance.value.dispose()
      chartInstance.value = null
      isReady.value = false
    }
  }

  // 生命周期
  onMounted(() => {
    initChart()
    if (autoresize) {
      window.addEventListener('resize', handleResize)
    }
  })

  onUnmounted(() => {
    dispose()
    if (autoresize) {
      window.removeEventListener('resize', handleResize)
    }
  })

  return {
    chartInstance,
    isReady,
    setOption,
    resize: handleResize,
    dispose
  }
}
```

### 5.3 高频更新示例

```typescript
// 在组件中使用
const { chartInstance, setOption } = useECharts(chartRef)

// 批量更新
let dataBuffer: number[] = []
const UPDATE_INTERVAL = 100

setInterval(() => {
  dataBuffer.push(Math.random() * 100)

  // 限制数据点数量
  if (dataBuffer.length > 100) {
    dataBuffer.shift()
  }

  setOption({
    series: [{
      data: dataBuffer
    }]
  })
}, UPDATE_INTERVAL)
```

---

## 六、useInterval.ts - 定时器

### 6.1 实现规范

解决setInterval在页面隐藏时的问题。

```typescript
// src/composables/useInterval.ts

import { ref, onUnmounted } from 'vue'

export function useInterval(callback: () => void, delay: number) {
  const isActive = ref(false)
  let timerId: ReturnType<typeof setInterval> | null = null

  function start() {
    if (isActive.value) return
    isActive.value = true
    timerId = setInterval(callback, delay)
  }

  function stop() {
    if (timerId !== null) {
      clearInterval(timerId)
      timerId = null
    }
    isActive.value = false
  }

  function restart() {
    stop()
    start()
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isActive,
    start,
    stop,
    restart
  }
}
```

### 6.2 使用示例

```typescript
const { isActive, start, stop } = useInterval(() => {
  // 更新数据
  updateSensorData()
}, 100)

start()
```

---

## 七、useRAF.ts - RAF封装

### 7.1 实现规范

封装requestAnimationFrame，提供暂停/恢复能力。

```typescript
// src/composables/useRAF.ts

import { ref, onUnmounted } from 'vue'

export function useRAF(callback: (deltaTime: number) => void) {
  const isRunning = ref(false)
  let animationId: number | null = null
  let lastTime = 0

  function tick(timestamp: number) {
    if (!isRunning.value) return

    const deltaTime = lastTime ? timestamp - lastTime : 0
    lastTime = timestamp

    callback(deltaTime)

    animationId = requestAnimationFrame(tick)
  }

  function start() {
    if (isRunning.value) return
    isRunning.value = true
    lastTime = 0
    animationId = requestAnimationFrame(tick)
  }

  function stop() {
    isRunning.value = false
    if (animationId !== null) {
      cancelAnimationFrame(animationId)
      animationId = null
    }
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isRunning,
    start,
    stop
  }
}
```

### 7.2 使用示例

```typescript
const { isRunning, start, stop } = useRAF((deltaTime) => {
  // deltaTime 单位ms
  mesh.rotation.y += deltaTime * 0.001
})

start()
```

---

## 八、Composables最佳实践

### 8.1 命名规范

| 规则 | 正确 | 错误 |
|------|------|------|
| 文件名 | `useXxx.ts` | `xxx.ts`, `UseXxx.ts` |
| 函数名 | `useXxx()` | `getXxx()`, `createXxx()` |
| 返回值 | 解构使用 | 直接返回ref |

### 8.2 状态管理

```typescript
// ✅ 推荐：返回响应式对象
function useCounter() {
  const count = ref(0)
  return { count }
}

// 使用
const { count } = useCounter()

// ❌ 避免：返回内部ref
function useCounter() {
  const count = ref(0)
  return { countRef: count }  // 不要这样
}
```

### 8.3 生命周期

```typescript
// ✅ 推荐：在composable内部处理生命周期
function useEventListener(event: string, handler: () => void) {
  onMounted(() => {
    window.addEventListener(event, handler)
  })
  onUnmounted(() => {
    window.removeEventListener(event, handler)
  })
}

// ❌ 避免：让调用者处理
function useEventListener(event: string, handler: () => void) {
  return {
    bind: () => window.addEventListener(event, handler),
    unbind: () => window.removeEventListener(event, handler)
  }
}
```

### 8.4 配置参数

```typescript
// ✅ 推荐：接受配置对象
function useThree(options: UseThreeOptions) {
  const { container, width, height, antialias = true } = options
}

// ❌ 避免：大量可选参数
function useThree(container, width?, height?, antialias?, ...)
```

---

## 九、类型定义

```typescript
// src/types/composables.ts

import type { Ref, ShallowRef, ComputedRef } from 'vue'

// useThree
export interface UseThreeOptions {
  container: Ref<HTMLElement | null>
  antialias?: boolean
  alpha?: boolean
  shadowMapEnabled?: boolean
}

export interface UseThreeReturn {
  scene: ShallowRef<THREE.Scene | null>
  camera: ShallowRef<THREE.PerspectiveCamera | null>
  renderer: ShallowRef<THREE.WebGLRenderer | null>
  controls: ShallowRef<OrbitControls | null>
  dispose: () => void
}

// useECharts
export interface UseEChartsOptions {
  renderer?: 'canvas' | 'svg'
  autoresize?: boolean
}

export interface UseEChartsReturn {
  chartInstance: ShallowRef<echarts.ECharts | null>
  isReady: Ref<boolean>
  setOption: (option: echarts.EChartsCoreOption, notMerge?: boolean) => void
  resize: () => void
  dispose: () => void
}

// usePlantData
export interface PlantData {
  temperature: number
  pressure: number
  level: number
  flowRate: number
}

export interface UsePlantDataReturn {
  data: ComputedRef<PlantData>
  isRunning: ComputedRef<boolean>
  hasAlarms: ComputedRef<boolean>
  alarms: ComputedRef<Alarm[]>
  startPlant: () => void
  stopPlant: () => void
  resetPlant: () => void
}
```

---

## 十、现有文件整合

### 10.1 待创建的文件清单

| 文件 | 优先级 | 依赖 |
|------|--------|------|
| `useRAF.ts` | 高 | - |
| `useInterval.ts` | 高 | - |
| `useECharts.ts` | 高 | echarts |
| `useThree.ts` | 高 | three.js |
| `usePlantData.ts` | 中 | plantStore |
| `useAlarm.ts` | 中 | alarmStore |

### 10.2 现有代码迁移

```typescript
// 旧代码
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  setup() {
    let animationId = null

    onMounted(() => {
      const animate = () => {
        animationId = requestAnimationFrame(animate)
      }
      animate()
    })

    onUnmounted(() => {
      if (animationId) cancelAnimationFrame(animationId)
    })

    return {}
  }
}

// 新代码
import { useRAF } from '@/composables/useRAF'

export default {
  setup() {
    const { start, stop } = useRAF((dt) => {
      // 动画逻辑
    })

    onMounted(() => start())

    return {}
  }
}
```

---

**文档状态**: 草稿
**版本历史**:
- v1.0 (2026-04-24): 初始版本
