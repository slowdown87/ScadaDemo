<template>
  <div class="panel production-panel">
    <div class="panel-header">
      <span class="panel-icon">📊</span>
      <span class="panel-title">产量计数</span>
    </div>
    <div class="panel-content">
      <div class="production-display">
        <div v-for="(digit, index) in digits" :key="index" class="digit-box">
          {{ digit }}
        </div>
      </div>
      <div class="production-info">
        <div class="info-item">
          <span class="info-label">班次产量</span>
          <span class="info-value">{{ shift }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">生产速率</span>
          <span class="info-value">{{ rate }} 个/分</span>
        </div>
        <div class="info-item">
          <span class="info-label">累计产量</span>
          <span class="info-value">{{ total }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  count: { type: Number, default: 0 },
  shift: { type: Number, default: 0 },
  rate: { type: Number, default: 0 },
  total: { type: Number, default: 0 }
})

const digits = computed(() => {
  return String(props.count).padStart(4, '0').split('')
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

.production-display {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 25px;
}

.digit-box {
  width: 65px;
  height: 85px;
  background: rgba(0, 0, 0, 0.5);
  border: 2px solid var(--color-accent);
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40px;
  font-weight: bold;
  font-family: 'Courier New', monospace;
  color: var(--color-accent);
  text-shadow: 0 0 15px rgba(54, 211, 153, 0.5);
  transition: all 0.2s ease;
}

.digit-box:hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(54, 211, 153, 0.4);
}

.production-info {
  display: flex;
  justify-content: space-around;
}

.info-item {
  text-align: center;
}

.info-label {
  display: block;
  font-size: 12px;
  color: var(--color-text-dim);
  margin-bottom: 5px;
}

.info-value {
  font-size: 15px;
  color: var(--color-text);
  font-weight: 600;
}
</style>
