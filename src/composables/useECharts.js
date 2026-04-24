import { ref, shallowRef, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

export function useECharts(containerRef, options = {}) {
  const { renderer = 'canvas', autoresize = true, manualUpdate = true } = options

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

    if (manualUpdate) {
      chartInstance.value.setOption({ series: [] })
    }

    isReady.value = true
  }

  function setOption(option, notMerge = false) {
    if (!chartInstance.value) return

    if (manualUpdate) {
      chartInstance.value.setOption(option, { notMerge: false, replaceMerge: ['series'] })
    } else {
      chartInstance.value.setOption(option, { notMerge })
    }
  }

  function appendData(seriesIndex, data) {
    if (!chartInstance.value) return

    try {
      chartInstance.value.appendData({
        seriesIndex,
        data
      })
    } catch (e) {
      chartInstance.value.setOption({
        series: [{ data }]
      }, { notMerge: true })
    }
  }

  function updateSeriesData(seriesIndex, newData) {
    if (!chartInstance.value) return

    try {
      chartInstance.value.setOption({
        series: [{
          data: newData
        }]
      }, { notMerge: false, replaceMerge: ['series'] })
    } catch (e) {
      console.warn('[useECharts] updateSeriesData failed:', e)
    }
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
    appendData,
    updateSeriesData,
    resize,
    dispose
  }
}
