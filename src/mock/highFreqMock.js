class HighFreqSimulator {
  constructor() {
    this.dataPoints = 150
    this.updateInterval = 50
    this.listeners = []
    this.running = false
    this.intervalId = null
    this.metrics = {
      fps: 0,
      frameTime: 0,
      updateRate: 0,
      memory: 0,
      dataPoints: 0
    }
    this.history = {
      fps: [],
      frameTime: [],
      temperature: [],
      pressure: [],
      flow: []
    }
    this.temperature = 25
    this.pressure = 1.0
    this.flow = 0
    this.lastUpdateTime = performance.now()
    this.frameCount = 0
    this.lastFrameTime = performance.now()
  }

  start() {
    if (this.running) return
    this.running = true
    this.startMetricsLoop()
    this.startDataLoop()
  }

  stop() {
    this.running = false
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
    }
  }

  startMetricsLoop() {
    const measureFrame = () => {
      if (!this.running) return

      const now = performance.now()
      const delta = now - this.lastFrameTime
      this.lastFrameTime = now

      this.metrics.fps = Math.round(1000 / delta)
      this.metrics.frameTime = Math.round(delta * 100) / 100
      this.metrics.memory = this.getMemoryUsage()
      this.metrics.dataPoints = this.dataPoints

      this.history.fps.push(this.metrics.fps)
      this.history.frameTime.push(this.metrics.frameTime)

      if (this.history.fps.length > 100) this.history.fps.shift()
      if (this.history.frameTime.length > 100) this.history.frameTime.shift()

      this.notifyListeners('metrics', this.metrics)

      requestAnimationFrame(measureFrame)
    }

    requestAnimationFrame(measureFrame)
  }

  startDataLoop() {
    this.intervalId = setInterval(() => {
      if (!this.running) return

      const now = performance.now()
      this.metrics.updateRate = Math.round(1000 / (now - this.lastUpdateTime))
      this.lastUpdateTime = now

      this.temperature += (Math.random() - 0.5) * 2
      this.temperature = Math.max(20, Math.min(100, this.temperature))

      this.pressure += (Math.random() - 0.5) * 0.1
      this.pressure = Math.max(0.5, Math.min(2.5, this.pressure))

      this.flow += (Math.random() - 0.5) * 2
      this.flow = Math.max(0, Math.min(20, this.flow))

      this.history.temperature.push(Math.round(this.temperature * 10) / 10)
      this.history.pressure.push(Math.round(this.pressure * 100) / 100)
      this.history.flow.push(Math.round(this.flow * 10) / 10)

      if (this.history.temperature.length > this.dataPoints) {
        this.history.temperature.shift()
      }
      if (this.history.pressure.length > this.dataPoints) {
        this.history.pressure.shift()
      }
      if (this.history.flow.length > this.dataPoints) {
        this.history.flow.shift()
      }

      this.notifyListeners('data', {
        temperature: this.temperature,
        pressure: this.pressure,
        flow: this.flow,
        history: this.history
      })
    }, this.updateInterval)
  }

  getMemoryUsage() {
    if (performance.memory) {
      return Math.round(performance.memory.usedJSHeapSize / 1048576)
    }
    return 0
  }

  addListener(callback) {
    this.listeners.push(callback)
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(l => l !== callback)
  }

  notifyListeners(type, data) {
    this.listeners.forEach(listener => listener(type, data))
  }

  getHistory() {
    return { ...this.history }
  }

  getMetrics() {
    return { ...this.metrics }
  }

  reset() {
    this.history = {
      fps: [],
      frameTime: [],
      temperature: [],
      pressure: [],
      flow: []
    }
    this.temperature = 25
    this.pressure = 1.0
    this.flow = 0
  }
}

export const highFreqSimulator = new HighFreqSimulator()
export default highFreqSimulator
