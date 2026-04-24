import { ref, shallowRef, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

export function useECharts(containerRef, options = {}) {
  const { renderer = 'canvas', autoresize = true } = options

  const chartInstance = shallowRef(null)
  const isReady = ref(false)

  function initChart() {
    if (!containerRef.value) {
      console.warn('[useECharts] Container is null')
      return
    }

    chartInstance.value = echarts.init(containerRef.value, undefined, {
      renderer,
      width: autoresize ? undefined : containerRef.value.clientWidth,
      height: autoresize ? undefined : containerRef.value.clientHeight
    })

    isReady.value = true
  }

  function setOption(option, notMerge = false) {
    if (!chartInstance.value) return
    chartInstance.value.setOption(option, { notMerge })
  }

  function resize() {
    if (!chartInstance.value || !autoresize) return
    chartInstance.value.resize()
  }

  function dispose() {
    if (chartInstance.value) {
      chartInstance.value.dispose()
      chartInstance.value = null
      isReady.value = false
    }
  }

  onMounted(() => {
    initChart()
    if (autoresize) {
      window.addEventListener('resize', resize)
    }
  })

  onUnmounted(() => {
    dispose()
    if (autoresize) {
      window.removeEventListener('resize', resize)
    }
  })

  return {
    chartInstance,
    isReady,
    setOption,
    resize,
    dispose
  }
}
