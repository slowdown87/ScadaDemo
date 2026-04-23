<template>
  <div class="trend-view">
    <div class="view-header">
      <h2>◆ 温度历史趋势</h2>
      <div class="header-info">
        <span class="info-item">实时数据 | 更新间隔: 2s</span>
      </div>
    </div>
    <div class="chart-container">
      <div ref="chartRef" class="chart"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import { usePlcStore } from '@/stores/plcStore'

const store = usePlcStore()
const chartRef = ref(null)
let chart = null
let updateInterval = null

function initChart() {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const option = {
    backgroundColor: 'rgba(10, 15, 26, 0.95)',
    title: {
      text: '温度趋势曲线',
      textStyle: {
        color: '#00aaff',
        fontSize: 18,
        fontWeight: 'normal',
        letterSpacing: 2
      },
      left: 'center',
      top: 15
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: {c}℃',
      backgroundColor: 'rgba(0, 40, 80, 0.95)',
      borderColor: '#00aaff',
      borderWidth: 1,
      textStyle: { color: '#fff', fontSize: 13 },
      axisPointer: {
        type: 'line',
        lineStyle: { color: '#00aaff', width: 1, type: 'dashed' }
      }
    },
    legend: {
      show: false
    },
    grid: {
      left: 55,
      right: 35,
      top: 60,
      bottom: 50,
      containLabel: false
    },
    xAxis: {
      type: 'category',
      data: [],
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: '#00aaff', width: 2 }
      },
      axisTick: { show: false },
      axisLabel: {
        color: '#8892a0',
        fontSize: 11,
        margin: 12
      },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      min: 20,
      max: 80,
      interval: 10,
      axisLine: {
        lineStyle: { color: '#00aaff', width: 2 }
      },
      axisTick: { show: false },
      axisLabel: {
        color: '#36d399',
        fontSize: 12,
        formatter: '{value}℃'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 170, 255, 0.15)',
          width: 1,
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '温度',
        type: 'line',
        smooth: 0.4,
        symbol: 'circle',
        symbolSize: 6,
        sampling: 'lttb',
        data: [],
        lineStyle: {
          color: '#00aaff',
          width: 3,
          shadowColor: 'rgba(0, 170, 255, 0.5)',
          shadowBlur: 10
        },
        itemStyle: {
          color: '#00aaff',
          borderWidth: 2,
          borderColor: '#fff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 170, 255, 0.4)' },
            { offset: 0.5, color: 'rgba(0, 170, 255, 0.2)' },
            { offset: 1, color: 'rgba(0, 170, 255, 0.02)' }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: {
            color: '#ff4444',
            width: 2,
            type: 'dashed'
          },
          label: {
            position: 'end',
            formatter: '报警线 {c}℃',
            color: '#ff4444',
            fontSize: 11
          },
          data: [{ yAxis: 50 }]
        },
        animationDuration: 500,
        animationEasing: 'cubicOut'
      }
    ]
  }

  chart.setOption(option)

  window.addEventListener('resize', handleResize)
}

function handleResize() {
  if (chart) {
    chart.resize()
  }
}

function updateChart() {
  if (!chart) return

  const history = store.temperature_history
  const labels = history.map((_, i) => `${(i + 1) * 2}s`)

  chart.setOption({
    xAxis: { data: labels },
    series: [{
      data: history
    }]
  })
}

onMounted(() => {
  store.initStore()
  initChart()
  updateChart()
  updateInterval = setInterval(updateChart, 2000)
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.trend-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.3);
}

.view-header h2 {
  color: var(--color-primary);
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 3px;
  text-shadow: 0 0 15px rgba(0, 170, 255, 0.4);
  margin: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.info-item {
  font-size: 12px;
  color: var(--color-text-dim);
  letter-spacing: 1px;
}

.chart-container {
  flex: 1;
  background: var(--color-panel);
  border: 1px solid var(--color-primary);
  border-radius: var(--border-radius);
  padding: 20px;
  box-shadow: var(--box-shadow);
  min-height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}
</style>
