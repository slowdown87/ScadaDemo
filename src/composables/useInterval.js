import { ref, onUnmounted } from 'vue'

export function useInterval(callback, delay) {
  const isActive = ref(false)
  let timerId = null

  function start() {
    if (isActive.value) return
    isActive.value = true
    timerId = setInterval(callback, delay)
  }

  function stop() {
    if (timerId !== null) {
      clearInterval(timerId)
      timerId = null
    }
    isActive.value = false
  }

  function restart() {
    stop()
    start()
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isActive,
    start,
    stop,
    restart
  }
}
