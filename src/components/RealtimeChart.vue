<template>
  <div class="realtime-chart">
    <div class="chart-header">
      <div class="header-left">
        <span class="chart-title">{{ title }}</span>
      </div>
      <div class="header-right">
        <span class="current-value" :style="{ color: valueColor }">
          {{ currentValue }} {{ unit }}
        </span>
      </div>
    </div>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  title: { type: String, default: '实时数据' },
  data: { type: Array, default: () => [] },
  currentValue: { type: Number, default: 0 },
  unit: { type: String, default: '' },
  maxValue: { type: Number, default: 100 },
  color: { type: String, default: 'var(--color-primary)' }
})

const chartCanvas = ref(null)
let ctx = null
let animationId = null

const colorMap = {
  'var(--color-primary)': '#00aaff',
  'var(--color-accent)': '#36d399',
  'var(--color-danger)': '#ff4757',
  'var(--color-warning)': '#faad14',
  'var(--color-primary-400)': '#40a9ff',
  'var(--color-primary-500)': '#1890ff'
}

function resolveColor(color) {
  return colorMap[color] || color || '#00aaff'
}

const alertColors = {
  danger: '#ff4757',
  warning: '#faad14'
}

const valueColor = computed(() => {
  const value = props.currentValue
  const max = props.maxValue
  const ratio = value / max
  if (ratio > 0.8) return alertColors.danger
  if (ratio > 0.6) return alertColors.warning
  return props.color
})

function drawChart() {
  if (!ctx || !chartCanvas.value) return

  const canvas = chartCanvas.value
  const width = canvas.width
  const height = canvas.height
  const data = props.data.slice(-60)

  ctx.clearRect(0, 0, width, height)

  if (data.length < 2) return

  const maxVal = props.maxValue
  const stepX = width / (data.length - 1)
  const resolvedColor = resolveColor(props.color)
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0, resolvedColor + '40')
  gradient.addColorStop(1, resolvedColor + '00')

  ctx.beginPath()
  ctx.moveTo(0, height)

  data.forEach((value, i) => {
    const x = i * stepX
    const y = height - (value / maxVal * height)
    ctx.lineTo(x, y)
  })

  ctx.lineTo(width, height)
  ctx.closePath()
  ctx.fillStyle = gradient
  ctx.fill()

  ctx.beginPath()
  ctx.strokeStyle = resolvedColor
  ctx.lineWidth = 2
  ctx.shadowBlur = 10
  ctx.shadowColor = resolvedColor

  data.forEach((value, i) => {
    const x = i * stepX
    const y = height - (value / maxVal * height)
    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })

  ctx.stroke()

  const lastX = (data.length - 1) * stepX
  const lastY = height - (data[data.length - 1] / maxVal * height)
  ctx.beginPath()
  ctx.arc(lastX, lastY, 5, 0, Math.PI * 2)
  ctx.fillStyle = resolvedColor
  ctx.shadowBlur = 15
  ctx.shadowColor = resolvedColor
  ctx.fill()
}

function initChart() {
  if (!chartCanvas.value) return
  chartCanvas.value.width = chartCanvas.value.parentElement.clientWidth
  chartCanvas.value.height = 120
  ctx = chartCanvas.value.getContext('2d')
}

watch(() => props.data, drawChart, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', initChart)
})

onUnmounted(() => {
  window.removeEventListener('resize', initChart)
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<style scoped>
.realtime-chart {
  background: var(--color-bg-glass);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow-md);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(0, 170, 255, 0.1), rgba(0, 170, 255, 0.05));
  border-bottom: 1px solid var(--color-border-light);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-title {
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chart-title::before {
  content: '◆';
  color: var(--color-primary);
  font-size: 12px;
}

.header-right {
  display: flex;
  align-items: center;
}

.current-value {
  font-size: 20px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  font-variant-numeric: tabular-nums;
  text-shadow: 0 0 10px currentColor;
}

.chart-container {
  padding: 16px;
  flex: 1;
  display: flex;
  align-items: center;
}

.chart-container canvas {
  display: block;
  width: 100%;
}
</style>
