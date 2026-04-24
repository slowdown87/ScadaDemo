import { useAlarmStore, ALARM_LEVELS } from '@/stores/alarmStore'
import { plantSimulator } from '@/mock/plantMock'

export const ALARM_RULES = [
  {
    id: 'A-TEMP-HIGH',
    deviceId: 'R-101',
    param: 'temperature',
    condition: 'high',
    threshold: 100,
    criticalThreshold: 120,
    level: 3,
    criticalLevel: 5,
    message: '反应釜温度过高',
    unit: '°C'
  },
  {
    id: 'A-PRESS-HIGH',
    deviceId: 'R-101',
    param: 'pressure',
    condition: 'high',
    threshold: 1.5,
    criticalThreshold: 1.8,
    level: 3,
    criticalLevel: 4,
    message: '反应釜压力过高',
    unit: 'atm'
  },
  {
    id: 'A-TANK1-LOW',
    deviceId: 'TK-101',
    param: 'level',
    condition: 'low',
    threshold: 20,
    criticalThreshold: 10,
    level: 2,
    criticalLevel: 4,
    message: '储罐TK-101液位过低',
    unit: '%'
  },
  {
    id: 'A-TANK1-HIGH',
    deviceId: 'TK-101',
    param: 'level',
    condition: 'high',
    threshold: 90,
    criticalThreshold: 95,
    level: 2,
    criticalLevel: 4,
    message: '储罐TK-101液位过高',
    unit: '%'
  },
  {
    id: 'A-TANK2-LOW',
    deviceId: 'TK-102',
    param: 'level',
    condition: 'low',
    threshold: 15,
    criticalThreshold: 8,
    level: 2,
    criticalLevel: 3,
    message: '储罐TK-102液位过低',
    unit: '%'
  },
  {
    id: 'A-FLOW-LOW',
    deviceId: 'PIPE-01',
    param: 'flowRate',
    condition: 'low',
    threshold: 5,
    criticalThreshold: 2,
    level: 1,
    criticalLevel: 2,
    message: '管道流量异常',
    unit: 'L/s'
  }
]

export class AlarmEngine {
  constructor() {
    this.store = useAlarmStore()
    this.activeAlarms = new Map()
    this.lastCheck = new Map()
    this.checkInterval = null
    this.soundEnabled = true
    this.flashEnabled = true
    this.audioContext = null
    this.isRunning = false
  }

  init() {
    if (this.isRunning) return
    this.isRunning = true
    this.checkInterval = setInterval(() => this.checkAll(), 500)
  }

  dispose() {
    this.isRunning = false
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
      this.checkInterval = null
    }
    this.activeAlarms.clear()
    this.lastCheck.clear()
  }

  checkAll() {
    ALARM_RULES.forEach(rule => {
      this.evaluateRule(rule)
    })
  }

  evaluateRule(rule) {
    const value = this.getParamValue(rule.deviceId, rule.param)

    if (value === null || value === undefined) return

    let isTriggered = false
    let level = rule.level
    let message = rule.message
    let valueStr = value.toFixed(1)

    if (rule.condition === 'high') {
      if (value >= rule.criticalThreshold) {
        isTriggered = true
        level = rule.criticalLevel
        message = `${rule.message}（严重：${valueStr}${rule.unit}）`
      } else if (value >= rule.threshold) {
        isTriggered = true
        message = `${rule.message}（${valueStr}${rule.unit}）`
      }
    } else if (rule.condition === 'low') {
      if (value <= rule.criticalThreshold) {
        isTriggered = true
        level = rule.criticalLevel
        message = `${rule.message}（严重：${valueStr}${rule.unit}）`
      } else if (value <= rule.threshold) {
        isTriggered = true
        message = `${rule.message}（${valueStr}${rule.unit}）`
      }
    }

    const alarmKey = rule.id

    if (isTriggered && !this.activeAlarms.has(alarmKey)) {
      this.triggerAlarm(rule, level, message, value)
    } else if (!isTriggered && this.activeAlarms.has(alarmKey)) {
      this.resolveAlarm(alarmKey)
    } else if (isTriggered && this.activeAlarms.has(alarmKey)) {
      const alarm = this.activeAlarms.get(alarmKey)
      if (alarm.level !== level) {
        this.updateAlarmLevel(alarmKey, level, message)
      }
    }
  }

  triggerAlarm(rule, level, message, value) {
    const alarm = {
      id: `${rule.id}-${Date.now()}`,
      deviceId: rule.deviceId,
      ruleId: rule.id,
      level: this.formatLevel(level),
      code: rule.id,
      message,
      value,
      threshold: level >= 4 ? rule.criticalThreshold : rule.threshold,
      timestamp: new Date().toLocaleTimeString()
    }

    this.store.addAlarm(alarm)
    this.activeAlarms.set(rule.id, alarm)

    this.playAlarmSound(level)
    this.flashDevice(rule.deviceId, level)
  }

  resolveAlarm(ruleId) {
    const alarm = this.activeAlarms.get(ruleId)
    if (alarm) {
      this.store.removeAlarm(alarm.id)
      this.activeAlarms.delete(ruleId)
    }
  }

  updateAlarmLevel(alarmKey, level, message) {
    const alarm = this.activeAlarms.get(alarmKey)
    if (alarm) {
      alarm.level = this.formatLevel(level)
      alarm.message = message
      alarm.timestamp = new Date().toLocaleTimeString()
    }
  }

  formatLevel(level) {
    if (level >= 5) return 'critical'
    if (level >= 4) return 'critical'
    if (level >= 3) return 'warning'
    return 'info'
  }

  getParamValue(deviceId, param) {
    if (!plantSimulator) return null

    const state = plantSimulator.getState()
    if (!state) return null

    switch (deviceId) {
      case 'R-101':
        if (param === 'temperature') return state.reactorTemp
        if (param === 'pressure') return state.reactorPressure
        break
      case 'TK-101':
      case 'TK-102':
        if (param === 'level') return state.tankLevel
        break
      case 'PIPE-01':
        if (param === 'flowRate') return state.flowRate
        break
    }

    return null
  }

  playAlarmSound(level) {
    if (!this.soundEnabled) return
    if (level < 3) return

    try {
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
      }

      const oscillator = this.audioContext.createOscillator()
      const gainNode = this.audioContext.createGain()

      oscillator.connect(gainNode)
      gainNode.connect(this.audioContext.destination)

      if (level >= 4) {
        oscillator.frequency.value = 880
        oscillator.type = 'square'
      } else {
        oscillator.frequency.value = 440
        oscillator.type = 'sine'
      }

      gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3)

      oscillator.start(this.audioContext.currentTime)
      oscillator.stop(this.audioContext.currentTime + 0.3)
    } catch (e) {
      console.warn('Audio alarm failed:', e)
    }
  }

  flashDevice(deviceId, level) {
    if (!this.flashEnabled) return
    if (level < 4) return
  }

  setSoundEnabled(enabled) {
    this.soundEnabled = enabled
  }

  setFlashEnabled(enabled) {
    this.flashEnabled = enabled
  }

  acknowledgeAlarm(alarmId) {
    this.store.acknowledgeAlarm(alarmId)
  }

  acknowledgeAll() {
    this.store.acknowledgeAll()
  }

  getActiveAlarms() {
    return this.store.activeAlarms
  }

  getAlarmHistory() {
    return this.store.alarmHistory
  }
}

let alarmEngineInstance = null

export function getAlarmEngine() {
  if (!alarmEngineInstance) {
    alarmEngineInstance = new AlarmEngine()
  }
  return alarmEngineInstance
}
