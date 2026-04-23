<template>
  <Transition name="alarm">
    <div v-if="show" class="alarm-popup">
      <div class="alarm-content">
        <div class="alarm-header">
          <span class="alarm-icon">⚠️</span>
          <span class="alarm-title">高温报警</span>
        </div>
        <div class="alarm-body">
          <div class="alarm-message">{{ message }}</div>
          <div class="alarm-time">{{ currentTime }}</div>
        </div>
        <div class="alarm-footer">
          <button class="ack-btn" @click="handleAck">确认报警</button>
          <button class="close-btn" @click="$emit('close')">关闭</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  message: { type: String, default: '' }
})

const emit = defineEmits(['close', 'ack'])
const currentTime = ref('')

watch(() => props.show, (val) => {
  if (val) {
    currentTime.value = new Date().toLocaleTimeString()
  }
})

function handleAck() {
  emit('ack')
}
</script>

<style scoped>
.alarm-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
  width: 420px;
  background: rgba(40, 20, 20, 0.95);
  border: 2px solid var(--color-warning);
  border-radius: 12px;
  box-shadow: 0 0 50px rgba(255, 68, 68, 0.5), 0 0 100px rgba(255, 68, 68, 0.3);
  animation: popup-flash 0.5s infinite;
}

@keyframes popup-flash {
  0%, 100% {
    box-shadow: 0 0 40px rgba(255, 68, 68, 0.4), 0 0 80px rgba(255, 68, 68, 0.2);
  }
  50% {
    box-shadow: 0 0 60px rgba(255, 68, 68, 0.6), 0 0 120px rgba(255, 68, 68, 0.4);
  }
}

.alarm-content {
  padding: 25px;
}

.alarm-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(255, 68, 68, 0.3);
}

.alarm-icon {
  font-size: 32px;
  animation: icon-shake 0.3s infinite;
}

@keyframes icon-shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-3px); }
  75% { transform: translateX(3px); }
}

.alarm-title {
  font-size: 22px;
  font-weight: bold;
  color: var(--color-warning);
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
}

.alarm-body {
  margin-bottom: 20px;
}

.alarm-message {
  font-size: 20px;
  color: #fff;
  text-align: center;
  margin-bottom: 12px;
  animation: msg-blink 0.5s infinite;
}

@keyframes msg-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.alarm-time {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  text-align: center;
}

.alarm-footer {
  display: flex;
  gap: 15px;
}

.ack-btn,
.close-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

.ack-btn {
  background: var(--color-warning);
  color: #fff;
}

.ack-btn:hover {
  background: #ff6666;
  box-shadow: 0 0 20px rgba(255, 68, 68, 0.5);
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  color: var(--color-text);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.alarm-enter-active,
.alarm-leave-active {
  transition: all 0.3s ease;
}

.alarm-enter-from,
.alarm-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.8);
}
</style>
