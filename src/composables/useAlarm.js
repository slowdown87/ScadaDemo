import { computed } from 'vue'
import { useAlarmStore } from '@/stores/alarmStore'

export const ALARM_LEVELS = {
  5: { name: '紧急', color: '#FF0000', sound: true, flash: true },
  4: { name: '严重', color: '#FF4757', sound: true, flash: false },
  3: { name: '警告', color: '#FF9F43', sound: false, flash: false },
  2: { name: '注意', color: '#FECA57', sound: false, flash: false },
  1: { name: '提示', color: '#54A0FF', sound: false, flash: false }
}

export function useAlarm() {
  const store = useAlarmStore()

  const activeAlarms = computed(() => store.activeAlarms)
  const alarmHistory = computed(() => store.alarmHistory)
  const unacknowledgedCount = computed(() => store.unacknowledgedCount)

  const hasCritical = computed(() => store.hasCritical)
  const hasWarning = computed(() => store.hasWarning)

  function acknowledge(alarmId) {
    store.acknowledgeAlarm(alarmId)
  }

  function acknowledgeAll() {
    store.acknowledgeAll()
  }

  function addAlarm(alarm) {
    store.addAlarm(alarm)
  }

  function getAlarmLevelInfo(level) {
    return ALARM_LEVELS[level] || ALARM_LEVELS[1]
  }

  return {
    activeAlarms,
    alarmHistory,
    unacknowledgedCount,
    hasCritical,
    hasWarning,
    acknowledge,
    acknowledgeAll,
    addAlarm,
    getAlarmLevelInfo,
    ALARM_LEVELS
  }
}
