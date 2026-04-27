<template>
  <div class="dashboard">
    <div class="dashboard-title">
      <h2>◆ 主控制面板</h2>
      <div class="title-actions">
        <el-button size="small" @click="handleResetAll">重置系统</el-button>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="panel motor-panel">
        <div class="panel-header">
          <span class="panel-icon">⚡</span>
          <span class="panel-title">电机控制</span>
        </div>
        <div class="panel-content">
          <div class="motor-display">
            <div class="motor-circle" :class="{ running: store.motor_running, stopping: !store.motor_running }">
              <span class="motor-label">MTR-01</span>
              <span class="motor-speed">{{ Math.round(store.motor_speed) }}</span>
              <span class="motor-unit">RPM</span>
            </div>
          </div>
          <div class="motor-status">
            <span class="status-label">状态:</span>
            <span class="status-value" :class="store.motor_status.toLowerCase()">
              {{ store.motor_status }}
            </span>
          </div>
          <div class="motor-runtime" v-if="store.motor_running">
            <span class="runtime-label">运行时间:</span>
            <span class="runtime-value">{{ formatRuntime(store.motor_runtime) }}</span>
          </div>
          <el-button
            class="control-btn"
            :type="store.motor_running ? 'danger' : 'success'"
            @click="handleToggle"
            :loading="isLoading"
          >
            {{ store.motor_running ? '停止' : '启动' }}
          </el-button>
        </div>
      </div>

      <div class="panel temperature-panel">
        <div class="panel-header">
          <span class="panel-icon">🌡️</span>
          <span class="panel-title">温度监控</span>
        </div>
        <div class="panel-content">
          <div class="temp-display">
            <span class="temp-value" :class="{ warning: store.temperature >= 50 }">
              {{ store.currentTemperature }}
            </span>
            <span class="temp-unit">℃</span>
          </div>
          <div class="temp-bar">
            <div
              class="temp-fill"
              :style="{ width: tempBarWidth + '%', backgroundColor: tempBarColor }"
            ></div>
          </div>
          <div class="temp-range">
            <span>25℃</span>
            <span>80℃</span>
          </div>
          <div class="temp-stats">
            <div class="stat-item">
              <span class="stat-label">最低</span>
              <span class="stat-value">{{ store.temp_min.toFixed(1) }}℃</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">最高</span>
              <span class="stat-value">{{ store.temp_max.toFixed(1) }}℃</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均</span>
              <span class="stat-value">{{ store.temp_average.toFixed(1) }}℃</span>
            </div>
          </div>
        </div>
      </div>

      <div class="panel production-panel">
        <div class="panel-header">
          <span class="panel-icon">📊</span>
          <span class="panel-title">产量计数</span>
        </div>
        <div class="panel-content">
          <div class="production-display">
            <div v-for="(digit, index) in productionDigits" :key="index" class="digit-box">
              {{ digit }}
            </div>
          </div>
          <div class="production-info">
            <div class="info-item">
              <span class="info-label">班次产量</span>
              <span class="info-value">{{ store.shift_count }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">生产速率</span>
              <span class="info-value">{{ store.production_rate }} 个/分</span>
            </div>
            <div class="info-item">
              <span class="info-label">累计产量</span>
              <span class="info-value">{{ store.production_total }}</span>
            </div>
          </div>
          <el-button class="reset-btn" size="small" @click="handleResetProduction">
            复位产量
          </el-button>
        </div>
      </div>

      <div class="panel alarm-panel" :class="{ triggered: store.alarm_triggered }">
        <div class="panel-header" :class="{ warning: store.alarm_triggered }">
          <span class="panel-icon">⚠️</span>
          <span class="panel-title">报警面板</span>
        </div>
        <div class="panel-content">
          <div v-if="store.alarm_triggered" class="alarm-content">
            <div class="alarm-message">
              {{ store.alarm_message }}
            </div>
            <div class="alarm-info">
              <span>报警次数: {{ store.alarm_count }}</span>
            </div>
            <el-button type="warning" size="small" @click="handleAcknowledge">
              确认报警
            </el-button>
          </div>
          <div v-else class="alarm-normal">
            <span class="normal-icon">✓</span>
            <span class="normal-text">系统正常</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { usePlcStore } from '@/stores/plcStore'
import { ElMessage } from 'element-plus'

const store = usePlcStore()
const isLoading = ref(false)

const productionDigits = computed(() => {
  return store.currentProduction.split('')
})

const tempBarWidth = computed(() => {
  const temp = store.temperature
  return Math.min(((temp - 25) / 55) * 100, 100)
})

const tempBarColor = computed(() => {
  const temp = store.temperature
  if (temp < 35) return 'var(--color-accent)'
  if (temp < 45) return 'var(--color-warning)'
  if (temp < 50) return '#ff9800'
  return 'var(--color-danger)'
})

function formatRuntime(seconds) {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

function handleToggle() {
  isLoading.value = true
  store.toggleMotor()
  setTimeout(() => {
    isLoading.value = false
    ElMessage({
      message: store.motor_running ? '电机已启动' : '电机已停止',
      type: store.motor_running ? 'success' : 'info'
    })
  }, 100)
}

function handleResetProduction() {
  store.resetProduction()
  ElMessage({
    message: '产量已复位',
    type: 'info'
  })
}

function handleAcknowledge() {
  store.acknowledgeAlarm()
  ElMessage({
    message: '报警已确认',
    type: 'success'
  })
}

function handleResetAll() {
  store.resetAll()
  ElMessage({
    message: '系统已重置',
    type: 'info'
  })
}

onMounted(() => {
  store.initStore()
})

onUnmounted(() => {
  store.cleanup()
})
</script>

<style scoped>
.dashboard {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.dashboard-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.dashboard-title h2 {
  color: var(--color-primary);
  font-size: 18px;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 20px;
  flex: 1;
}

.panel {
  background: rgba(10, 15, 26, 0.9);
  border: 1px solid var(--color-primary);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.1), inset 0 0 30px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.panel:hover {
  box-shadow: 0 0 25px rgba(0, 170, 255, 0.2), inset 0 0 30px rgba(0, 0, 0, 0.3);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.3);
}

.panel-icon {
  font-size: 20px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--color-text);
}

.panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.motor-display {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
}

.motor-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 3px solid #444;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.5s ease;
  position: relative;
}

.motor-circle::before {
  content: '';
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 2px solid transparent;
  transition: all 0.5s ease;
}

.motor-circle.running {
  border-color: var(--color-accent);
  box-shadow: 0 0 30px rgba(54, 211, 153, 0.6);
  animation: motor-glow 1.5s ease-in-out infinite;
}

.motor-circle.running::before {
  border-color: rgba(54, 211, 153, 0.3);
  animation: ring-pulse 1.5s ease-in-out infinite;
}

.motor-circle.stopping {
  border-color: #555;
  box-shadow: none;
}

@keyframes motor-glow {
  0%, 100% {
    box-shadow: 0 0 20px rgba(54, 211, 153, 0.4);
  }
  50% {
    box-shadow: 0 0 40px rgba(54, 211, 153, 0.8);
  }
}

@keyframes ring-pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.8;
  }
}

.motor-label {
  font-size: 12px;
  color: var(--color-text-dim);
}

.motor-speed {
  font-size: 28px;
  font-weight: bold;
  color: var(--color-accent);
  text-shadow: 0 0 10px rgba(54, 211, 153, 0.5);
}

.motor-unit {
  font-size: 10px;
  color: var(--color-text-dim);
}

.motor-status {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 8px 0;
}

.motor-runtime {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 13px;
}

.runtime-label {
  color: var(--color-text-dim);
}

.runtime-value {
  color: var(--color-primary);
  font-family: 'Courier New', monospace;
}

.status-label {
  color: var(--color-text-dim);
}

.status-value {
  font-weight: bold;
}

.status-value.idle {
  color: #888;
}

.status-value.running {
  color: var(--color-accent);
}

.control-btn {
  width: 100%;
  height: 45px;
  font-size: 16px;
  font-weight: bold;
  letter-spacing: 2px;
  margin-top: auto;
}

.temp-display {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 5px;
}

.temp-value {
  font-size: 56px;
  font-weight: bold;
  color: var(--color-primary);
  text-shadow: 0 0 20px rgba(0, 170, 255, 0.5);
  transition: all 0.3s ease;
}

.temp-value.warning {
  color: var(--color-warning);
  text-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
  animation: temp-blink 0.5s infinite;
}

@keyframes temp-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.temp-unit {
  font-size: 24px;
  color: var(--color-text-dim);
}

.temp-bar {
  height: 20px;
  background: rgba(30, 40, 60, 0.8);
  border-radius: 10px;
  margin: 15px 0;
  overflow: hidden;
}

.temp-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease, background-color 0.5s ease;
  box-shadow: 0 0 10px currentColor;
}

.temp-range {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-text-dim);
}

.temp-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid rgba(0, 170, 255, 0.2);
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: var(--color-text-dim);
  margin-bottom: 3px;
}

.stat-value {
  font-size: 14px;
  color: var(--color-accent);
}

.production-display {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 15px;
}

.digit-box {
  width: 60px;
  height: 80px;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid var(--color-accent);
  border-radius: 6px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 36px;
  font-weight: bold;
  font-family: 'Courier New', monospace;
  color: var(--color-accent);
  text-shadow: 0 0 10px rgba(54, 211, 153, 0.5);
  transition: all 0.2s ease;
}

.digit-box:hover {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(54, 211, 153, 0.3);
}

.production-info {
  display: flex;
  justify-content: space-around;
  margin-bottom: 10px;
}

.info-item {
  text-align: center;
}

.info-label {
  display: block;
  font-size: 11px;
  color: var(--color-text-dim);
  margin-bottom: 3px;
}

.info-value {
  font-size: 14px;
  color: var(--color-text);
}

.reset-btn {
  margin-top: auto;
  width: 100%;
}

.alarm-panel {
  border-color: var(--color-accent);
  transition: all 0.3s ease;
}

.alarm-panel.triggered {
  border-color: var(--color-warning);
  animation: alarm-flash 0.5s infinite;
}

@keyframes alarm-flash {
  0%, 100% {
    box-shadow: 0 0 15px rgba(255, 68, 68, 0.3);
    border-color: var(--color-warning);
  }
  50% {
    box-shadow: 0 0 35px rgba(255, 68, 68, 0.6);
    border-color: var(--color-danger);
  }
}

.panel-header.warning .panel-icon,
.panel-header.warning .panel-title {
  color: var(--color-warning);
}

.alarm-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.alarm-message {
  font-size: 20px;
  font-weight: bold;
  color: var(--color-warning);
  text-align: center;
  animation: blink 0.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.alarm-info {
  font-size: 14px;
  color: var(--color-text-dim);
}

.alarm-normal {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
}

.normal-icon {
  font-size: 48px;
  color: var(--color-accent);
}

.normal-text {
  font-size: 16px;
  color: var(--color-accent);
}
</style>
