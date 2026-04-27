<template>
  <span class="animated-number" :style="numberStyle">
    {{ displayValue }}
  </span>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  value: {
    type: Number,
    default: 0
  },
  duration: {
    type: Number,
    default: 500
  },
  decimals: {
    type: Number,
    default: 0
  },
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  }
})

const displayValue = ref(formatNumber(props.value))
let animationFrame = null

function formatNumber(num) {
  const formatted = num.toFixed(props.decimals)
  return `${props.prefix}${formatted}${props.suffix}`
}

function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3)
}

function animateValue(start, end, duration) {
  const startTime = performance.now()

  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
  }

  function update(currentTime) {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    const easeProgress = easeOutCubic(progress)
    const current = start + (end - start) * easeProgress

    displayValue.value = formatNumber(current)

    if (progress < 1) {
      animationFrame = requestAnimationFrame(update)
    }
  }

  animationFrame = requestAnimationFrame(update)
}

watch(() => props.value, (newVal, oldVal) => {
  if (typeof newVal !== 'number' || isNaN(newVal)) {
    displayValue.value = formatNumber(0)
    return
  }
  animateValue(oldVal || 0, newVal, props.duration)
}, { immediate: true })

const numberStyle = computed(() => ({
  fontVariantNumeric: 'tabular-nums'
}))
</script>

<style scoped>
.animated-number {
  display: inline-block;
  font-variant-numeric: tabular-nums;
  transition: color 0.3s ease;
}
</style>
