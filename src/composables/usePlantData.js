import { computed } from 'vue'
import { usePlantStore } from '@/stores/plantStore'

export function usePlantData() {
  const store = usePlantStore()

  const data = computed(() => ({
    temperature: parseFloat(store.reactorTemp),
    pressure: parseFloat(store.reactorPressure),
    level: parseFloat(store.tankLevel),
    flowRate: parseFloat(store.flowRate)
  }))

  const isRunning = computed(() => store.isRunning)

  const hasAlarms = computed(() => store.hasAlarms)
  const alarms = computed(() => store.alarms)

  const temperatureHistory = computed(() => store.temperatureHistory)
  const pressureHistory = computed(() => store.pressureHistory)
  const levelHistory = computed(() => store.levelHistory)

  function startPlant() {
    store.start()
  }

  function stopPlant() {
    store.stop()
  }

  function resetPlant() {
    store.reset()
  }

  return {
    data,
    isRunning,
    hasAlarms,
    alarms,
    temperatureHistory,
    pressureHistory,
    levelHistory,
    startPlant,
    stopPlant,
    resetPlant
  }
}
