import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePerfStore = defineStore('perf', () => {
  const fps = ref(60)
  const fpsHistory = ref([])
  const memoryUsage = ref(0)
  const memoryHistory = ref([])
  const dataThroughput = ref(0)
  const renderTime = ref(0)

  const maxHistoryLength = 100

  const avgFps = computed(() => {
    if (fpsHistory.value.length === 0) return 0
    const sum = fpsHistory.value.reduce((a, b) => a + b, 0)
    return Math.round(sum / fpsHistory.value.length)
  })

  const fpsStatus = computed(() => {
    if (fps.value >= 50) return 'good'
    if (fps.value >= 30) return 'warning'
    return 'critical'
  })

  const memoryStatus = computed(() => {
    if (memoryUsage.value < 200) return 'good'
    if (memoryUsage.value < 400) return 'warning'
    return 'critical'
  })

  function updateFps(newFps) {
    fps.value = newFps
    fpsHistory.value.push(newFps)
    if (fpsHistory.value.length > maxHistoryLength) {
      fpsHistory.value.shift()
    }
  }

  function updateMemory(memoryMB) {
    memoryUsage.value = memoryMB
    memoryHistory.value.push(memoryMB)
    if (memoryHistory.value.length > maxHistoryLength) {
      memoryHistory.value.shift()
    }
  }

  function updateThroughput(pointsPerSecond) {
    dataThroughput.value = pointsPerSecond
  }

  function updateRenderTime(ms) {
    renderTime.value = ms
  }

  function getStats() {
    return {
      fps: fps.value,
      avgFps: avgFps.value,
      fpsStatus: fpsStatus.value,
      memory: memoryUsage.value,
      memoryStatus: memoryStatus.value,
      throughput: dataThroughput.value,
      renderTime: renderTime.value
    }
  }

  function reset() {
    fps.value = 60
    fpsHistory.value = []
    memoryUsage.value = 0
    memoryHistory.value = []
    dataThroughput.value = 0
    renderTime.value = 0
  }

  return {
    fps,
    fpsHistory,
    memoryUsage,
    memoryHistory,
    dataThroughput,
    renderTime,
    avgFps,
    fpsStatus,
    memoryStatus,
    updateFps,
    updateMemory,
    updateThroughput,
    updateRenderTime,
    getStats,
    reset
  }
})
