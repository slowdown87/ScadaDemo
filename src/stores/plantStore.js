import { defineStore } from 'pinia'
import { ref, computed, onUnmounted } from 'vue'
import { plantSimulator } from '@/mock/plantMock'

export const usePlantStore = defineStore('plant', () => {
  const running = ref(false)
  const tankLevel = ref(50.0)
  const flowRate = ref(0)
  const reactorTemp = ref(25.0)
  const reactorPressure = ref(1.0)
  const motorSpeed = ref(0)
  const productCount = ref(0)
  const productRate = ref(0)
  const productTotal = ref(0)
  const alarms = ref([])
  const alarmHistory = ref([])
  const temperatureHistory = ref([])
  const pressureHistory = ref([])
  const levelHistory = ref([])
  const systemTime = ref('')
  const systemDate = ref('')
  const connectionStatus = ref('ONLINE')
  const softwareVersion = ref('2.0.0')

  const isRunning = computed(() => running.value)

  const hasAlarms = computed(() => alarms.value.length > 0)

  const criticalAlarms = computed(() =>
    alarms.value.filter(a => a.level === 'critical')
  )

  const warningAlarms = computed(() =>
    alarms.value.filter(a => a.level === 'warning')
  )

  const currentTankLevel = computed(() => tankLevel.value.toFixed(1))
  const currentFlowRate = computed(() => flowRate.value.toFixed(1))
  const currentTemp = computed(() => reactorTemp.value.toFixed(1))
  const currentPressure = computed(() => reactorPressure.value.toFixed(2))
  const currentMotorSpeed = computed(() => motorSpeed.value)
  const currentProductCount = computed(() => productCount.value)

  let timeInterval = null
  let initialized = false

  function syncFromSimulator(state) {
    running.value = state.running
    tankLevel.value = state.tankLevel
    flowRate.value = state.flowRate
    reactorTemp.value = state.reactorTemp
    reactorPressure.value = state.reactorPressure
    motorSpeed.value = state.motorSpeed
    productCount.value = state.productCount
    productRate.value = state.productRate
    productTotal.value = state.productTotal
    alarms.value = state.alarms || []
    alarmHistory.value = state.alarmHistory || []
    temperatureHistory.value = state.temperatureHistory || []
    pressureHistory.value = state.pressureHistory || []
    levelHistory.value = state.levelHistory || []
    systemTime.value = state.systemTime
    systemDate.value = state.systemDate
    connectionStatus.value = state.connectionStatus
  }

  function handleUpdate(type, data, state) {
    syncFromSimulator(state)
  }

  function initStore() {
    if (initialized) return

    plantSimulator.init()
    const initialState = plantSimulator.getState()
    syncFromSimulator(initialState)
    plantSimulator.addListener(handleUpdate)

    timeInterval = setInterval(() => {
      plantSimulator.updateTime()
      const state = plantSimulator.getState()
      systemTime.value = state.systemTime
      systemDate.value = state.systemDate
    }, 1000)

    initialized = true
  }

  function start() {
    plantSimulator.start()
    const state = plantSimulator.getState()
    syncFromSimulator(state)
  }

  function stop() {
    plantSimulator.stop()
    const state = plantSimulator.getState()
    syncFromSimulator(state)
  }

  function toggle() {
    plantSimulator.toggle()
    const state = plantSimulator.getState()
    syncFromSimulator(state)
  }

  function reset() {
    plantSimulator.reset()
    const state = plantSimulator.getState()
    syncFromSimulator(state)
  }

  function acknowledgeAlarm(alarmId) {
    plantSimulator.acknowledgeAlarm(alarmId)
    const state = plantSimulator.getState()
    syncFromSimulator(state)
  }

  function acknowledgeAll() {
    plantSimulator.acknowledgeAll()
    const state = plantSimulator.getState()
    syncFromSimulator(state)
  }

  function cleanup() {
    if (timeInterval) {
      clearInterval(timeInterval)
      timeInterval = null
    }
    plantSimulator.removeListener(handleUpdate)
    plantSimulator.stopTimers()
    initialized = false
  }

  return {
    running,
    tankLevel,
    flowRate,
    reactorTemp,
    reactorPressure,
    motorSpeed,
    productCount,
    productRate,
    productTotal,
    alarms,
    alarmHistory,
    temperatureHistory,
    pressureHistory,
    levelHistory,
    systemTime,
    systemDate,
    connectionStatus,
    softwareVersion,
    isRunning,
    hasAlarms,
    criticalAlarms,
    warningAlarms,
    currentTankLevel,
    currentFlowRate,
    currentTemp,
    currentPressure,
    currentMotorSpeed,
    currentProductCount,
    initStore,
    start,
    stop,
    toggle,
    reset,
    acknowledgeAlarm,
    acknowledgeAll,
    cleanup,
    simulator: plantSimulator
  }
})
