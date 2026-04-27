<template>
  <div class="alarm-panel" :class="{ 'has-alarms': hasAlarms }">
    <div class="panel-header">
      <div class="header-left">
        <span class="panel-title">报警管理</span>
        <div class="alarm-counts">
          <span class="count critical" v-if="criticalCount > 0">
            <span class="count-num">{{ criticalCount }}</span> 紧急
          </span>
          <span class="count warning" v-if="warningCount > 0">
            <span class="count-num">{{ warningCount }}</span> 警告
          </span>
          <span class="count info" v-if="infoCount > 0">
            <span class="count-num">{{ infoCount }}</span> 提示
          </span>
        </div>
      </div>
      <div class="header-actions">
        <button class="sound-btn" @click="$emit('toggleSound')" :class="{ muted: !soundEnabled }">
          <svg v-if="soundEnabled" viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M3,9H7L12,4V20L7,15H3V9M16.5,12A4.5,4.5 0 0,1 12,16.5A4.5,4.5 0 0,1 7.5,12A4.5,4.5 0 0,1 12,7.5A4.5,4.5 0 0,1 16.5,12M16.5,15A1.5,1.5 0 0,1 15,13.5A1.5,1.5 0 0,1 16.5,12A1.5,1.5 0 0,1 18,13.5A1.5,1.5 0 0,1 16.5,15Z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M12,4L9.91,6.09L12,8.18M4.27,3L3,4.27L7.73,9H3V15H7L12,20V13.27L16.25,17.53C15.58,18.04 14.83,18.45 14,18.7V20.77C15.38,20.45 16.63,19.81 17.68,18.95L19.73,21L21,19.73L12,10.73M19,12C19,12.94 18.8,13.87 18.46,14.73L19.97,16.24C20.62,14.91 21,13.5 21,12C21,7.72 18,4.14 14,3.23V5.29C16.89,6.15 19,8.83 19,12M16.5,12A4.5,4.5 0 0,1 12,16.5A4.5,4.5 0 0,1 7.5,12A4.5,4.5 0 0,1 12,7.5A4.5,4.5 0 0,1 16.5,12Z"/>
          </svg>
        </button>
        <button class="export-btn" @click="$emit('exportHistory')" v-if="alarmHistory.length > 0">
          导出
        </button>
        <button class="ack-all-btn" @click="$emit('acknowledgeAll')" v-if="hasAlarms">
          全部确认
        </button>
      </div>
    </div>

    <div class="alarms-list" v-if="hasAlarms">
      <div
        v-for="alarm in alarms"
        :key="alarm.id + alarm.timestamp"
        class="alarm-item"
        :class="alarm.level"
      >
        <div class="alarm-indicator">
          <span class="alarm-led" :class="alarm.level"></span>
        </div>
        <div class="alarm-content">
          <div class="alarm-header">
            <span class="alarm-id">{{ alarm.id }}</span>
            <span class="alarm-time">{{ alarm.timestamp }}</span>
          </div>
          <div class="alarm-message">{{ alarm.message }}</div>
        </div>
        <button class="alarm-ack-btn" @click="$emit('acknowledge', alarm.id)">
          确认
        </button>
      </div>
    </div>

    <div class="no-alarms" v-else>
      <svg viewBox="0 0 24 24" width="40" height="40">
        <path fill="currentColor" d="M12,2C6.5,2 2,6.5 2,12S6.5,22 12,22 22,17.5 22,12 17.5,2 12,2M12,20C7.59,20 4,16.41 4,12S7.59,4 12,4 20,7.59 20,12 16.41,20 12,20M16.59,7.58L10,14.17L7.41,11.59L6,13L10,17L18,9L16.59,7.58Z"/>
      </svg>
      <span>系统运行正常，无报警</span>
    </div>

    <div class="alarm-history" v-if="alarmHistory.length > 0">
      <div class="history-header">
        <span>报警历史</span>
        <span class="history-count">{{ alarmHistory.length }} 条记录</span>
      </div>
      <div class="history-list">
        <div
          v-for="(item, index) in recentHistory"
          :key="index"
          class="history-item"
          :class="item.level"
        >
          <span class="history-time">{{ item.timestamp }}</span>
          <span class="history-msg">{{ item.message }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  alarms: { type: Array, default: () => [] },
  alarmHistory: { type: Array, default: () => [] },
  soundEnabled: { type: Boolean, default: true }
})

defineEmits(['acknowledge', 'acknowledgeAll', 'toggleSound', 'exportHistory'])

const hasAlarms = computed(() => props.alarms.length > 0)

const criticalCount = computed(() =>
  props.alarms.filter(a => a.level === 'critical').length
)

const warningCount = computed(() =>
  props.alarms.filter(a => a.level === 'warning').length
)

const infoCount = computed(() =>
  props.alarms.filter(a => a.level === 'info').length
)

const recentHistory = computed(() =>
  props.alarmHistory.slice(-5).reverse()
)
</script>

<style scoped>
.alarm-panel {
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  box-shadow: var(--shadow-md);
}

.alarm-panel.has-alarms {
  border-color: var(--color-danger);
  animation: panel-pulse 2s ease-in-out infinite;
}

@keyframes panel-pulse {
  0%, 100% { box-shadow: 0 0 10px rgba(255, 71, 87, 0.2); }
  50% { box-shadow: 0 0 25px rgba(255, 71, 87, 0.4); }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border-light);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-title {
  color: var(--color-primary);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-title::before {
  content: '◆';
  color: var(--color-primary);
  font-size: 12px;
}

.alarm-counts {
  display: flex;
  gap: 10px;
}

.count {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.count.critical {
  background: rgba(255, 71, 87, 0.15);
  color: var(--color-danger);
  border: 1px solid rgba(255, 71, 87, 0.3);
}

.count.warning {
  background: rgba(250, 173, 20, 0.15);
  color: var(--color-warning);
  border: 1px solid rgba(250, 173, 20, 0.3);
}

.count.info {
  background: rgba(0, 170, 255, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(0, 170, 255, 0.3);
}

.count-num {
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.sound-btn {
  background: transparent;
  border: 1px solid var(--color-border-light);
  color: var(--color-text-secondary);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sound-btn:hover {
  background: rgba(0, 170, 255, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.sound-btn.muted {
  color: var(--color-text-disabled);
  border-color: var(--color-border-light);
}

.sound-btn.muted:hover {
  background: rgba(74, 85, 104, 0.2);
}

.export-btn {
  background: transparent;
  border: 1px solid var(--color-border-light);
  color: var(--color-text-secondary);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.export-btn:hover {
  background: rgba(0, 170, 255, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.ack-all-btn {
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.4);
  color: var(--color-danger);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.ack-all-btn:hover {
  background: rgba(255, 71, 87, 0.2);
}

.alarms-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 200px;
  overflow-y: auto;
}

.alarm-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  border-left: 3px solid;
  animation: slide-in 0.3s ease;
}

@keyframes slide-in {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.alarm-item.critical {
  border-left-color: var(--color-danger);
  background: rgba(255, 71, 87, 0.08);
}

.alarm-item.warning {
  border-left-color: var(--color-warning);
  background: rgba(250, 173, 20, 0.08);
}

.alarm-item.info {
  border-left-color: var(--color-primary);
  background: rgba(0, 170, 255, 0.08);
}

.alarm-indicator {
  flex-shrink: 0;
}

.alarm-led {
  display: block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  animation: blink 1s ease-in-out infinite;
}

.alarm-led.critical {
  background: var(--color-danger);
  box-shadow: 0 0 8px var(--color-danger);
}

.alarm-led.warning {
  background: var(--color-warning);
  box-shadow: 0 0 8px var(--color-warning);
}

.alarm-led.info {
  background: var(--color-primary);
  box-shadow: 0 0 6px var(--color-primary);
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.alarm-content {
  flex: 1;
  min-width: 0;
}

.alarm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.alarm-id {
  color: var(--color-text-tertiary);
  font-size: 10px;
  font-family: 'Courier New', monospace;
}

.alarm-time {
  color: var(--color-text-disabled);
  font-size: 10px;
}

.alarm-message {
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 500;
}

.alarm-ack-btn {
  flex-shrink: 0;
  background: transparent;
  border: 1px solid var(--color-border-light);
  color: var(--color-text-tertiary);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 11px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.alarm-ack-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.no-alarms {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  color: var(--color-accent);
  gap: 12px;
}

.no-alarms svg {
  opacity: 0.6;
}

.no-alarms span {
  font-size: 13px;
}

.alarm-history {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border-light);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  color: var(--color-text-tertiary);
  font-size: 12px;
}

.history-count {
  font-size: 10px;
  opacity: 0.7;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.history-item {
  display: flex;
  gap: 10px;
  font-size: 11px;
  padding: 6px 10px;
  background: var(--color-bg-secondary);
  border-radius: 6px;
}

.history-item.critical .history-msg { color: var(--color-danger); }
.history-item.warning .history-msg { color: var(--color-warning); }
.history-item.info .history-msg { color: var(--color-primary); }

.history-time {
  color: var(--color-text-disabled);
  flex-shrink: 0;
  font-family: 'Courier New', monospace;
}

.history-msg {
  color: var(--color-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
