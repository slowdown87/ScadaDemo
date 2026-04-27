<template>
  <svg
    class="sparkline"
    :viewBox="`0 0 ${width} ${height}`"
    :width="width"
    :height="height"
  >
    <defs>
      <linearGradient :id="gradientId" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" :stop-color="color" stop-opacity="0.4" />
        <stop offset="100%" :stop-color="color" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path
      v-if="filled && points.length > 1"
      :d="areaPath"
      :fill="`url(#${gradientId})`"
      class="sparkline-area"
    />
    <polyline
      :points="points.join(' ')"
      fill="none"
      :stroke="color"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="sparkline-line"
    />
    <circle
      v-if="showDot && pointsArray.length > 0"
      :cx="lastPoint.x"
      :cy="lastPoint.y"
      :r="dotRadius"
      :fill="color"
      class="sparkline-dot"
    />
  </svg>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  width: {
    type: Number,
    default: 100
  },
  height: {
    type: Number,
    default: 30
  },
  color: {
    type: String,
    default: 'var(--color-primary)'
  },
  filled: {
    type: Boolean,
    default: false
  },
  showDot: {
    type: Boolean,
    default: false
  },
  dotRadius: {
    type: Number,
    default: 3
  },
  smooth: {
    type: Boolean,
    default: true
  }
})

const gradientId = ref(`sparkline-gradient-${Math.random().toString(36).substr(2, 9)}`)

const pointsArray = computed(() => {
  if (!props.data || props.data.length < 2) return []

  const max = Math.max(...props.data)
  const min = Math.min(...props.data)
  const range = max - min || 1
  const padding = 2

  return props.data.map((value, index) => ({
    x: (index / (props.data.length - 1)) * (props.width - padding * 2) + padding,
    y: props.height - ((value - min) / range) * (props.height - padding * 2) - padding
  }))
})

const points = computed(() => {
  if (pointsArray.value.length < 2) return []
  return pointsArray.value.map(p => `${p.x},${p.y}`)
})

const lastPoint = computed(() => {
  return pointsArray.value[pointsArray.value.length - 1] || { x: 0, y: 0 }
})

const areaPath = computed(() => {
  if (pointsArray.value.length < 2) return ''
  const first = pointsArray.value[0]
  const last = pointsArray.value[pointsArray.value.length - 1]
  let d = `M ${first.x},${props.height} L ${first.x},${first.y}`

  if (props.smooth && pointsArray.value.length > 2) {
    for (let i = 1; i < pointsArray.value.length; i++) {
      const prev = pointsArray.value[i - 1]
      const curr = pointsArray.value[i]
      const cpx = (prev.x + curr.x) / 2
      d += ` Q ${prev.x},${prev.y} ${cpx},${(prev.y + curr.y) / 2}`
    }
    d += ` Q ${last.x},${last.y} ${last.x},${last.y}`
  } else {
    for (let i = 1; i < pointsArray.value.length; i++) {
      d += ` L ${pointsArray.value[i].x},${pointsArray.value[i].y}`
    }
  }

  d += ` L ${last.x},${props.height} Z`
  return d
})
</script>

<style scoped>
.sparkline {
  display: block;
}

.sparkline-line {
  transition: stroke 0.3s ease;
}

.sparkline-area {
  transition: opacity 0.3s ease;
}

.sparkline:hover .sparkline-line {
  stroke-width: 3;
}

.sparkline:hover .sparkline-area {
  opacity: 0.8;
}

.sparkline-dot {
  transition: r 0.2s ease;
}

.sparkline:hover .sparkline-dot {
  r: 5;
}
</style>
