<template>
  <div class="metrics-panel">
    <div class="panel-header">
      <span>◆ 系统性能</span>
      <span class="status-indicator" :class="{ active: isRunning }">
        {{ isRunning ? '监测中' : '已停止' }}
      </span>
    </div>

    <div class="metrics-grid">
      <div class="metric-card fps">
        <div class="metric-icon">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12,4A8,8 0 0,0 4,12A8,8 0 0,0 12,20A8,8 0 0,0 20,12A8,8 0 0,0 12,4M12,6A6,6 0 0,1 18,12A6,6 0 0,1 12,18A6,6 0 0,1 6,12A6,6 0 0,1 12,6M12,8A4,4 0 0,0 8,12A4,4 0 0,0 12,16A4,4 0 0,0 16,12A4,4 0 0,0 12,8Z"/>
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">帧率 (FPS)</span>
          <span class="metric-value" :class="fpsClass">{{ metrics.fps }}</span>
        </div>
        <div class="metric-bar">
          <div class="bar-fill" :style="{ width: (metrics.fps / 60 * 100) + '%' }" :class="fpsClass"></div>
        </div>
      </div>

      <div class="metric-card frame-time">
        <div class="metric-icon">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20M12,2A10,10 0 0,1 22,12A10,10 0 0,1 12,22A10,10 0 0,1 2,12A10,10 0 0,1 12,2M12.5,7V12.25L17,14.92L16.25,16.15L11,13V7H12.5Z"/>
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">帧时间</span>
          <span class="metric-value">{{ metrics.frameTime }} ms</span>
        </div>
      </div>

      <div class="metric-card update-rate">
        <div class="metric-icon">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M4,4H10L12,6H20A2,2 0 0,1 22,8V18A2,2 0 0,1 20,20H4C2.89,20 2,19.1 2,18V6C2,4.89 2.89,4 4,4M16,18V12H18V18H16M12,18V10H14V18H12Z"/>
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">数据更新率</span>
          <span class="metric-value">{{ metrics.updateRate }} /s</span>
        </div>
      </div>

      <div class="metric-card memory">
        <div class="metric-icon">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M17,17H7V7H17M21,11V9H19V7C19,5.89 18.1,5 17,5H15V3H13V5H11V3H9V5H7C5.89,5 5,5.89 5,7V9H3V11H5V13H3V15H5V17A2,2 0 0,0 7,19H9V21H11V19H13V21H15V19H17A2,2 0 0,0 19,17V15H21V13H19V11M13,13H11V11H13M15,9H9V15H15V9Z"/>
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">内存占用</span>
          <span class="metric-value">{{ metrics.memory }} MB</span>
        </div>
      </div>

      <div class="metric-card data-points">
        <div class="metric-icon">
          <svg viewBox="0 0 24 24" width="24" height="24">
            <path fill="currentColor" d="M3,3H9V7H3V3M15,10H21V14H15V10M15,17H21V21H15V17M13,13H7V23H13V13Z"/>
          </svg>
        </div>
        <div class="metric-content">
          <span class="metric-label">数据点数</span>
          <span class="metric-value">{{ metrics.dataPoints }}</span>
        </div>
      </div>
    </div>

    <div class="quick-chart">
      <div class="chart-header">
        <span>FPS 趋势</span>
      </div>
      <div class="chart-canvas">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

const props = defineProps({
  metrics: { type: Object, default: () => ({ fps: 0, frameTime: 0, updateRate: 0, memory: 0, dataPoints: 0 }) },
  fpsHistory: { type: Array, default: () => [] },
  isRunning: { type: Boolean, default: false }
})

const chartCanvas = ref(null)
let ctx = null
let animationId = null

const fpsClass = computed(() => {
  const fps = props.metrics.fps
  if (fps >= 50) return 'good'
  if (fps >= 30) return 'warning'
  return 'danger'
})

function drawChart() {
  if (!ctx || !chartCanvas.value) return

  const canvas = chartCanvas.value
  const width = canvas.width
  const height = canvas.height

  ctx.clearRect(0, 0, width, height)

  const history = props.fpsHistory.slice(-60)
  if (history.length < 2) return

  const maxFps = 60
  const stepX = width / (history.length - 1)

  ctx.beginPath()
  ctx.strokeStyle = '#00aaff'
  ctx.lineWidth = 2
  ctx.shadowBlur = 5
  ctx.shadowColor = '#00aaff'

  history.forEach((fps, i) => {
    const x = i * stepX
    const y = height - (fps / maxFps * height)
    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })

  ctx.stroke()

  ctx.fillStyle = '#00aaff'
  history.forEach((fps, i) => {
    if (i % 10 === 0) {
      const x = i * stepX
      const y = height - (fps / maxFps * height)
      ctx.beginPath()
      ctx.arc(x, y, 3, 0, Math.PI * 2)
      ctx.fill()
    }
  })
}

function initChart() {
  if (!chartCanvas.value) return
  chartCanvas.value.width = chartCanvas.value.parentElement.clientWidth
  chartCanvas.value.height = 80
  ctx = chartCanvas.value.getContext('2d')
}

watch(() => props.fpsHistory, drawChart, { deep: true })

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
.metrics-panel {
  background: rgba(26, 34, 53, 0.9);
  border: 1px solid rgba(0, 170, 255, 0.3);
  border-radius: 10px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(0, 170, 255, 0.1);
  border-bottom: 1px solid rgba(0, 170, 255, 0.2);
}

.panel-header span:first-child {
  color: #00aaff;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
}

.status-indicator {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 10px;
  background: rgba(74, 85, 104, 0.3);
  color: #4a5568;
}

.status-indicator.active {
  background: rgba(54, 211, 153, 0.2);
  color: #36d399;
  animation: pulse-status 1.5s ease-in-out infinite;
}

@keyframes pulse-status {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 15px;
}

.metric-card {
  background: rgba(18, 24, 38, 0.8);
  border: 1px solid rgba(0, 170, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.metric-icon {
  color: #00aaff;
  opacity: 0.7;
}

.metric-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  color: #5a6a8a;
  font-size: 10px;
  text-transform: uppercase;
}

.metric-value {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.metric-value.good { color: #36d399; }
.metric-value.warning { color: #f39c12; }
.metric-value.danger { color: #ff4757; }

.metric-bar {
  height: 3px;
  background: rgba(0, 170, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.bar-fill.good { background: #36d399; }
.bar-fill.warning { background: #f39c12; }
.bar-fill.danger { background: #ff4757; }

.quick-chart {
  margin: 0 15px 15px;
  background: rgba(18, 24, 38, 0.8);
  border: 1px solid rgba(0, 170, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
}

.chart-header {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.chart-header span {
  color: #5a6a8a;
  font-size: 11px;
  text-transform: uppercase;
}

.chart-canvas {
  padding: 10px;
}

.chart-canvas canvas {
  display: block;
  width: 100%;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
