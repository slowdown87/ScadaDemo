const STORAGE_KEY = 'scada_plc_state'
const TEMP_ALARM_HIGH = 50
const TEMP_ALARM_LOW = 48
const TEMP_UPDATE_INTERVAL = 2000
const PROD_UPDATE_INTERVAL = 1000
const MAX_HISTORY_LENGTH = 60

class PlcSimulator {
  constructor() {
    this.state = {
      motor_running: false,
      motor_speed: 0,
      motor_status: 'IDLE',
      motor_runtime: 0,
      temperature: 25.0,
      production_count: 0,
      production_rate: 0,
      production_total: 0,
      shift_count: 0,
      alarm_triggered: false,
      alarm_temperature: 50,
      alarm_level: 0,
      alarm_message: '',
      alarm_count: 0,
      alarm_history: [],
      temperature_history: [],
      temp_min: 25.0,
      temp_max: 25.0,
      temp_average: 25.0
    }

    this.tempTimer = null
    this.prodTimer = null
    this.runtimeTimer = null
    this.listeners = []
  }

  init() {
    this.loadState()
    return this.state
  }

  loadState() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const parsed = JSON.parse(saved)
        this.state.temperature = parsed.temperature ?? 25.0
        this.state.production_count = parsed.production_count ?? 0
        this.state.production_total = parsed.production_total ?? 0
        this.state.shift_count = parsed.shift_count ?? 0
        this.state.alarm_count = parsed.alarm_count ?? 0
        this.state.temperature_history = parsed.temperature_history ?? []
        this.state.alarm_history = parsed.alarm_history ?? []
        this.state.temp_min = parsed.temp_min ?? this.state.temperature
        this.state.temp_max = parsed.temp_max ?? this.state.temperature
        this.state.temp_average = parsed.temp_average ?? this.state.temperature

        if (this.state.temperature >= TEMP_ALARM_HIGH) {
          this.state.alarm_triggered = true
          this.state.alarm_message = `温度过高！当前温度：${this.state.temperature.toFixed(1)}℃`
        }

        this.state.motor_running = false
        this.state.motor_status = 'IDLE'
        this.state.motor_speed = 0
      }
    } catch (e) {
      console.warn('Failed to load state from storage:', e)
    }
  }

  saveState() {
    try {
      const toSave = {
        temperature: this.state.temperature,
        production_count: this.state.production_count,
        production_total: this.state.production_total,
        shift_count: this.state.shift_count,
        alarm_count: this.state.alarm_count,
        temperature_history: this.state.temperature_history,
        alarm_history: this.state.alarm_history,
        temp_min: this.state.temp_min,
        temp_max: this.state.temp_max,
        temp_average: this.state.temp_average,
        timestamp: Date.now()
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
    } catch (e) {
      console.warn('Failed to save state to storage:', e)
    }
  }

  startMotor() {
    if (this.state.motor_running) return

    this.state.motor_running = true
    this.state.motor_status = 'RUNNING'
    this.state.motor_speed = 1500 + Math.random() * 1500

    this.startTimers()
    this.notifyListeners('motor', this.state.motor_running)
    this.saveState()
  }

  stopMotor() {
    if (!this.state.motor_running) return

    this.state.motor_running = false
    this.state.motor_status = 'IDLE'
    this.state.motor_speed = 0

    this.stopTimers()
    this.notifyListeners('motor', this.state.motor_running)
    this.saveState()
  }

  toggleMotor() {
    if (this.state.motor_running) {
      this.stopMotor()
    } else {
      this.startMotor()
    }
  }

  startTimers() {
    this.stopTimers()

    this.tempTimer = setInterval(() => {
      this.updateTemperature()
    }, TEMP_UPDATE_INTERVAL)

    this.prodTimer = setInterval(() => {
      this.updateProduction()
    }, PROD_UPDATE_INTERVAL)

    this.runtimeTimer = setInterval(() => {
      this.updateRuntime()
    }, 1000)
  }

  stopTimers() {
    if (this.tempTimer) {
      clearInterval(this.tempTimer)
      this.tempTimer = null
    }
    if (this.prodTimer) {
      clearInterval(this.prodTimer)
      this.prodTimer = null
    }
    if (this.runtimeTimer) {
      clearInterval(this.runtimeTimer)
      this.runtimeTimer = null
    }
  }

  updateTemperature() {
    if (!this.state.motor_running) return
    if (this.state.temperature >= 80) return

    this.state.temperature += 0.5
    this.state.temperature = Math.round(this.state.temperature * 10) / 10

    this.state.temperature_history.push(this.state.temperature)
    if (this.state.temperature_history.length > MAX_HISTORY_LENGTH) {
      this.state.temperature_history.shift()
    }

    if (this.state.temperature_history.length > 0) {
      const sum = this.state.temperature_history.reduce((a, b) => a + b, 0)
      this.state.temp_min = Math.min(...this.state.temperature_history)
      this.state.temp_max = Math.max(...this.state.temperature_history)
      this.state.temp_average = Math.round((sum / this.state.temperature_history.length) * 10) / 10
    }

    this.checkAlarm()
    this.notifyListeners('temperature', this.state.temperature)
    this.saveState()
  }

  checkAlarm() {
    if (this.state.temperature >= TEMP_ALARM_HIGH && !this.state.alarm_triggered) {
      this.state.alarm_triggered = true
      this.state.alarm_level = 1
      this.state.alarm_message = `温度过高！当前温度：${this.state.temperature.toFixed(1)}℃`
      this.state.alarm_count++

      this.state.alarm_history.unshift({
        time: new Date().toLocaleTimeString(),
        temperature: this.state.temperature,
        acknowledged: false
      })

      if (this.state.alarm_history.length > 10) {
        this.state.alarm_history.pop()
      }

      this.notifyListeners('alarm', this.state.alarm_triggered)
    } else if (this.state.temperature <= TEMP_ALARM_LOW && this.state.alarm_triggered) {
      this.state.alarm_triggered = false
      this.state.alarm_level = 0
      this.state.alarm_message = ''

      this.notifyListeners('alarm', this.state.alarm_triggered)
    }
  }

  updateProduction() {
    if (!this.state.motor_running) return

    this.state.production_count++
    this.state.production_total++
    this.state.shift_count++

    if (this.state.motor_runtime > 0) {
      this.state.production_rate = Math.round(this.state.production_count / (this.state.motor_runtime / 60))
    }

    this.notifyListeners('production', this.state.production_count)
    this.saveState()
  }

  updateRuntime() {
    if (this.state.motor_running) {
      this.state.motor_runtime++
    }
  }

  acknowledgeAlarm() {
    if (this.state.alarm_history.length > 0) {
      this.state.alarm_history[0].acknowledged = true
    }
    this.state.alarm_triggered = false
    this.state.alarm_level = 0
    this.state.alarm_message = ''
    this.saveState()
  }

  resetProduction() {
    this.state.production_count = 0
    this.state.shift_count = 0
    this.state.production_rate = 0
    this.saveState()
    this.notifyListeners('production', this.state.production_count)
  }

  resetAll() {
    this.stopMotor()
    this.state = {
      motor_running: false,
      motor_speed: 0,
      motor_status: 'IDLE',
      motor_runtime: 0,
      temperature: 25.0,
      production_count: 0,
      production_rate: 0,
      production_total: 0,
      shift_count: 0,
      alarm_triggered: false,
      alarm_temperature: 50,
      alarm_level: 0,
      alarm_message: '',
      alarm_count: 0,
      alarm_history: [],
      temperature_history: [],
      temp_min: 25.0,
      temp_max: 25.0,
      temp_average: 25.0
    }
    localStorage.removeItem(STORAGE_KEY)
    this.notifyListeners('reset', null)
  }

  addListener(callback) {
    this.listeners.push(callback)
  }

  removeListener(callback) {
    const index = this.listeners.indexOf(callback)
    if (index > -1) {
      this.listeners.splice(index, 1)
    }
  }

  notifyListeners(type, data) {
    this.listeners.forEach(cb => {
      try {
        cb(type, data, this.state)
      } catch (e) {
        console.error('Listener error:', e)
      }
    })
  }

  getState() {
    return { ...this.state }
  }

  getMotorState() {
    return {
      running: this.state.motor_running,
      speed: this.state.motor_speed,
      status: this.state.motor_status,
      runtime: this.state.motor_runtime
    }
  }

  getTemperature() {
    return {
      current: this.state.temperature,
      min: this.state.temp_min,
      max: this.state.temp_max,
      average: this.state.temp_average,
      history: [...this.state.temperature_history]
    }
  }

  getProduction() {
    return {
      count: this.state.production_count,
      rate: this.state.production_rate,
      total: this.state.production_total,
      shift: this.state.shift_count
    }
  }

  getAlarmState() {
    return {
      triggered: this.state.alarm_triggered,
      level: this.state.alarm_level,
      message: this.state.alarm_message,
      count: this.state.alarm_count,
      history: [...this.state.alarm_history]
    }
  }
}

export const plcMock = new PlcSimulator()
export default plcMock
