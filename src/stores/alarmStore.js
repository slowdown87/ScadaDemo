import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const ALARM_LEVELS = {
  5: { name: '紧急', color: '#FF0000', sound: true, flash: true },
  4: { name: '严重', color: '#FF4757', sound: true, flash: false },
  3: { name: '警告', color: '#FF9F43', sound: false, flash: false },
  2: { name: '注意', color: '#FECA57', sound: false, flash: false },
  1: { name: '提示', color: '#54A0FF', sound: false, flash: false }
}

export const useAlarmStore = defineStore('alarm', () => {
  const activeAlarms = ref([])
  const alarmHistory = ref([])
  const maxHistory = 100
  const soundEnabled = ref(true)
  const onAlarmCallback = ref(null)

  const unacknowledgedCount = computed(() =>
    activeAlarms.value.filter(a => !a.acknowledged).length
  )

  const hasCritical = computed(() =>
    activeAlarms.value.some(a => a.level === 5 && !a.acknowledged)
  )

  const hasWarning = computed(() =>
    activeAlarms.value.some(a => (a.level === 4 || a.level === 3) && !a.acknowledged)
  )

  function setSoundEnabled(enabled) {
    soundEnabled.value = enabled
  }

  function setOnAlarmCallback(callback) {
    onAlarmCallback.value = callback
  }

  function generateAlarmId() {
    return `ALM-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  function addAlarm(alarm) {
    const newAlarm = {
      id: alarm.id || generateAlarmId(),
      deviceId: alarm.deviceId,
      level: alarm.level,
      code: alarm.code,
      message: alarm.message,
      value: alarm.value,
      threshold: alarm.threshold,
      timestamp: alarm.timestamp || new Date(),
      acknowledged: false,
      acknowledgedBy: null,
      acknowledgedAt: null
    }

    activeAlarms.value.unshift(newAlarm)

    if (alarmHistory.value.length >= maxHistory) {
      alarmHistory.value.pop()
    }
    alarmHistory.value.unshift({ ...newAlarm })

    if (soundEnabled.value && onAlarmCallback.value) {
      const levelConfig = ALARM_LEVELS[alarm.level]
      if (levelConfig?.sound) {
        onAlarmCallback.value(alarm.level)
      }
    }

    return newAlarm
  }

  function acknowledgeAlarm(alarmId) {
    const alarm = activeAlarms.value.find(a => a.id === alarmId)
    if (alarm) {
      alarm.acknowledged = true
      alarm.acknowledgedBy = 'Operator'
      alarm.acknowledgedAt = new Date()

      const historyAlarm = alarmHistory.value.find(a => a.id === alarmId)
      if (historyAlarm) {
        historyAlarm.acknowledged = true
        historyAlarm.acknowledgedBy = 'Operator'
        historyAlarm.acknowledgedAt = new Date()
      }
    }
  }

  function acknowledgeAll() {
    const now = new Date()
    activeAlarms.value.forEach(alarm => {
      if (!alarm.acknowledged) {
        alarm.acknowledged = true
        alarm.acknowledgedBy = 'Operator'
        alarm.acknowledgedAt = now
      }
    })

    alarmHistory.value.forEach(alarm => {
      if (!alarm.acknowledged) {
        alarm.acknowledged = true
        alarm.acknowledgedBy = 'Operator'
        alarm.acknowledgedAt = now
      }
    })
  }

  function removeAlarm(alarmId) {
    const index = activeAlarms.value.findIndex(a => a.id === alarmId)
    if (index !== -1) {
      activeAlarms.value.splice(index, 1)
    }
  }

  function clearAll() {
    activeAlarms.value = []
  }

  function getAlarmByDevice(deviceId) {
    return activeAlarms.value.filter(a => a.deviceId === deviceId)
  }

  function getUnacknowledgedAlarms() {
    return activeAlarms.value.filter(a => !a.acknowledged)
  }

  function exportHistory() {
    return alarmHistory.value.map(alarm => ({
      id: alarm.id,
      deviceId: alarm.deviceId,
      level: alarm.level,
      levelName: ALARM_LEVELS[alarm.level]?.name || '未知',
      code: alarm.code,
      message: alarm.message,
      value: alarm.value,
      threshold: alarm.threshold,
      timestamp: alarm.timestamp,
      acknowledged: alarm.acknowledged,
      acknowledgedBy: alarm.acknowledgedBy,
      acknowledgedAt: alarm.acknowledgedAt
    }))
  }

  return {
    activeAlarms,
    alarmHistory,
    unacknowledgedCount,
    hasCritical,
    hasWarning,
    soundEnabled,
    addAlarm,
    acknowledgeAlarm,
    acknowledgeAll,
    removeAlarm,
    clearAll,
    getAlarmByDevice,
    getUnacknowledgedAlarms,
    setSoundEnabled,
    setOnAlarmCallback,
    exportHistory,
    ALARM_LEVELS
  }
})
