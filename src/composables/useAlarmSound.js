import { ref, watch, onUnmounted } from 'vue'

export function useAlarmSound() {
  const audioContext = ref(null)
  const isEnabled = ref(true)
  const isPlaying = ref(false)

  function getAudioContext() {
    if (!audioContext.value) {
      audioContext.value = new (window.AudioContext || window.webkitAudioContext)()
    }
    return audioContext.value
  }

  function playAlarmTone(frequency = 800, duration = 200, pattern = 'beep') {
    if (!isEnabled.value || isPlaying.value) return

    try {
      const ctx = getAudioContext()
      if (ctx.state === 'suspended') {
        ctx.resume()
      }

      isPlaying.value = true

      if (pattern === 'beep') {
        playBeep(ctx, frequency, duration)
      } else if (pattern === 'urgent') {
        playUrgent(ctx, frequency, duration)
      } else if (pattern === 'warning') {
        playWarning(ctx, frequency, duration)
      }

      setTimeout(() => {
        isPlaying.value = false
      }, duration)
    } catch (e) {
      console.warn('[AlarmSound] Play failed:', e)
      isPlaying.value = false
    }
  }

  function playBeep(ctx, frequency, duration) {
    const oscillator = ctx.createOscillator()
    const gainNode = ctx.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(ctx.destination)

    oscillator.type = 'sine'
    oscillator.frequency.setValueAtTime(frequency, ctx.currentTime)

    gainNode.gain.setValueAtTime(0.3, ctx.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration / 1000)

    oscillator.start(ctx.currentTime)
    oscillator.stop(ctx.currentTime + duration / 1000)
  }

  function playUrgent(ctx, frequency, duration) {
    for (let i = 0; i < 3; i++) {
      setTimeout(() => {
        playBeep(ctx, frequency, duration / 3)
      }, i * (duration / 3))
    }
  }

  function playWarning(ctx, frequency, duration) {
    const oscillator = ctx.createOscillator()
    const gainNode = ctx.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(ctx.destination)

    oscillator.type = 'square'
    oscillator.frequency.setValueAtTime(frequency, ctx.currentTime)
    oscillator.frequency.linearRampToValueAtTime(frequency * 0.7, ctx.currentTime + duration / 1000)

    gainNode.gain.setValueAtTime(0.2, ctx.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration / 1000)

    oscillator.start(ctx.currentTime)
    oscillator.stop(ctx.currentTime + duration / 1000)
  }

  function playCriticalAlarm() {
    playAlarmTone(1000, 500, 'urgent')
  }

  function playWarningAlarm() {
    playAlarmTone(600, 300, 'warning')
  }

  function playInfoBeep() {
    playAlarmTone(440, 100, 'beep')
  }

  function setEnabled(enabled) {
    isEnabled.value = enabled
  }

  function toggle() {
    isEnabled.value = !isEnabled.value
  }

  function dispose() {
    if (audioContext.value) {
      audioContext.value.close()
      audioContext.value = null
    }
  }

  onUnmounted(() => {
    dispose()
  })

  return {
    isEnabled,
    isPlaying,
    playAlarmTone,
    playCriticalAlarm,
    playWarningAlarm,
    playInfoBeep,
    setEnabled,
    toggle,
    dispose
  }
}
