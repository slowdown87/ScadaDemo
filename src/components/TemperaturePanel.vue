<template>
  <div class="panel temperature-panel" :class="{ warning: isWarning }">
    <div class="panel-header">
      <span class="panel-icon">🌡️</span>
      <span class="panel-title">温度监控</span>
    </div>
    <div class="panel-content">
      <div class="temp-main">
        <span class="temp-value" :class="{ warning: isWarning }">{{ temp.toFixed(1) }}</span>
        <span class="temp-unit">℃</span>
      </div>
      <div class="temp-bar">
        <div class="temp-fill" :style="{ width: barWidth + '%', backgroundColor: barColor }"></div>
      </div>
      <div class="temp-range">
        <span>25℃</span>
        <span>80℃</span>
      </div>
      <div class="temp-stats">
        <div class="stat-item">
          <span class="stat-label">最低</span>
          <span class="stat-value">{{ min.toFixed(1) }}℃</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">最高</span>
          <span class="stat-value">{{ max.toFixed(1) }}℃</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">平均</span>
          <span class="stat-value">{{ avg.toFixed(1) }}℃</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  temp: { type: Number, default: 25.0 },
  min: { type: Number, default: 25.0 },
  max: { type: Number, default: 25.0 },
  avg: { type: Number, default: 25.0 }
})

const isWarning = computed(() => props.temp >= 50)

const barWidth = computed(() => {
  return Math.min(((props.temp - 25) / 55) * 100, 100)
})

const barColor = computed(() => {
  const t = props.temp
  if (t < 35) return '#36d399'
  if (t < 45) return '#ffc107'
  if (t < 50) return '#ff9800'
  return '#ff4444'
})
</script>

<style scoped>
.panel {
  background: var(--color-panel);
  border: 1px solid var(--color-primary);
  border-radius: var(--border-radius);
  padding: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: var(--box-shadow);
  transition: all 0.3s ease;
}

.panel:hover {
  box-shadow: 0 0 30px rgba(0, 170, 255, 0.2);
}

.panel.warning {
  border-color: var(--color-warning);
  animation: panel-flash 0.5s infinite;
}

@keyframes panel-flash {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 68, 68, 0.3); }
  50% { box-shadow: 0 0 40px rgba(255, 68, 68, 0.6); }
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.3);
}

.panel-icon {
  font-size: 22px;
}

.panel-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text);
  letter-spacing: 1px;
}

.panel-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.temp-main {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 15px;
}

.temp-value {
  font-size: 64px;
  font-weight: bold;
  color: var(--color-primary);
  text-shadow: 0 0 25px rgba(0, 170, 255, 0.5);
  transition: all 0.3s ease;
}

.temp-value.warning {
  color: var(--color-warning);
  text-shadow: 0 0 25px rgba(255, 68, 68, 0.6);
  animation: temp-blink 0.5s infinite;
}

@keyframes temp-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.temp-unit {
  font-size: 28px;
  color: var(--color-text-dim);
}

.temp-bar {
  height: 24px;
  background: rgba(30, 40, 60, 0.8);
  border-radius: 12px;
  margin-bottom: 8px;
  overflow: hidden;
  border: 1px solid rgba(0, 170, 255, 0.2);
}

.temp-fill {
  height: 100%;
  border-radius: 12px;
  transition: width 0.5s ease, background-color 0.5s ease;
  box-shadow: 0 0 15px currentColor;
}

.temp-range {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-text-dim);
  margin-bottom: 20px;
}

.temp-stats {
  display: flex;
  justify-content: space-around;
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
  margin-bottom: 4px;
}

.stat-value {
  font-size: 15px;
  color: var(--color-accent);
  font-weight: 600;
}
</style>
