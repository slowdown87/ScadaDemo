<template>
  <div class="home-container">
    <header class="top-bar">
      <div class="header-left">
        <h1 class="page-title">工艺流程监控</h1>
        <span class="page-subtitle">实时状态 · 数据采集 · 报警管理</span>
      </div>
      <div class="header-right">
        <div class="system-info">
          <span class="info-item">
            <svg viewBox="0 0 24 24" width="14" height="14">
              <path fill="currentColor" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6M12,8A4,4 0 0,0 8,12A4,4 0 0,0 12,16A4,4 0 0,0 16,12A4,4 0 0,0 12,8Z"/>
            </svg>
            {{ systemTime }}
          </span>
        </div>
      </div>
    </header>

    <div class="dashboard-grid">
      <div class="plant-section">
        <PlantView
          :is-running="store.running"
          :tank-level="store.tankLevel"
          :tank-b-level="75"
          :flow-rate="store.flowRate"
          :flow-rate-b="8"
          :reactor-temp="store.reactorTemp"
          :reactor-pressure="store.reactorPressure"
          :motor-speed="store.motorSpeed"
          :product-count="store.productCount"
          :sep-level="50"
          :storage-level="100"
          :alarms="store.alarms"
        />
      </div>

      <div class="control-section">
        <ControlPanel
          :is-running="store.running"
          :runtime="runtime"
          :total-product="store.productTotal"
          :alarm-count="store.alarmHistory.length"
          @start="handleStart"
          @stop="handleStop"
          @reset="handleReset"
          @toggle="handleToggle"
        />
      </div>

      <div class="data-section">
        <DataPanel
          :tank-level="store.tankLevel"
          :flow-rate="store.flowRate"
          :reactor-temp="store.reactorTemp"
          :reactor-pressure="store.reactorPressure"
          :motor-speed="store.motorSpeed"
          :product-count="store.productCount"
          :product-rate="store.productRate"
          :system-time="store.systemTime"
        />
      </div>

      <div class="alarm-section">
        <AlarmPanel
          :alarms="store.alarms"
          :alarm-history="store.alarmHistory"
          @acknowledge="handleAckAlarm"
          @acknowledge-all="handleAckAll"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePlantStore } from '@/stores/plantStore'
import PlantView from '@/components/PlantView.vue'
import ControlPanel from '@/components/ControlPanel.vue'
import DataPanel from '@/components/DataPanel.vue'
import AlarmPanel from '@/components/AlarmPanel.vue'

const store = usePlantStore()

const runtime = ref('00:00:00')
let runtimeInterval = null
let startTime = null

const systemTime = computed(() => store.systemTime)

function handleStart() {
  store.start()
  startRuntimeTimer()
}

function handleStop() {
  store.stop()
  stopRuntimeTimer()
}

function handleReset() {
  store.reset()
  resetRuntime()
}

function handleToggle() {
  store.toggle()
  if (store.running) {
    startRuntimeTimer()
  } else {
    stopRuntimeTimer()
  }
}

function handleAckAlarm(alarmId) {
  store.acknowledgeAlarm(alarmId)
}

function handleAckAll() {
  store.acknowledgeAll()
}

function startRuntimeTimer() {
  if (runtimeInterval) return
  startTime = Date.now()
  runtimeInterval = setInterval(updateRuntime, 1000)
}

function stopRuntimeTimer() {
  if (runtimeInterval) {
    clearInterval(runtimeInterval)
    runtimeInterval = null
  }
}

function resetRuntime() {
  stopRuntimeTimer()
  runtime.value = '00:00:00'
  startTime = null
}

function updateRuntime() {
  if (!startTime) return
  const elapsed = Math.floor((Date.now() - startTime) / 1000)
  const hours = Math.floor(elapsed / 3600)
  const minutes = Math.floor((elapsed % 3600) / 60)
  const seconds = elapsed % 60
  runtime.value = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
}

onMounted(() => {
  store.initStore()
  if (store.running) {
    startRuntimeTimer()
  }
})

onUnmounted(() => {
  store.cleanup()
  stopRuntimeTimer()
})
</script>

<style scoped>
.home-container {
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

.system-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: var(--color-bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--color-border-light);
  border-radius: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
}

.info-item svg {
  color: var(--color-primary);
  opacity: 0.8;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.dashboard-grid {
  flex: 1;
  display: grid;
  grid-template-columns: minmax(600px, 1fr) 380px;
  grid-template-rows: 1fr auto;
  gap: 20px;
}

.plant-section {
  grid-column: 1;
  grid-row: 1 / 3;
  min-height: 400px;
}

.control-section {
  grid-column: 2;
  grid-row: 1;
}

.data-section {
  grid-column: 2;
  grid-row: 2;
}

.alarm-section {
  grid-column: 1 / -1;
  grid-row: 3;
}

@media (max-width: 1400px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto auto;
  }

  .plant-section {
    grid-column: 1;
    grid-row: 1;
    min-height: 350px;
  }

  .control-section {
    grid-column: 1;
    grid-row: 2;
  }

  .data-section {
    grid-column: 1;
    grid-row: 3;
  }

  .alarm-section {
    grid-column: 1;
    grid-row: 4;
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

  .system-info {
    align-self: flex-start;
  }
}
</style>
