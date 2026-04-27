<template>
  <div class="perf-container">
    <header class="top-bar">
      <div class="header-left">
        <h1 class="page-title">性能监控系统</h1>
        <span class="page-subtitle">高频数据实时监控</span>
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
            color="var(--color-danger)"
          />
          <RealtimeChart
            title="压力监控"
            :data="pressureHistory"
            :current-value="currentPressure"
            unit="atm"
            :max-value="2.5"
            color="var(--color-primary)"
          />
          <RealtimeChart
            title="流量监控"
            :data="flowHistory"
            :current-value="currentFlow"
            unit="L/s"
            :max-value="20"
            color="var(--color-accent)"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { highFreqSimulator } from '@/mock/highFreqMock'
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
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: transparent;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
  position: relative;
}

.top-bar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), transparent);
  border-radius: 1px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 2px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title::before {
  content: '◆';
  color: var(--color-primary);
  font-size: 18px;
}

.page-subtitle {
  font-size: 12px;
  color: var(--color-text-tertiary);
  letter-spacing: 1px;
  margin-left: 28px;
}

.header-right {
  display: flex;
  align-items: center;
}

.control-buttons {
  display: flex;
  gap: 8px;
  padding: 6px;
  background: var(--color-bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
}

.ctrl-btn {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  gap: 6px;
}

.ctrl-btn:hover {
  background: rgba(0, 170, 255, 0.1);
  color: var(--color-text-primary);
}

.ctrl-btn.active {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-600));
  color: white;
  box-shadow: 0 2px 8px rgba(54, 211, 153, 0.3);
}

.ctrl-btn.reset {
  color: var(--color-warning);
}

.ctrl-btn.reset:hover {
  background: rgba(250, 173, 20, 0.1);
}

.perf-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: hidden;
}

.main-grid {
  flex: 1;
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
  overflow: hidden;
}

.left-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.right-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
}

.stats-bar {
  display: flex;
  justify-content: space-around;
  padding: 16px 24px;
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  box-shadow: var(--shadow-md);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.stat-label {
  color: var(--color-text-tertiary);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.stat-value {
  color: var(--color-primary);
  font-size: 18px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

@media (max-width: 1400px) {
  .main-grid {
    grid-template-columns: 1fr;
  }

  .left-panel {
    max-height: 300px;
  }
}

@media (max-width: 1024px) {
  .top-bar {
    flex-direction: column;
    gap: 12px;
  }

  .page-title {
    font-size: 18px;
  }

  .stats-bar {
    flex-wrap: wrap;
    gap: 16px;
  }
}
</style>
