<template>
  <div class="trend-container">
    <header class="top-bar">
        <div class="header-left">
          <h1 class="page-title">趋势分析</h1>
          <span class="page-subtitle">温度历史趋势</span>
        </div>
        <div class="header-right">
          <div class="system-info">
            <span class="info-item">实时数据 | 更新间隔: 2s</span>
          </div>
        </div>
      </header>
      <div class="chart-container">
        <div ref="chartRef" class="chart"></div>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { usePlcStore } from '@/stores/plcStore'

const store = usePlcStore()
const chartRef = ref(null)
let chart = null
let updateInterval = null

const colors = {
  primary: '#00aaff',
  accent: '#36d399',
  danger: '#ff4757',
  warning: '#ff9f43',
  text: '#ffffff',
  textDim: 'rgba(255, 255, 255, 0.45)',
  bg: 'rgba(10, 15, 26, 0.95)',
  border: 'rgba(0, 170, 255, 0.3)',
  gridLine: 'rgba(0, 170, 255, 0.15)',
  areaTop: 'rgba(0, 170, 255, 0.4)',
  areaBottom: 'rgba(0, 170, 255, 0.05)'
}

function initChart() {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const option = {
    backgroundColor: colors.bg,
    title: {
      text: '温度趋势曲线',
      textStyle: {
        color: colors.primary,
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
      borderColor: colors.primary,
      borderWidth: 1,
      textStyle: { color: colors.text, fontSize: 13 },
      axisPointer: {
        type: 'line',
        lineStyle: { color: colors.primary, width: 1, type: 'dashed' }
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
        lineStyle: { color: colors.primary, width: 2 }
      },
      axisTick: { show: false },
      axisLabel: {
        color: colors.textDim,
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
        lineStyle: { color: colors.primary, width: 2 }
      },
      axisTick: { show: false },
      axisLabel: {
        color: colors.accent,
        fontSize: 12,
        formatter: '{value}℃'
      },
      splitLine: {
        lineStyle: {
          color: colors.gridLine,
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
          color: colors.primary,
          width: 3,
          shadowColor: 'rgba(0, 170, 255, 0.5)',
          shadowBlur: 10
        },
        itemStyle: {
          color: colors.primary,
          borderWidth: 2,
          borderColor: colors.text
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: colors.areaTop },
            { offset: 1, color: colors.areaBottom }
          ])
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: {
            color: colors.danger,
            width: 2,
            type: 'dashed'
          },
          label: {
            position: 'end',
            formatter: '报警线 {c}℃',
            color: colors.danger,
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
.trend-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: transparent;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
  position: relative;
}

.top-bar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), transparent);
  border-radius: 1px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 2px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title::before {
  content: '◆';
  color: var(--color-primary);
  font-size: 18px;
}

.page-subtitle {
  font-size: 12px;
  color: var(--color-text-tertiary);
  letter-spacing: 1px;
  margin-left: 28px;
}

.header-right {
  display: flex;
  align-items: center;
}

.system-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: var(--color-bg-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid var(--color-border-light);
  border-radius: 20px;
}

.info-item {
  font-size: 12px;
  color: var(--color-text-secondary);
  letter-spacing: 1px;
}

.chart-container {
  flex: 1;
  background: var(--color-bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-lg);
  min-height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

@media (max-width: 1024px) {
  .top-bar {
    flex-direction: column;
    gap: 12px;
  }

  .page-title {
    font-size: 18px;
  }

  .chart-container {
    min-height: 300px;
    padding: 16px;
  }
}
</style>
