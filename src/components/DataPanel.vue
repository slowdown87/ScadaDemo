<template>
  <div class="data-panel">
    <div class="panel-header">
      <span class="panel-title">实时数据监控</span>
      <span class="data-time">{{ systemTime }}</span>
    </div>
    <div class="data-grid">
      <div class="data-item" :class="{ warning: tankLevel > 90 || tankLevel < 20 }">
        <div class="data-icon">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6M12,8A4,4 0 0,0 8,12A4,4 0 0,0 12,16A4,4 0 0,0 16,12A4,4 0 0,0 12,8Z"/>
          </svg>
        </div>
        <div class="data-content">
          <span class="data-label">液位</span>
          <span class="data-value">{{ tankLevel }}<span class="data-unit">%</span></span>
        </div>
        <div class="data-bar">
          <div class="data-bar-fill" :style="{ width: tankLevel + '%', background: getLevelColor(tankLevel) }"></div>
        </div>
      </div>

      <div class="data-item" :class="{ warning: flowRate > 15 || flowRate < 5 }">
        <div class="data-icon">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12,2L4,5V11.09C4,16.14 7.41,20.85 12,22C16.59,20.85 20,16.14 20,11.09V5L12,2M12,4.14L18,6.39V11.09C18,15.09 15.45,18.79 12,19.92C8.55,18.79 6,15.09 6,11.09V6.39L12,4.14Z"/>
          </svg>
        </div>
        <div class="data-content">
          <span class="data-label">流量</span>
          <span class="data-value">{{ flowRate }}<span class="data-unit">L/s</span></span>
        </div>
        <div class="data-bar">
          <div class="data-bar-fill" :style="{ width: (flowRate / 20 * 100) + '%', background: getFlowColor(flowRate) }"></div>
        </div>
      </div>

      <div class="data-item" :class="{ danger: reactorTemp > 80 }">
        <div class="data-icon temp">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M15,13V5A3,3 0 0,0 9,5V13A5,5 0 1,0 15,13M12,4A1,1 0 0,1 13,5V8H11V5A1,1 0 0,1 12,4Z"/>
          </svg>
        </div>
        <div class="data-content">
          <span class="data-label">反应釜温度</span>
          <span class="data-value">{{ reactorTemp }}<span class="data-unit">°C</span></span>
        </div>
        <div class="data-bar">
          <div class="data-bar-fill" :style="{ width: (reactorTemp / 100 * 100) + '%', background: getTempColor(reactorTemp) }"></div>
        </div>
      </div>

      <div class="data-item" :class="{ danger: reactorPressure > 1.5 }">
        <div class="data-icon pressure">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6M12,8A4,4 0 0,0 8,12A4,4 0 0,0 12,16A4,4 0 0,0 16,12A4,4 0 0,0 12,8Z"/>
          </svg>
        </div>
        <div class="data-content">
          <span class="data-label">反应釜压力</span>
          <span class="data-value">{{ reactorPressure }}<span class="data-unit">atm</span></span>
        </div>
        <div class="data-bar">
          <div class="data-bar-fill" :style="{ width: (reactorPressure / 2.5 * 100) + '%', background: getPressureColor(reactorPressure) }"></div>
        </div>
      </div>

      <div class="data-item" :class="{ warning: motorSpeed > 1400 }">
        <div class="data-icon motor">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6M12,8A4,4 0 0,0 8,12A4,4 0 0,0 12,16A4,4 0 0,0 16,12A4,4 0 0,0 12,8Z"/>
          </svg>
        </div>
        <div class="data-content">
          <span class="data-label">电机转速</span>
          <span class="data-value">{{ motorSpeed }}<span class="data-unit">RPM</span></span>
        </div>
        <div class="data-bar">
          <div class="data-bar-fill" :style="{ width: (motorSpeed / 2000 * 100) + '%', background: getMotorColor(motorSpeed) }"></div>
        </div>
      </div>

      <div class="data-item product">
        <div class="data-icon product">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M19,3H14.82C14.4,1.84 13.3,1 12,1C10.7,1 9.6,1.84 9.18,3H5A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5A2,2 0 0,0 19,3M12,3A1,1 0 0,1 13,4A1,1 0 0,1 12,5A1,1 0 0,1 11,4A1,1 0 0,1 12,3M7,7H17V5H19V19H5V5H7V7M17,11H7V9H17V11M15,15H7V13H15V15Z"/>
          </svg>
        </div>
        <div class="data-content">
          <span class="data-label">产量计数</span>
          <span class="data-value product-value">{{ productCount }}</span>
        </div>
        <div class="data-trend up" v-if="productRate > 0">
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M7,15L12,10L17,15H7Z"/>
          </svg>
          +{{ productRate }}/s
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tankLevel: { type: Number, default: 50 },
  flowRate: { type: Number, default: 0 },
  reactorTemp: { type: Number, default: 25 },
  reactorPressure: { type: Number, default: 1.0 },
  motorSpeed: { type: Number, default: 0 },
  productCount: { type: Number, default: 0 },
  productRate: { type: Number, default: 0 },
  systemTime: { type: String, default: '' }
})

function getLevelColor(level) {
  if (level > 90 || level < 20) return 'var(--color-danger)'
  if (level > 80) return 'var(--color-warning)'
  return 'var(--color-accent)'
}

function getTempColor(temp) {
  if (temp > 80) return 'var(--color-danger)'
  if (temp > 60) return 'var(--color-warning)'
  return 'var(--color-primary)'
}

function getPressureColor(pressure) {
  if (pressure > 1.5) return 'var(--color-danger)'
  if (pressure > 1.3) return 'var(--color-warning)'
  return 'var(--color-primary)'
}

function getFlowColor(rate) {
  if (rate > 15 || rate < 5) return 'var(--color-warning)'
  return 'var(--color-primary)'
}

function getMotorColor(speed) {
  if (speed > 1400) return 'var(--color-warning)'
  return 'var(--color-primary)'
}
</script>

<style scoped>
.data-panel {
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  box-shadow: var(--shadow-md);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border-light);
}

.panel-title {
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
}

.panel-title::before {
  content: '◆ ';
  color: var(--color-primary);
  font-size: 12px;
}

.data-time {
  color: var(--color-text-tertiary);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}

.data-item {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  transition: all var(--transition-normal);
}

.data-item:hover {
  border-color: var(--color-border);
  box-shadow: var(--shadow-glow);
  transform: translateY(-2px);
}

.data-item.warning {
  border-color: var(--color-warning);
  background: rgba(255, 159, 67, 0.1);
}

.data-item.danger {
  border-color: var(--color-danger);
  background: rgba(255, 71, 87, 0.1);
  animation: pulse-danger 1s ease-in-out infinite;
}

@keyframes pulse-danger {
  0%, 100% { box-shadow: 0 0 5px rgba(255, 71, 87, 0.3); }
  50% { box-shadow: 0 0 20px rgba(255, 71, 87, 0.5); }
}

.data-icon {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
  opacity: 0.8;
}

.data-icon.temp { color: var(--color-warning); }
.data-icon.pressure { color: var(--color-primary-400); }
.data-icon.motor { color: var(--color-accent); }
.data-icon.product { color: var(--color-warning); }

.data-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.data-label {
  color: var(--color-text-tertiary);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-value {
  color: var(--color-text-primary);
  font-size: 20px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}

.data-value.product-value {
  color: var(--color-accent);
  font-size: 24px;
}

.data-unit {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-left: 2px;
}

.data-bar {
  height: 4px;
  background: rgba(0, 170, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.data-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s ease, background 0.3s ease;
}

.data-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--color-accent);
}

.data-trend.up {
  color: var(--color-accent);
}

.data-trend.down {
  color: var(--color-danger);
}

@media (max-width: 1200px) {
  .data-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .data-grid {
    grid-template-columns: 1fr;
  }
}
</style>
