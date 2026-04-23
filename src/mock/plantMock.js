class PlantSimulator {
  constructor() {
    this.state = {
      running: false,
      tankLevel: 50.0,
      flowRate: 0,
      reactorTemp: 25.0,
      reactorPressure: 1.0,
      motorSpeed: 0,
      productCount: 0,
      productRate: 0,
      productTotal: 0,
      alarms: [],
      alarmHistory: [],
      temperatureHistory: [],
      pressureHistory: [],
      levelHistory: [],
      systemTime: '',
      systemDate: '',
      connectionStatus: 'ONLINE',
      softwareVersion: '2.0.0'
    }

    this.listeners = []
    this.temperatureTimer = null
    this.pressureTimer = null
    this.levelTimer = null
    this.productionTimer = null
    this.flowTimer = null
    this.motorTimer = null
    this.historyTimer = null
    this.initialized = false
  }

  init() {
    if (this.initialized) return
    this.updateTime()
    this.initialized = true
  }

  addListener(callback) {
    this.listeners.push(callback)
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(l => l !== callback)
  }

  notifyListeners(type, data) {
    this.listeners.forEach(listener => listener(type, data, this.state))
  }

  getState() {
    return { ...this.state }
  }

  updateTime() {
    const now = new Date()
    this.state.systemTime = now.toLocaleTimeString('zh-CN')
    this.state.systemDate = now.toLocaleDateString('zh-CN')
  }

  start() {
    if (this.state.running) return
    this.state.running = true
    this.startTimers()
    this.notifyListeners('start', this.state)
  }

  stop() {
    if (!this.state.running) return
    this.state.running = false
    this.stopTimers()
    this.notifyListeners('stop', this.state)
  }

  toggle() {
    if (this.state.running) {
      this.stop()
    } else {
      this.start()
    }
  }

  reset() {
    this.stop()
    this.state.productCount = 0
    this.state.productRate = 0
    this.state.temperatureHistory = []
    this.state.pressureHistory = []
    this.state.levelHistory = []
    this.state.alarmHistory = []
    this.state.alarms = []
    this.notifyListeners('reset', this.state)
  }

  startTimers() {
    this.updateFlowRate()
    this.updateMotorSpeed()
    this.updateLevel()
    this.updateProduction()

    this.temperatureTimer = setInterval(() => this.updateTemperature(), 2000)
    this.pressureTimer = setInterval(() => this.updatePressure(), 3000)
    this.flowTimer = setInterval(() => this.updateFlowRate(), 1000)
    this.levelTimer = setInterval(() => this.updateLevel(), 1000)
    this.productionTimer = setInterval(() => this.updateProduction(), 1000)
    this.motorTimer = setInterval(() => this.updateMotorSpeed(), 1000)
    this.historyTimer = setInterval(() => this.updateHistory(), 5000)
  }

  stopTimers() {
    clearInterval(this.temperatureTimer)
    clearInterval(this.pressureTimer)
    clearInterval(this.flowTimer)
    clearInterval(this.levelTimer)
    clearInterval(this.productionTimer)
    clearInterval(this.motorTimer)
    clearInterval(this.historyTimer)

    this.temperatureTimer = null
    this.pressureTimer = null
    this.flowTimer = null
    this.levelTimer = null
    this.productionTimer = null
    this.motorTimer = null
    this.historyTimer = null
  }

  updateTemperature() {
    if (!this.state.running) return
    this.state.reactorTemp += 0.5
    if (this.state.reactorTemp > 100) {
      this.state.reactorTemp = 100
    }
    this.checkAlarms()
    this.notifyListeners('temperature', { temp: this.state.reactorTemp })
  }

  updatePressure() {
    if (!this.state.running) return
    this.state.reactorPressure += 0.1
    if (this.state.reactorPressure > 2.0) {
      this.state.reactorPressure = 2.0
    }
    this.checkAlarms()
    this.notifyListeners('pressure', { pressure: this.state.reactorPressure })
  }

  updateFlowRate() {
    if (!this.state.running) {
      this.state.flowRate = 0
      return
    }
    const baseFlow = 10
    const variation = (Math.random() - 0.5) * 2
    this.state.flowRate = Math.max(5, Math.min(15, baseFlow + variation))
    this.notifyListeners('flow', { flow: this.state.flowRate })
  }

  updateLevel() {
    if (!this.state.running) return
    this.state.tankLevel += 0.5
    if (this.state.tankLevel > 95) {
      this.state.tankLevel = 95
    }
    this.checkAlarms()
    this.notifyListeners('level', { level: this.state.tankLevel })
  }

  updateMotorSpeed() {
    if (!this.state.running) {
      this.state.motorSpeed = 0
      return
    }
    const targetSpeed = 1500
    const variation = (Math.random() - 0.5) * 100
    this.state.motorSpeed = Math.round(targetSpeed + variation)
    this.notifyListeners('motor', { speed: this.state.motorSpeed })
  }

  updateProduction() {
    if (!this.state.running) {
      this.state.productRate = 0
      return
    }
    this.state.productCount += 1
    this.state.productRate = 1
    this.state.productTotal += 1
    this.notifyListeners('production', { count: this.state.productCount, rate: this.state.productRate })
  }

  updateHistory() {
    this.updateTime()
    this.state.temperatureHistory.push({
      time: this.state.systemTime,
      value: this.state.reactorTemp
    })
    this.state.pressureHistory.push({
      time: this.state.systemTime,
      value: this.state.reactorPressure
    })
    this.state.levelHistory.push({
      time: this.state.systemTime,
      value: this.state.tankLevel
    })

    if (this.state.temperatureHistory.length > 100) {
      this.state.temperatureHistory.shift()
    }
    if (this.state.pressureHistory.length > 100) {
      this.state.pressureHistory.shift()
    }
    if (this.state.levelHistory.length > 100) {
      this.state.levelHistory.shift()
    }

    this.notifyListeners('history', {
      temperature: this.state.temperatureHistory,
      pressure: this.state.pressureHistory,
      level: this.state.levelHistory
    })
  }

  checkAlarms() {
    const alarms = []

    if (this.state.reactorTemp > 80) {
      alarms.push({
        id: 'TEMP_HIGH',
        level: this.state.reactorTemp > 90 ? 'critical' : 'warning',
        message: `温度过高: ${this.state.reactorTemp.toFixed(1)}°C`,
        timestamp: new Date().toLocaleTimeString()
      })
    }

    if (this.state.reactorPressure > 1.5) {
      alarms.push({
        id: 'PRESSURE_HIGH',
        level: this.state.reactorPressure > 1.8 ? 'critical' : 'warning',
        message: `压力过高: ${this.state.reactorPressure.toFixed(2)} atm`,
        timestamp: new Date().toLocaleTimeString()
      })
    }

    if (this.state.tankLevel > 90) {
      alarms.push({
        id: 'LEVEL_HIGH',
        level: 'warning',
        message: `液位过高: ${this.state.tankLevel.toFixed(1)}%`,
        timestamp: new Date().toLocaleTimeString()
      })
    }

    if (this.state.tankLevel < 20) {
      alarms.push({
        id: 'LEVEL_LOW',
        level: 'warning',
        message: `液位过低: ${this.state.tankLevel.toFixed(1)}%`,
        timestamp: new Date().toLocaleTimeString()
      })
    }

    if (this.state.flowRate > 15 || this.state.flowRate < 5) {
      alarms.push({
        id: 'FLOW_ABNORMAL',
        level: 'info',
        message: `流量异常: ${this.state.flowRate.toFixed(1)} L/s`,
        timestamp: new Date().toLocaleTimeString()
      })
    }

    if (alarms.length > 0 && this.state.alarms.length === 0) {
      this.state.alarmHistory.push(...alarms)
      if (this.state.alarmHistory.length > 50) {
        this.state.alarmHistory = this.state.alarmHistory.slice(-50)
      }
    }

    this.state.alarms = alarms
    this.notifyListeners('alarms', { alarms: this.state.alarms })
  }

  acknowledgeAlarm(alarmId) {
    this.state.alarms = this.state.alarms.filter(a => a.id !== alarmId)
    this.notifyListeners('alarmAck', { alarmId })
  }

  acknowledgeAll() {
    this.state.alarms = []
    this.notifyListeners('alarmAckAll', {})
  }
}

export const plantSimulator = new PlantSimulator()
export default plantSimulator
