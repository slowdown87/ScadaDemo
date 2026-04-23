<template>
  <div class="realtime-chart">
    <div class="chart-header">
      <div class="header-left">
        <span class="chart-title">◆ {{ title }}</span>
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
  color: { type: String, default: '#00aaff' }
})

const chartCanvas = ref(null)
let ctx = null
let animationId = null

const valueColor = computed(() => {
  const value = props.currentValue
  const max = props.maxValue
  const ratio = value / max
  if (ratio > 0.8) return '#ff4757'
  if (ratio > 0.6) return '#f39c12'
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
  const gradient = ctx.createLinearGradient(0, 0, 0, height)
  gradient.addColorStop(0, props.color + '40')
  gradient.addColorStop(1, props.color + '00')

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
  ctx.strokeStyle = props.color
  ctx.lineWidth = 2
  ctx.shadowBlur = 10
  ctx.shadowColor = props.color

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
  ctx.fillStyle = props.color
  ctx.shadowBlur = 15
  ctx.shadowColor = props.color
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
  background: rgba(26, 34, 53, 0.9);
  border: 1px solid rgba(0, 170, 255, 0.3);
  border-radius: 10px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(0, 170, 255, 0.1);
  border-bottom: 1px solid rgba(0, 170, 255, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chart-title {
  color: #00aaff;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
}

.header-right {
  display: flex;
  align-items: center;
}

.current-value {
  font-size: 20px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 10px currentColor;
}

.chart-container {
  padding: 15px;
}

.chart-container canvas {
  display: block;
  width: 100%;
}
</style>
