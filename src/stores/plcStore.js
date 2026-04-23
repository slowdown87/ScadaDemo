import { defineStore } from 'pinia'
import { ref, computed, onUnmounted } from 'vue'
import { plcMock } from '@/mock/plcMock'

export const usePlcStore = defineStore('plc', () => {
  const motor_running = ref(false)
  const motor_speed = ref(0)
  const motor_status = ref('IDLE')
  const motor_runtime = ref(0)

  const temperature = ref(25.0)
  const temperature_unit = ref('C')
  const temperature_history = ref([])
  const temp_min = ref(25.0)
  const temp_max = ref(25.0)
  const temp_average = ref(25.0)

  const production_count = ref(0)
  const production_rate = ref(0)
  const production_total = ref(0)
  const shift_count = ref(0)

  const alarm_triggered = ref(false)
  const alarm_temperature = ref(50)
  const alarm_level = ref(0)
  const alarm_message = ref('')
  const alarm_count = ref(0)
  const alarm_history = ref([])

  const system_time = ref('')
  const system_date = ref('')
  const refresh_rate = ref(1000)
  const connection_status = ref('ONLINE')
  const software_version = ref('1.0.0')

  const isRunning = computed(() => motor_running.value)
  const currentTemperature = computed(() => temperature.value.toFixed(1))
  const currentProduction = computed(() => String(production_count.value).padStart(4, '0'))

  let timeInterval = null
  let initialized = false

  function syncFromMock(state) {
    motor_running.value = state.motor_running
    motor_speed.value = state.motor_speed
    motor_status.value = state.motor_status
    motor_runtime.value = state.motor_runtime
    temperature.value = state.temperature
    production_count.value = state.production_count
    production_rate.value = state.production_rate
    production_total.value = state.production_total
    shift_count.value = state.shift_count
    alarm_triggered.value = state.alarm_triggered
    alarm_temperature.value = state.alarm_temperature
    alarm_level.value = state.alarm_level
    alarm_message.value = state.alarm_message
    alarm_count.value = state.alarm_count
    alarm_history.value = state.alarm_history || []
    temperature_history.value = state.temperature_history || []
    temp_min.value = state.temp_min || 25.0
    temp_max.value = state.temp_max || 25.0
    temp_average.value = state.temp_average || 25.0
  }

  function handleMockUpdate(type, data, state) {
    syncFromMock(state)
  }

  function initStore() {
    if (initialized) return

    plcMock.init()
    const initialState = plcMock.getState()
    syncFromMock(initialState)

    plcMock.addListener(handleMockUpdate)

    timeInterval = setInterval(() => {
      const now = new Date()
      system_time.value = now.toLocaleTimeString()
      system_date.value = now.toLocaleDateString()
    }, 1000)

    initialized = true
  }

  function startMotor() {
    plcMock.startMotor()
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function stopMotor() {
    plcMock.stopMotor()
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function toggleMotor() {
    plcMock.toggleMotor()
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function resetProduction() {
    plcMock.resetProduction()
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function acknowledgeAlarm() {
    plcMock.acknowledgeAlarm()
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function resetAll() {
    plcMock.resetAll()
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function updateTemperature() {
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function updateProduction() {
    const state = plcMock.getState()
    syncFromMock(state)
  }

  function updateSystemTime() {
    const now = new Date()
    system_time.value = now.toLocaleTimeString()
    system_date.value = now.toLocaleDateString()
  }

  function cleanup() {
    if (timeInterval) {
      clearInterval(timeInterval)
      timeInterval = null
    }
    plcMock.removeListener(handleMockUpdate)
    plcMock.stopTimers()
    initialized = false
  }

  return {
    motor_running,
    motor_speed,
    motor_status,
    motor_runtime,
    temperature,
    temperature_unit,
    temperature_history,
    temp_min,
    temp_max,
    temp_average,
    production_count,
    production_rate,
    production_total,
    shift_count,
    alarm_triggered,
    alarm_temperature,
    alarm_level,
    alarm_message,
    alarm_count,
    alarm_history,
    system_time,
    system_date,
    refresh_rate,
    connection_status,
    software_version,
    isRunning,
    currentTemperature,
    currentProduction,
    initStore,
    startMotor,
    stopMotor,
    toggleMotor,
    resetProduction,
    acknowledgeAlarm,
    resetAll,
    updateTemperature,
    updateProduction,
    updateSystemTime,
    cleanup,
    plcMock
  }
})
