<template>
  <div class="simulation-view">
    <div class="sim-header">
      <h2>仿真培训系统</h2>
      <div class="sim-controls">
        <button class="ctrl-btn" @click="handlePlay" :disabled="isRunning && !isPaused">
          <span>▶</span>
        </button>
        <button class="ctrl-btn" @click="handlePause" :disabled="!isRunning || isPaused">
          <span>⏸</span>
        </button>
        <button class="ctrl-btn" @click="handleStop" :disabled="!isRunning">
          <span>⏹</span>
        </button>
        <button class="ctrl-btn" @click="handleRewind" :disabled="recordings.length === 0">
          <span>⏮</span>
        </button>
        <div class="speed-control">
          <span>速度:</span>
          <select v-model="speed" @change="handleSpeedChange">
            <option value="0.5">0.5x</option>
            <option value="1">1x</option>
            <option value="2">2x</option>
            <option value="5">5x</option>
          </select>
        </div>
      </div>
      <div class="sim-time">
        <span class="time-label">仿真时间</span>
        <span class="time-value">{{ formatTime(simulationTime) }}</span>
      </div>
    </div>

    <div class="sim-content">
      <div class="sim-sidebar">
        <div class="panel equipment-panel">
          <div class="panel-header">
            <span>设备状态</span>
          </div>
          <div class="equipment-list">
            <div
              v-for="eq in equipment"
              :key="eq.id"
              :class="['equipment-item', { faulty: eq.isFaulty, selected: selectedEquipment?.id === eq.id }]"
              @click="selectEquipment(eq)"
            >
              <div class="eq-indicator" :style="{ backgroundColor: EquipmentStateColors[eq.state] }"></div>
              <div class="eq-info">
                <span class="eq-name">{{ eq.name }}</span>
                <span class="eq-state">{{ EquipmentStateLabels[eq.state] }}</span>
              </div>
              <div v-if="eq.isFaulty" class="fault-badge">!</div>
            </div>
          </div>
        </div>

        <div class="panel faults-panel">
          <div class="panel-header">
            <span>故障注入</span>
          </div>
          <div class="fault-injection">
            <div v-if="selectedEquipment" class="fault-selector">
              <span class="fault-target">{{ selectedEquipment.name }}</span>
              <div class="fault-buttons">
                <button
                  v-for="fault in faultTypes"
                  :key="fault.type"
                  class="fault-btn"
                  :class="fault.severity"
                  @click="injectFault(fault.type)"
                  :disabled="selectedEquipment.isFaulty"
                >
                  {{ fault.label }}
                </button>
              </div>
            </div>
            <div v-else class="fault-empty">
              <span>选择设备以注入故障</span>
            </div>
          </div>
        </div>

        <div class="panel ops-panel">
          <div class="panel-header">
            <span>操作记录</span>
            <button class="btn-clear" @click="handleClearOperations">清空</button>
          </div>
          <div class="ops-list">
            <div v-for="(op, index) in operations.slice(0, 20)" :key="index" class="op-item">
              <span class="op-time">{{ formatOpTime(op.timestamp) }}</span>
              <span class="op-type">{{ getOpTypeLabel(op.type) }}</span>
              <span class="op-detail">{{ getOpDetail(op) }}</span>
            </div>
            <div v-if="operations.length === 0" class="ops-empty">
              <span>暂无操作记录</span>
            </div>
          </div>
        </div>
      </div>

      <div class="sim-main">
        <div class="main-content">
          <div class="plant-view">
            <div class="plant-placeholder">
              <div class="placeholder-content">
                <span class="placeholder-icon">◈</span>
                <p>3D 场景</p>
                <p class="placeholder-desc">TwinView 独立页面</p>
              </div>
            </div>
          </div>

          <div class="control-panel">
            <div class="metrics-display">
              <div class="metric-item">
                <span class="metric-label">温度</span>
                <span class="metric-value" :class="tempClass">
                  {{ selectedEquipment?.metrics.temperature.toFixed(1) || '--' }}°C
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">压力</span>
                <span class="metric-value" :class="pressureClass">
                  {{ selectedEquipment?.metrics.pressure.toFixed(2) || '--' }} atm
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">液位</span>
                <span class="metric-value" :class="levelClass">
                  {{ selectedEquipment?.metrics.level.toFixed(1) || '--' }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">流量</span>
                <span class="metric-value">
                  {{ selectedEquipment?.metrics.flow.toFixed(1) || '--' }} L/s
                </span>
              </div>
            </div>

            <div v-if="selectedEquipment?.isFaulty" class="fault-alert">
              <div class="alert-header">
                <span class="alert-icon">⚠</span>
                <span class="alert-title">设备故障</span>
              </div>
              <div class="alert-content">
                <p><strong>故障类型:</strong> {{ FaultTypeLabels[selectedEquipment.activeFault.type] }}</p>
                <p><strong>严重程度:</strong> {{ selectedEquipment.activeFault.severity }}</p>
                <p><strong>持续时间:</strong> {{ getFaultDuration(selectedEquipment.activeFault) }}</p>
              </div>
              <button class="btn-resolve" @click="resolveFault(selectedEquipment.id, selectedEquipment.activeFault.id)">
                消除故障
              </button>
            </div>
          </div>
        </div>

        <div class="sop-section" v-if="currentSOP">
          <div class="sop-header">
            <h3>{{ currentSOP.title }}</h3>
            <span class="sop-progress">步骤 {{ currentStepIndex + 1 }} / {{ currentSOP.steps.length }}</span>
          </div>
          <div class="sop-content">
            <div class="sop-steps">
              <div
                v-for="(step, index) in currentSOP.steps"
                :key="index"
                :class="['sop-step', {
                  completed: index < currentStepIndex,
                  current: index === currentStepIndex,
                  pending: index > currentStepIndex
                }]"
              >
                <div class="step-number">{{ index + 1 }}</div>
                <div class="step-content">
                  <p class="step-title">{{ step.title }}</p>
                  <p class="step-desc">{{ step.description }}</p>
                </div>
                <div class="step-check" v-if="index < currentStepIndex">✓</div>
              </div>
            </div>
            <button class="btn-next-step" @click="advanceStep" :disabled="currentStepIndex >= currentSOP.steps.length - 1">
              下一操作 →
            </button>
          </div>
        </div>

        <div class="scoring-section" v-if="showScoring">
          <div class="score-header">
            <h3>培训评分</h3>
            <span class="score-total">总分: {{ totalScore }}</span>
          </div>
          <div class="score-categories">
            <div class="score-item">
              <span class="score-label">响应速度</span>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: responseScore + '%' }"></div>
              </div>
              <span class="score-value">{{ responseScore }}/100</span>
            </div>
            <div class="score-item">
              <span class="score-label">操作准确性</span>
              <div class="score-bar">
                <div class="score-fill accurate" :style="{ width: accuracyScore + '%' }"></div>
              </div>
              <span class="score-value">{{ accuracyScore }}/100</span>
            </div>
            <div class="score-item">
              <span class="score-label">故障处理</span>
              <div class="score-bar">
                <div class="score-fill fault" :style="{ width: faultScore + '%' }"></div>
              </div>
              <span class="score-value">{{ faultScore }}/100</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSimulationStore } from '@/stores/simulationStore'
import { createEquipment, EquipmentState, EquipmentStateLabels, EquipmentStateColors, FaultType, FaultSeverity, FaultTypeLabels } from '@/mock/simulationEngine'

const simStore = useSimulationStore()

const {
  faults,
  initialize,
  start,
  pause,
  resume,
  stop,
  rewind,
  setSpeed,
  injectFault: storeInjectFault,
  resolveFault: storeResolveFault,
  getOperations,
  clearOperations
} = simStore

const { isRunning, isPaused, simulationTime, recordings, equipment } = storeToRefs(simStore)

const speed = ref('1')
const selectedEquipment = ref(null)
const showScoring = ref(false)
const currentStepIndex = ref(0)

const responseScore = ref(0)
const accuracyScore = ref(0)
const faultScore = ref(0)

const totalScore = computed(() => {
  return Math.round((responseScore.value + accuracyScore.value + faultScore.value) / 3)
})

const currentSOP = ref({
  title: '反应釜启停操作规程',
  steps: [
    {
      title: '检查设备状态',
      description: '确认反应釜处于空闲状态，各项指标正常'
    },
    {
      title: '启动预热',
      description: '开启搅拌器，设置目标温度'
    },
    {
      title: '监控运行',
      description: '观察温度、压力、液位变化'
    },
    {
      title: '异常处理',
      description: '如发生异常报警，及时处理'
    },
    {
      title: '正常停机',
      description: '达到工艺要求后，逐步降温和停机'
    }
  ]
})

const faultTypes = [
  { type: FaultType.TEMPERATURE_HIGH, label: '温度过高', severity: 'critical' },
  { type: FaultType.PRESSURE_HIGH, label: '压力过高', severity: 'critical' },
  { type: FaultType.LEVEL_HIGH, label: '液位过高', severity: 'warning' },
  { type: FaultType.LEVEL_LOW, label: '液位过低', severity: 'warning' },
  { type: FaultType.FLOW_BLOCKED, label: '管道堵塞', severity: 'warning' },
  { type: FaultType.MOTOR_OVERLOAD, label: '电机过载', severity: 'critical' }
]

const defaultEquipment = [
  createEquipment('R-101', '反应釜 R-101', 'reactor', EquipmentState.IDLE),
  createEquipment('TK-101', '储罐 TK-101', 'tank', EquipmentState.IDLE),
  createEquipment('TK-102', '储罐 TK-102', 'tank', EquipmentState.IDLE),
  createEquipment('B-101', '传送带 B-101', 'conveyor', EquipmentState.IDLE),
  createEquipment('P-101', '泵 P-101', 'pump', EquipmentState.IDLE)
]

function handlePlay() {
  if (isPaused.value) {
    resume()
  } else {
    start()
  }
}

function handlePause() {
  pause()
}

function handleStop() {
  stop()
  showScoring.value = true
  calculateScores()
}

function handleRewind() {
  rewind(10)
  if (currentStepIndex.value > 0) {
    currentStepIndex.value--
  }
}

function handleSpeedChange() {
  setSpeed(parseFloat(speed.value))
}

function selectEquipment(eq) {
  selectedEquipment.value = eq
}

function injectFault(faultType) {
  if (selectedEquipment.value) {
    storeInjectFault(selectedEquipment.value.id, faultType, FaultSeverity.WARNING)
    responseScore.value = Math.min(100, responseScore.value + 10)
  }
}

function resolveFault(equipmentId, faultId) {
  storeResolveFault(equipmentId, faultId)
  faultScore.value = Math.min(100, faultScore.value + 20)
}

function advanceStep() {
  if (currentStepIndex.value < currentSOP.value.steps.length - 1) {
    currentStepIndex.value++
    accuracyScore.value = Math.min(100, accuracyScore.value + 15)
  }
}

function calculateScores() {
  responseScore.value = Math.min(100, Math.round(Math.random() * 30 + 70))
  faultScore.value = Math.min(100, Math.round(Math.random() * 40 + 60))
}

function handleClearOperations() {
  clearOperations()
}

function formatTime(ms) {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

function formatOpTime(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function getOpTypeLabel(type) {
  const labels = {
    stateChange: '状态变更',
    faultInjected: '故障注入',
    faultResolved: '故障消除',
    start: '启动',
    stop: '停止'
  }
  return labels[type] || type
}

function getOpDetail(op) {
  if (op.type === 'stateChange') {
    return `${EquipmentStateLabels[op.oldState]} → ${EquipmentStateLabels[op.newState]}`
  }
  if (op.type === 'faultInjected') {
    return FaultTypeLabels[op.faultType] || op.faultType
  }
  return ''
}

function getFaultDuration(fault) {
  if (!fault) return '--'
  const duration = Date.now() - fault.startTime
  const seconds = Math.floor(duration / 1000)
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes}m ${secs}s`
}

const tempClass = computed(() => {
  if (!selectedEquipment.value) return ''
  const temp = selectedEquipment.value.metrics.temperature
  if (temp > 90) return 'critical'
  if (temp > 80) return 'warning'
  return ''
})

const pressureClass = computed(() => {
  if (!selectedEquipment.value) return ''
  const pressure = selectedEquipment.value.metrics.pressure
  if (pressure > 1.8) return 'critical'
  if (pressure > 1.5) return 'warning'
  return ''
})

const levelClass = computed(() => {
  if (!selectedEquipment.value) return ''
  const level = selectedEquipment.value.metrics.level
  if (level > 90 || level < 20) return 'warning'
  return ''
})

const operations = computed(() => simStore.getOperations())

onMounted(() => {
  initialize(defaultEquipment)
})

onUnmounted(() => {
  stop()
})
</script>

<style scoped>
.simulation-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: transparent;
  color: var(--color-text-primary);
}

.sim-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--color-border-light);
  margin-bottom: 16px;
  border-radius: 12px;
}

.sim-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.sim-header h2::before {
  content: '◆';
  color: var(--color-primary);
  font-size: 14px;
}

.sim-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ctrl-btn {
  width: 40px;
  height: 40px;
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  background: var(--color-bg-glass);
  color: var(--color-text-secondary);
  font-size: 16px;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.ctrl-btn:hover:not(:disabled) {
  background: rgba(0, 170, 255, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.ctrl-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 12px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.speed-control select {
  background: var(--color-bg-glass);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
}

.sim-time {
  text-align: right;
}

.time-label {
  display: block;
  font-size: 10px;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.time-value {
  font-size: 22px;
  font-family: 'Courier New', monospace;
  color: var(--color-primary);
  font-variant-numeric: tabular-nums;
}

.sim-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 16px;
}

.sim-sidebar {
  width: 280px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
}

.panel {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  overflow: hidden;
}

.panel-header {
  padding: 12px 14px;
  background: linear-gradient(135deg, rgba(0, 170, 255, 0.1), rgba(0, 170, 255, 0.05));
  border-bottom: 1px solid var(--color-border-light);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.equipment-list {
  max-height: 200px;
  overflow-y: auto;
}

.equipment-item {
  display: flex;
  align-items: center;
  padding: 10px 14px;
  cursor: pointer;
  transition: all var(--transition-fast);
  gap: 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
}

.equipment-item:hover {
  background: rgba(0, 170, 255, 0.05);
}

.equipment-item.selected {
  background: rgba(0, 170, 255, 0.1);
}

.equipment-item.faulty {
  border-left: 3px solid var(--color-danger);
}

.eq-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.eq-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.eq-name {
  font-size: 12px;
  font-weight: 600;
}

.eq-state {
  font-size: 10px;
  color: var(--color-text-tertiary);
}

.fault-badge {
  width: 18px;
  height: 18px;
  background: var(--color-danger);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  color: white;
}

.fault-empty {
  padding: 20px;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.fault-selector {
  padding: 12px;
}

.fault-target {
  display: block;
  font-size: 12px;
  margin-bottom: 10px;
  color: var(--color-primary);
}

.fault-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.fault-btn {
  padding: 8px 10px;
  border: 1px solid;
  border-radius: 6px;
  font-size: 10px;
  cursor: pointer;
  background: transparent;
  transition: all var(--transition-fast);
}

.fault-btn.critical {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.fault-btn.warning {
  border-color: var(--color-warning);
  color: var(--color-warning);
}

.fault-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.fault-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-clear {
  background: transparent;
  border: none;
  color: var(--color-text-tertiary);
  font-size: 10px;
  cursor: pointer;
}

.btn-clear:hover {
  color: var(--color-text-primary);
}

.ops-list {
  max-height: 150px;
  overflow-y: auto;
}

.op-item {
  display: flex;
  gap: 8px;
  padding: 6px 10px;
  font-size: 10px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
}

.op-time {
  color: var(--color-text-tertiary);
  font-family: 'Courier New', monospace;
}

.op-type {
  color: var(--color-primary);
  min-width: 50px;
}

.op-detail {
  color: var(--color-text-primary);
}

.ops-empty {
  padding: 20px;
  text-align: center;
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.sim-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  gap: 16px;
  overflow: hidden;
}

.plant-view {
  flex: 1;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--color-border-light);
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.plant-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
  color: var(--color-text-tertiary);
}

.placeholder-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 10px;
  opacity: 0.5;
  color: var(--color-primary);
}

.placeholder-desc {
  font-size: 12px;
  opacity: 0.7;
}

.control-panel {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metrics-display {
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 16px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.metric-value {
  font-size: 14px;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.metric-value.warning {
  color: var(--color-warning);
}

.metric-value.critical {
  color: var(--color-danger);
}

.fault-alert {
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid var(--color-danger);
  border-radius: 10px;
  padding: 14px;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.alert-icon {
  font-size: 18px;
  color: var(--color-danger);
}

.alert-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-danger);
}

.alert-content p {
  margin: 5px 0;
  font-size: 11px;
}

.btn-resolve {
  width: 100%;
  margin-top: 10px;
  padding: 8px;
  background: var(--color-danger);
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.btn-resolve:hover {
  background: var(--color-danger);
}

.sop-section {
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid var(--color-border-light);
  padding: 16px;
}

.sop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.sop-header h3 {
  margin: 0;
  font-size: 14px;
  color: var(--color-primary);
}

.sop-progress {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.sop-steps {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.sop-step {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 14px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  min-width: 180px;
  position: relative;
  transition: all var(--transition-normal);
}

.sop-step.completed {
  background: rgba(54, 211, 153, 0.1);
  border-color: rgba(54, 211, 153, 0.3);
}

.sop-step.current {
  background: rgba(0, 170, 255, 0.1);
  border-color: var(--color-primary);
}

.sop-step.pending {
  opacity: 0.5;
}

.step-number {
  width: 22px;
  height: 22px;
  background: var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.sop-step.completed .step-number {
  background: var(--color-accent);
}

.step-title {
  font-size: 12px;
  font-weight: 600;
  margin: 0 0 4px 0;
}

.step-desc {
  font-size: 10px;
  color: var(--color-text-tertiary);
  margin: 0;
}

.step-check {
  position: absolute;
  top: 5px;
  right: 5px;
  color: var(--color-accent);
  font-size: 12px;
}

.btn-next-step {
  margin-top: 12px;
  padding: 10px 20px;
  background: rgba(0, 170, 255, 0.1);
  border: 1px solid var(--color-primary);
  border-radius: 6px;
  color: var(--color-primary);
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-next-step:hover:not(:disabled) {
  background: rgba(0, 170, 255, 0.2);
}

.btn-next-step:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.scoring-section {
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-top: 1px solid var(--color-border-light);
  padding: 16px;
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.score-header h3 {
  margin: 0;
  font-size: 14px;
  color: var(--color-primary);
}

.score-total {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-accent);
}

.score-categories {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-label {
  width: 80px;
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.score-bar {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: var(--color-primary);
  transition: width 0.3s;
}

.score-fill.accurate {
  background: var(--color-accent);
}

.score-fill.fault {
  background: var(--color-warning);
}

.score-value {
  width: 50px;
  text-align: right;
  font-size: 12px;
  font-family: 'Courier New', monospace;
}

@media (max-width: 1400px) {
  .sim-content {
    flex-direction: column;
  }

  .sim-sidebar {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .sim-sidebar > .panel {
    flex: 1;
    min-width: 280px;
  }

  .main-content {
    flex-direction: column;
  }

  .control-panel {
    width: 100%;
  }
}
</style>