<template>
  <div class="panel motor-panel">
    <div class="panel-header">
      <span class="panel-icon">⚡</span>
      <span class="panel-title">电机控制</span>
    </div>
    <div class="panel-content">
      <div class="motor-display">
        <div class="motor-circle" :class="{ running: running }">
          <span class="motor-label">MTR-01</span>
          <span class="motor-speed">{{ Math.round(speed) }}</span>
          <span class="motor-unit">RPM</span>
        </div>
      </div>
      <div class="motor-info">
        <div class="info-row">
          <span class="info-label">状态:</span>
          <span class="info-value" :class="status.toLowerCase()">{{ status }}</span>
        </div>
        <div class="info-row" v-if="running">
          <span class="info-label">运行时长:</span>
          <span class="info-value runtime">{{ formatRuntime(runtime) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  running: { type: Boolean, default: false },
  speed: { type: Number, default: 0 },
  status: { type: String, default: 'IDLE' },
  runtime: { type: Number, default: 0 }
})

function formatRuntime(seconds) {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}
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
  align-items: center;
}

.motor-display {
  margin-bottom: 20px;
}

.motor-circle {
  width: 140px;
  height: 140px;
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
  inset: -10px;
  border-radius: 50%;
  border: 2px solid transparent;
  transition: all 0.5s ease;
}

.motor-circle.running {
  border-color: var(--color-accent);
  box-shadow: 0 0 35px rgba(54, 211, 153, 0.6);
  animation: motor-glow 1.5s ease-in-out infinite;
}

.motor-circle.running::before {
  border-color: rgba(54, 211, 153, 0.3);
  animation: ring-pulse 1.5s ease-in-out infinite;
}

@keyframes motor-glow {
  0%, 100% { box-shadow: 0 0 25px rgba(54, 211, 153, 0.5); }
  50% { box-shadow: 0 0 50px rgba(54, 211, 153, 0.8); }
}

@keyframes ring-pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.motor-label {
  font-size: 13px;
  color: var(--color-text-dim);
  margin-bottom: 5px;
}

.motor-speed {
  font-size: 32px;
  font-weight: bold;
  color: var(--color-accent);
  text-shadow: 0 0 15px rgba(54, 211, 153, 0.6);
}

.motor-unit {
  font-size: 11px;
  color: var(--color-text-dim);
}

.motor-info {
  width: 100%;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 13px;
  color: var(--color-text-dim);
}

.info-value {
  font-size: 14px;
  font-weight: 600;
}

.info-value.idle { color: #888; }
.info-value.running { color: var(--color-accent); }
.info-value.runtime {
  color: var(--color-primary);
  font-family: 'Courier New', monospace;
}
</style>
