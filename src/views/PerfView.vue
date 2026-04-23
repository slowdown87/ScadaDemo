<template>
  <div class="perf-container">
    <SideNav />
    <main class="main-content">
      <header class="top-bar">
        <div class="header-left">
          <h1 class="page-title">◆ 性能监控系统</h1>
          <span class="page-subtitle">方案C - 高频数据实时监控</span>
        </div>
        <div class="header-right">
          <div class="control-buttons">
            <button
              class="ctrl-btn"
              :class="{ active: isRunning }"
              @click="toggleMonitor"
            >
              {{ isRunning ? '⏸ 暂停' : '▶ 开始' }}
            </button>
            <button class="ctrl-btn reset" @click="resetData">
              ↻ 重置
            </button>
          </div>
        </div>
      </header>

      <div class="perf-content">
        <div class="main-grid">
          <div class="left-panel">
            <MetricsPanel
              :metrics="metrics"
              :fps-history="fpsHistory"
              :is-running="isRunning"
            />
          </div>

          <div class="right-panel">
            <RealtimeChart
              title="温度监控"
              :data="temperatureHistory"
              :current-value="currentTemperature"
              unit="°C"
              :max-value="100"
              color="#ff6b6b"
            />
            <RealtimeChart
              title="压力监控"
              :data="pressureHistory"
              :current-value="currentPressure"
              unit="atm"
              :max-value="2.5"
              color="#4ecdc4"
            />
            <RealtimeChart
              title="流量监控"
              :data="flowHistory"
              :current-value="currentFlow"
              unit="L/s"
              :max-value="20"
              color="#45b7d1"
            />
          </div>
        </div>

        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-label">监测时长</span>
            <span class="stat-value">{{ duration }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">数据更新</span>
            <span class="stat-value">{{ metrics.updateRate }} /s</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">峰值FPS</span>
            <span class="stat-value">{{ peakFps }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">平均FPS</span>
            <span class="stat-value">{{ averageFps }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { highFreqSimulator } from '@/mock/highFreqMock'
import SideNav from '@/components/SideNav.vue'
import MetricsPanel from '@/components/MetricsPanel.vue'
import RealtimeChart from '@/components/RealtimeChart.vue'

const isRunning = ref(false)
const metrics = ref({ fps: 0, frameTime: 0, updateRate: 0, memory: 0, dataPoints: 0 })
const temperatureHistory = ref([])
const pressureHistory = ref([])
const flowHistory = ref([])
const fpsHistory = ref([])
const currentTemperature = ref(25)
const currentPressure = ref(1.0)
const currentFlow = ref(0)
const startTime = ref(null)
const duration = ref('00:00:00')
let durationInterval = null
let peakFps = ref(0)
let fpsSamples = ref([])

function handleData(type, data) {
  if (type === 'metrics') {
    metrics.value = data
    fpsHistory.value = [...data.fps > 0 ? [...fpsHistory.value, data.fps] : fpsHistory.value]
    if (fpsHistory.value.length > 100) {
      fpsHistory.value = fpsHistory.value.slice(-100)
    }
    fpsSamples.value.push(data.fps)
    if (data.fps > peakFps.value) {
      peakFps.value = data.fps
    }
  } else if (type === 'data') {
    temperatureHistory.value = [...data.history.temperature]
    pressureHistory.value = [...data.history.pressure]
    flowHistory.value = [...data.history.flow]
    currentTemperature.value = data.temperature
    currentPressure.value = data.pressure
    currentFlow.value = data.flow
  }
}

const averageFps = computed(() => {
  if (fpsSamples.value.length === 0) return 0
  const sum = fpsSamples.value.reduce((a, b) => a + b, 0)
  return Math.round(sum / fpsSamples.value.length)
})

function toggleMonitor() {
  if (isRunning.value) {
    highFreqSimulator.stop()
    stopDurationTimer()
  } else {
    highFreqSimulator.start()
    startDurationTimer()
  }
  isRunning.value = !isRunning.value
}

function resetData() {
  highFreqSimulator.reset()
  fpsHistory.value = []
  fpsSamples.value = []
  peakFps.value = 0
  duration.value = '00:00:00'
  startTime.value = Date.now()
}

function startDurationTimer() {
  startTime.value = Date.now()
  durationInterval = setInterval(updateDuration, 1000)
}

function stopDurationTimer() {
  if (durationInterval) {
    clearInterval(durationInterval)
    durationInterval = null
  }
}

function updateDuration() {
  if (!startTime.value) return
  const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
  const hours = Math.floor(elapsed / 3600)
  const minutes = Math.floor((elapsed % 3600) / 60)
  const seconds = elapsed % 60
  duration.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

onMounted(() => {
  highFreqSimulator.addListener(handleData)
  highFreqSimulator.start()
  isRunning.value = true
  startDurationTimer()
})

onUnmounted(() => {
  highFreqSimulator.stop()
  highFreqSimulator.removeListener(handleData)
  stopDurationTimer()
})
</script>

<style scoped>
.perf-container {
  display: flex;
  width: 100%;
  height: 100%;
  background: var(--color-bg);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: auto;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.3);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 3px;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 170, 255, 0.4);
}

.page-subtitle {
  font-size: 12px;
  color: var(--color-text-dim);
  letter-spacing: 1px;
}

.header-right {
  display: flex;
  align-items: center;
}

.control-buttons {
  display: flex;
  gap: 10px;
}

.ctrl-btn {
  background: rgba(0, 170, 255, 0.2);
  border: 1px solid rgba(0, 170, 255, 0.5);
  color: #00aaff;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.ctrl-btn:hover {
  background: rgba(0, 170, 255, 0.3);
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.3);
}

.ctrl-btn.active {
  background: rgba(54, 211, 153, 0.2);
  border-color: rgba(54, 211, 153, 0.5);
  color: #36d399;
}

.ctrl-btn.reset {
  background: rgba(243, 156, 18, 0.2);
  border-color: rgba(243, 156, 18, 0.5);
  color: #f39c12;
}

.ctrl-btn.reset:hover {
  background: rgba(243, 156, 18, 0.3);
  box-shadow: 0 0 15px rgba(243, 156, 18, 0.3);
}

.perf-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.main-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 350px 1fr;
  gap: 20px;
}

.left-panel {
  display: flex;
  flex-direction: column;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  padding: 15px;
  background: rgba(26, 34, 53, 0.9);
  border: 1px solid rgba(0, 170, 255, 0.3);
  border-radius: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.stat-label {
  color: #5a6a8a;
  font-size: 11px;
  text-transform: uppercase;
}

.stat-value {
  color: #00aaff;
  font-size: 18px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

@media (max-width: 1200px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}
</style>
