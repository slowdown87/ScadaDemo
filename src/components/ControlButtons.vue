<template>
  <div class="control-buttons">
    <button class="ctrl-btn start-btn" :disabled="running" @click="$emit('start')">
      <span class="btn-icon">▶</span>
      <span class="btn-text">启动</span>
    </button>
    <button class="ctrl-btn stop-btn" :disabled="!running" @click="$emit('stop')">
      <span class="btn-icon">■</span>
      <span class="btn-text">停止</span>
    </button>
    <button class="ctrl-btn reset-btn" @click="$emit('reset')">
      <span class="btn-icon">↺</span>
      <span class="btn-text">复位</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  running: { type: Boolean, default: false }
})

defineEmits(['start', 'stop', 'reset'])
</script>

<style scoped>
.control-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 25px;
  background: rgba(10, 15, 26, 0.8);
  border: 1px solid rgba(0, 170, 255, 0.3);
  border-radius: var(--border-radius);
  box-shadow: 0 0 20px rgba(0, 170, 255, 0.1);
}

.ctrl-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 18px 40px;
  border: 2px solid;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.ctrl-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 28px;
}

.btn-text {
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 2px;
}

.start-btn {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.start-btn:not(:disabled):hover {
  background: rgba(54, 211, 153, 0.15);
  box-shadow: 0 0 30px rgba(54, 211, 153, 0.4);
  transform: translateY(-2px);
}

.start-btn:not(:disabled):active {
  transform: translateY(0);
}

.stop-btn {
  border-color: var(--color-warning);
  color: var(--color-warning);
}

.stop-btn:not(:disabled):hover {
  background: rgba(255, 68, 68, 0.15);
  box-shadow: 0 0 30px rgba(255, 68, 68, 0.4);
  transform: translateY(-2px);
}

.stop-btn:not(:disabled):active {
  transform: translateY(0);
}

.reset-btn {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.reset-btn:not(:disabled):hover {
  background: rgba(0, 170, 255, 0.15);
  box-shadow: 0 0 30px rgba(0, 170, 255, 0.4);
  transform: translateY(-2px);
}

.reset-btn:not(:disabled):active {
  transform: translateY(0);
}
</style>
