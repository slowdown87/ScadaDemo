<template>
  <div class="control-panel">
    <div class="panel-header">
      <span class="panel-title">◆ 系统控制</span>
      <span class="system-status" :class="{ running: isRunning }">
        <span class="status-dot"></span>
        {{ isRunning ? '运行中' : '已停止' }}
      </span>
    </div>

    <div class="control-buttons">
      <button
        class="ctrl-btn start"
        :disabled="isRunning"
        @click="$emit('start')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M8,5.14V19.14L19,12.14L8,5.14Z"/>
        </svg>
        <span class="btn-text">启动</span>
        <span class="btn-hint">电机运转</span>
      </button>

      <button
        class="ctrl-btn stop"
        :disabled="!isRunning"
        @click="$emit('stop')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M18,18H6V6H18V18Z"/>
        </svg>
        <span class="btn-text">停止</span>
        <span class="btn-hint">紧急停机</span>
      </button>

      <button
        class="ctrl-btn reset"
        @click="$emit('reset')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12,4C14.1,4 16.1,4.8 17.6,6.3C20.7,9.4 20.7,14.5 17.6,17.6C15.8,19.5 13.3,20.2 10.9,19.9L11.4,17.9C13.1,18.1 14.9,17.5 16.2,16.2C18.5,13.9 18.5,10.1 16.2,7.7C15.1,6.6 13.5,6 12,6V10.6L7,5.6L12,0.6V4M6.3,17.6C3.7,15 3.3,11 5.1,7.9L6.6,9.4C5.5,11.6 5.9,14.4 7.8,16.2C8.3,16.7 8.9,17.1 9.6,17.4L9,19.4C8,19 7.1,18.4 6.3,17.6Z"/>
        </svg>
        <span class="btn-text">复位</span>
        <span class="btn-hint">数据清零</span>
      </button>

      <button
        class="ctrl-btn toggle"
        :class="{ active: isRunning }"
        @click="$emit('toggle')"
      >
        <svg viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M13,7H11V13H17V11H13V7Z"/>
        </svg>
        <span class="btn-text">{{ isRunning ? '暂停' : '继续' }}</span>
        <span class="btn-hint">切换状态</span>
      </button>
    </div>

    <div class="quick-stats">
      <div class="stat-item">
        <span class="stat-label">运行时长</span>
        <span class="stat-value">{{ runtime }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">总产量</span>
        <span class="stat-value">{{ totalProduct }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">报警次数</span>
        <span class="stat-value">{{ alarmCount }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  isRunning: { type: Boolean, default: false },
  runtime: { type: String, default: '00:00:00' },
  totalProduct: { type: Number, default: 0 },
  alarmCount: { type: Number, default: 0 }
})

defineEmits(['start', 'stop', 'reset', 'toggle'])
</script>

<style scoped>
.control-panel {
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
  margin-bottom: var(--space-lg);
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

.system-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--color-danger);
  padding: 4px 12px;
  background: rgba(255, 71, 87, 0.1);
  border-radius: 15px;
  border: 1px solid rgba(255, 71, 87, 0.3);
}

.system-status.running {
  color: var(--color-accent);
  background: rgba(54, 211, 153, 0.1);
  border-color: rgba(54, 211, 153, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse-status 1.5s ease-in-out infinite;
}

.system-status:not(.running) .status-dot {
  animation: none;
}

@keyframes pulse-status {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.control-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: var(--space-lg);
}

.ctrl-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 15px 10px;
  border: 2px solid;
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.ctrl-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.5s ease;
}

.ctrl-btn:hover::before {
  left: 100%;
}

.ctrl-btn svg {
  transition: transform var(--transition-normal);
}

.ctrl-btn:hover svg {
  transform: scale(1.1);
}

.ctrl-btn .btn-text {
  font-size: 14px;
  font-weight: 600;
}

.ctrl-btn .btn-hint {
  font-size: 10px;
  opacity: 0.7;
}

.ctrl-btn.start {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.ctrl-btn.start:hover:not(:disabled) {
  background: rgba(54, 211, 153, 0.15);
  box-shadow: 0 0 20px rgba(54, 211, 153, 0.3);
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
  box-shadow: 0 0 20px rgba(255, 71, 87, 0.3);
}

.ctrl-btn.stop:disabled {
  border-color: var(--color-text-disabled);
  color: var(--color-text-disabled);
  cursor: not-allowed;
}

.ctrl-btn.reset {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.ctrl-btn.reset:hover {
  background: rgba(0, 170, 255, 0.15);
  box-shadow: 0 0 20px rgba(0, 170, 255, 0.3);
}

.ctrl-btn.toggle {
  border-color: var(--color-warning);
  color: var(--color-warning);
}

.ctrl-btn.toggle:hover {
  background: rgba(250, 173, 20, 0.15);
  box-shadow: 0 0 20px rgba(250, 173, 20, 0.3);
}

.ctrl-btn.toggle.active {
  background: rgba(250, 173, 20, 0.2);
  animation: toggle-active 1s ease-in-out infinite;
}

@keyframes toggle-active {
  0%, 100% { box-shadow: 0 0 10px rgba(250, 173, 20, 0.3); }
  50% { box-shadow: 0 0 25px rgba(250, 173, 20, 0.5); }
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border-light);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 10px;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  font-family: 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
}
</style>
