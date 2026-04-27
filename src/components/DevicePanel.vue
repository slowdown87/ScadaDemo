<template>
  <Transition name="panel">
    <div v-if="visible" class="device-panel" :class="deviceClass">
      <div class="panel-header">
        <div class="device-info">
          <span class="device-icon">{{ deviceIcon }}</span>
          <div class="device-title">
            <span class="device-name">{{ deviceName }}</span>
            <span class="device-id">{{ deviceId }}</span>
          </div>
        </div>
        <button class="close-btn" @click="handleClose">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"/>
          </svg>
        </button>
      </div>

      <div class="panel-body">
        <div class="status-section">
          <div class="status-badge" :class="statusClass">
            <span class="status-dot"></span>
            <span class="status-text">{{ statusText }}</span>
          </div>
        </div>

        <div class="data-grid">
          <div
            v-for="item in displayData"
            :key="item.key"
            class="data-item"
            :class="{ warning: item.isWarning, danger: item.isDanger }"
          >
            <span class="data-label">{{ item.label }}</span>
            <div class="data-value-row">
              <span class="data-value">{{ item.value }}</span>
              <span class="data-unit">{{ item.unit }}</span>
            </div>
            <div class="data-bar" v-if="item.max">
              <div class="data-bar-fill" :style="{ width: item.percent + '%' }"></div>
            </div>
          </div>
        </div>

        <div class="chart-section" v-if="hasChart">
          <div class="chart-header">
            <span class="chart-title">{{ chartTitle }}</span>
          </div>
          <div class="chart-container" ref="chartContainer"></div>
        </div>

        <div class="control-section" v-if="isControllable">
          <div class="control-header">
            <span>控制面板</span>
          </div>

          <div class="control-item" v-if="hasSpeedControl">
            <label>{{ controlLabels.speed }}</label>
            <div class="slider-control">
              <input
                type="range"
                :min="0"
                :max="1500"
                :value="controlValues.speed"
                @input="handleSpeedChange"
              />
              <span class="slider-value">{{ controlValues.speed }} RPM</span>
            </div>
          </div>

          <div class="control-item" v-if="hasValveControl">
            <label>{{ controlLabels.valve }}</label>
            <div class="slider-control">
              <input
                type="range"
                :min="0"
                :max="100"
                :value="controlValues.valve"
                @input="handleValveChange"
              />
              <span class="slider-value">{{ controlValues.valve }}%</span>
            </div>
          </div>

          <div class="control-buttons">
            <button
              class="ctrl-btn start"
              :disabled="isRunning"
              @click="handleStart"
            >
              <span>▶</span> 启动
            </button>
            <button
              class="ctrl-btn stop"
              :disabled="!isRunning"
              @click="handleStop"
            >
              <span>■</span> 停止
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useECharts } from '@/composables/useECharts'

const props = defineProps({
  visible: { type: Boolean, default: false },
  device: { type: Object, default: null }
})

const emit = defineEmits(['close', 'control'])

const chartContainer = ref(null)
const controlValues = ref({
  speed: 0,
  valve: 0
})

const { chartInstance, setOption, appendData, updateSeriesData, resize } = useECharts(chartContainer, {
  autoresize: true,
  manualUpdate: true
})

const deviceConfig = {
  reactor: {
    icon: '⚗️',
    name: '反应釜',
    hasChart: true,
    chartTitle: '温度趋势',
    hasSpeedControl: true,
    hasValveControl: false,
    dataKeys: ['temp', 'pressure']
  },
  tank: {
    icon: '🛢️',
    name: '储罐',
    hasChart: true,
    chartTitle: '液位趋势',
    hasSpeedControl: false,
    hasValveControl: false,
    dataKeys: ['level']
  },
  conveyor: {
    icon: '🏭',
    name: '传送带',
    hasChart: false,
    hasSpeedControl: true,
    hasValveControl: false,
    dataKeys: ['speed', 'products']
  },
  valve: {
    icon: '🔧',
    name: '阀门',
    hasChart: false,
    hasSpeedControl: false,
    hasValveControl: true,
    dataKeys: ['position']
  }
}

const deviceType = computed(() => props.device?.type || 'reactor')
const deviceId = computed(() => props.device?.id || 'R-101')
const config = computed(() => deviceConfig[deviceType.value] || deviceConfig.reactor)

const deviceIcon = computed(() => config.value.icon)
const deviceName = computed(() => config.value.name)
const deviceClass = computed(() => deviceType.value)
const hasChart = computed(() => config.value.hasChart)
const chartTitle = computed(() => config.value.chartTitle || '趋势')
const hasSpeedControl = computed(() => config.value.hasSpeedControl)
const hasValveControl = computed(() => config.value.hasValveControl)
const isControllable = computed(() => hasSpeedControl.value || hasValveControl.value)

const isRunning = computed(() => props.device?.running || false)

const statusText = computed(() => {
  if (!props.device) return '离线'
  if (props.device.alarm) return '报警'
  if (isRunning.value) return '运行中'
  return '停止'
})

const statusClass = computed(() => {
  if (props.device?.alarm) return 'alarm'
  if (isRunning.value) return 'running'
  return 'stopped'
})

const displayData = computed(() => {
  if (!props.device?.data) return []

  const data = props.device.data
  const type = deviceType.value

  const items = []

  if (type === 'reactor' || type === 'tank') {
    items.push({
      key: 'temp',
      label: '温度',
      value: (data.temp || 0).toFixed(1),
      unit: '°C',
      isWarning: data.temp > 60,
      isDanger: data.temp > 80,
      max: 120,
      percent: Math.min(100, (data.temp / 120) * 100)
    })
  }

  if (type === 'tank') {
    items.push({
      key: 'level',
      label: '液位',
      value: (data.level || 0).toFixed(1),
      unit: '%',
      isWarning: data.level > 80 || data.level < 20,
      isDanger: data.level > 95 || data.level < 10,
      max: 100,
      percent: Math.min(100, data.level)
    })
  }

  if (type === 'reactor') {
    items.push({
      key: 'pressure',
      label: '压力',
      value: (data.pressure || 0).toFixed(2),
      unit: 'atm',
      isWarning: data.pressure > 1.5,
      isDanger: data.pressure > 1.8,
      max: 2,
      percent: Math.min(100, (data.pressure / 2) * 100)
    })
  }

  if (type === 'conveyor') {
    items.push({
      key: 'speed',
      label: '速度',
      value: (data.speed || 0).toFixed(0),
      unit: 'RPM',
      max: 1500,
      percent: Math.min(100, (data.speed / 1500) * 100)
    })
    items.push({
      key: 'products',
      label: '产量',
      value: (data.products || 0).toFixed(0),
      unit: '件'
    })
  }

  return items
})

const controlLabels = computed(() => ({
  speed: deviceType.value === 'conveyor' ? '传送速度' : '搅拌速度',
  valve: '阀门开度'
}))

function handleClose() {
  emit('close')
}

function handleSpeedChange(e) {
  controlValues.value.speed = parseInt(e.target.value)
  emit('control', { type: 'speed', value: controlValues.value.speed })
}

function handleValveChange(e) {
  controlValues.value.valve = parseInt(e.target.value)
  emit('control', { type: 'valve', value: controlValues.value.valve })
}

function handleStart() {
  emit('control', { type: 'start' })
}

function handleStop() {
  emit('control', { type: 'stop' })
}

const chartColors = {
  axisLine: '#5a7a9a',
  splitLine: '#1a2a4a',
  axisLabel: '#5a7a9a',
  line: 'var(--color-primary)',
  areaTop: 'rgba(0, 170, 255, 0.3)',
  areaBottom: 'rgba(0, 170, 255, 0.05)'
}

function updateChartData() {
  if (!hasChart.value || !props.device?.history) return

  const history = props.device.history || []

  if (history.length <= 1) {
    setOption({
      grid: { top: 10, right: 10, bottom: 20, left: 40 },
      xAxis: {
        type: 'category',
        data: history.map((_, i) => i.toString()),
        axisLine: { lineStyle: { color: chartColors.axisLine } },
        axisLabel: { color: chartColors.axisLabel, fontSize: 10 },
        show: false
      },
      yAxis: {
        type: 'value',
        axisLine: { show: false },
        splitLine: { lineStyle: { color: chartColors.splitLine, type: 'dashed' } },
        axisLabel: { color: chartColors.axisLabel, fontSize: 10 }
      },
      series: [{
        data: history,
        type: 'line',
        smooth: true,
        symbol: 'none',
        lineStyle: { color: chartColors.line, width: 2 },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: chartColors.areaTop },
              { offset: 1, color: chartColors.areaBottom }
            ]
          }
        }
      }]
    })
  } else {
    updateSeriesData(0, history)
  }
}

watch(() => props.device?.data, () => {
  if (props.device?.history) {
    updateChartData()
  }
}, { deep: true })

watch(() => props.visible, (val) => {
  if (val) {
    nextTick(() => {
      if (hasChart.value) {
        updateChartData()
      }
    })
  }
})

watch(() => props.device?.controlValues, (val) => {
  if (val) {
    controlValues.value = { ...val }
  }
}, { deep: true, immediate: true })
</script>

<style scoped>
.device-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 320px;
  background: rgba(15, 20, 35, 0.95);
  border: 1px solid rgba(0, 170, 255, 0.4);
  border-radius: 12px;
  overflow: hidden;
  backdrop-filter: blur(15px);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 100;
}

.device-panel.valve {
  border-color: rgba(255, 159, 67, 0.4);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: rgba(0, 170, 255, 0.1);
  border-bottom: 1px solid rgba(0, 170, 255, 0.2);
}

.device-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.device-icon {
  font-size: 28px;
}

.device-title {
  display: flex;
  flex-direction: column;
}

.device-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.device-id {
  font-size: 11px;
  color: var(--color-text-tertiary);
  font-family: 'Courier New', monospace;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--color-text-tertiary);
  cursor: pointer;
  padding: 5px;
  border-radius: 5px;
  transition: all var(--transition-fast);
}

.close-btn:hover {
  color: var(--color-danger);
  background: rgba(255, 71, 87, 0.1);
}

.panel-body {
  padding: 15px;
  max-height: 500px;
  overflow-y: auto;
}

.status-section {
  margin-bottom: 15px;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.running {
  background: rgba(54, 211, 153, 0.15);
  color: var(--color-accent);
}

.status-badge.stopped {
  background: rgba(74, 85, 104, 0.15);
  color: var(--color-text-tertiary);
}

.status-badge.alarm {
  background: rgba(255, 71, 87, 0.15);
  color: var(--color-danger);
  animation: alarm-pulse 1s infinite;
}

@keyframes alarm-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.status-badge.running .status-dot {
  animation: dot-pulse 1.5s infinite;
}

@keyframes dot-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.data-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 15px;
}

.data-item {
  background: var(--color-bg-secondary);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--color-border-light);
}

.data-item.warning {
  border-color: rgba(255, 159, 67, 0.3);
  background: rgba(255, 159, 67, 0.05);
}

.data-item.danger {
  border-color: rgba(255, 71, 87, 0.3);
  background: rgba(255, 71, 87, 0.05);
}

.data-label {
  display: block;
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-bottom: 5px;
}

.data-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.data-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  font-family: 'Courier New', monospace;
}

.data-unit {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.data-bar {
  height: 4px;
  background: rgba(0, 170, 255, 0.1);
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
}

.data-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  border-radius: 2px;
  transition: width 0.3s;
}

.data-item.warning .data-bar-fill {
  background: linear-gradient(90deg, var(--color-warning), var(--color-danger));
}

.data-item.danger .data-bar-fill {
  background: var(--color-danger);
}

.chart-section {
  margin-bottom: 15px;
  background: var(--color-bg-secondary);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--color-border-light);
}

.chart-header {
  margin-bottom: 10px;
}

.chart-title {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.chart-container {
  height: 120px;
}

.control-section {
  background: var(--color-bg-secondary);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--color-border-light);
}

.control-header {
  margin-bottom: 12px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.control-item label {
  display: block;
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-bottom: 8px;
}

.slider-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-control input[type="range"] {
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  background: rgba(0, 170, 255, 0.2);
  border-radius: 3px;
  outline: none;
}

.slider-control input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: var(--color-primary);
  border-radius: 50%;
  cursor: pointer;
}

.slider-value {
  font-size: 12px;
  color: var(--color-text-primary);
  min-width: 70px;
  text-align: right;
  font-family: 'Courier New', monospace;
}

.control-buttons {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.ctrl-btn {
  flex: 1;
  padding: 10px;
  border: 2px solid;
  border-radius: 6px;
  background: transparent;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.ctrl-btn.start {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.ctrl-btn.start:hover:not(:disabled) {
  background: rgba(54, 211, 153, 0.15);
}

.ctrl-btn.start:disabled {
  border-color: var(--color-text-disabled);
  color: var(--color-text-disabled);
  cursor: not-allowed;
}

.ctrl-btn.stop {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.ctrl-btn.stop:hover:not(:disabled) {
  background: rgba(255, 71, 87, 0.15);
}

.ctrl-btn.stop:disabled {
  border-color: var(--color-text-disabled);
  color: var(--color-text-disabled);
  cursor: not-allowed;
}

.panel-enter-active,
.panel-leave-active {
  transition: all 0.3s ease;
}

.panel-enter-from,
.panel-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
