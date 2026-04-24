import { ref, onUnmounted } from 'vue'

export function useRAF(callback) {
  const isRunning = ref(false)
  let animationId = null
  let lastTime = 0

  function tick(timestamp) {
    if (!isRunning.value) return

    const deltaTime = lastTime ? timestamp - lastTime : 0
    lastTime = timestamp

    callback(deltaTime)

    animationId = requestAnimationFrame(tick)
  }

  function start() {
    if (isRunning.value) return
    isRunning.value = true
    lastTime = 0
    animationId = requestAnimationFrame(tick)
  }

  function stop() {
    isRunning.value = false
    if (animationId !== null) {
      cancelAnimationFrame(animationId)
      animationId = null
    }
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isRunning,
    start,
    stop
  }
}
