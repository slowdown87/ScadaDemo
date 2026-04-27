export const EquipmentState = {
  IDLE: 'idle',
  STARTING: 'starting',
  RUNNING: 'running',
  STOPPING: 'stopping',
  FAULT: 'fault',
  MAINTENANCE: 'maintenance'
}

export const EquipmentStateLabels = {
  [EquipmentState.IDLE]: '空闲',
  [EquipmentState.STARTING]: '启动中',
  [EquipmentState.RUNNING]: '运行',
  [EquipmentState.STOPPING]: '停止中',
  [EquipmentState.FAULT]: '故障',
  [EquipmentState.MAINTENANCE]: '维护'
}

export const EquipmentStateColors = {
  [EquipmentState.IDLE]: '#6c757d',
  [EquipmentState.STARTING]: '#ffc107',
  [EquipmentState.RUNNING]: '#28a745',
  [EquipmentState.STOPPING]: '#ffc107',
  [EquipmentState.FAULT]: '#dc3545',
  [EquipmentState.MAINTENANCE]: '#17a2b8'
}

export const FaultType = {
  TEMPERATURE_HIGH: 'temperature_high',
  TEMPERATURE_LOW: 'temperature_low',
  PRESSURE_HIGH: 'pressure_high',
  PRESSURE_LOW: 'pressure_low',
  LEVEL_HIGH: 'level_high',
  LEVEL_LOW: 'level_low',
  FLOW_BLOCKED: 'flow_blocked',
  MOTOR_OVERLOAD: 'motor_overload',
  SENSOR_DRIFT: 'sensor_drift',
  VALVE_STUCK: 'valve_stuck'
}

export const FaultTypeLabels = {
  [FaultType.TEMPERATURE_HIGH]: '温度过高',
  [FaultType.TEMPERATURE_LOW]: '温度过低',
  [FaultType.PRESSURE_HIGH]: '压力过高',
  [FaultType.PRESSURE_LOW]: '压力过低',
  [FaultType.LEVEL_HIGH]: '液位过高',
  [FaultType.LEVEL_LOW]: '液位过低',
  [FaultType.FLOW_BLOCKED]: '管道堵塞',
  [FaultType.MOTOR_OVERLOAD]: '电机过载',
  [FaultType.SENSOR_DRIFT]: '传感器漂移',
  [FaultType.VALVE_STUCK]: '阀门卡滞'
}

export const FaultSeverity = {
  INFO: 'info',
  WARNING: 'warning',
  CRITICAL: 'critical'
}

export function createEquipment(id, name, type, initialState = EquipmentState.IDLE) {
  return {
    id,
    name,
    type,
    state: initialState,
    stateStartTime: Date.now(),
    faults: [],
    faultHistory: [],
    metrics: {
      temperature: 25.0,
      pressure: 1.0,
      level: 50.0,
      flow: 0,
      speed: 0,
      vibration: 0
    },
    settings: {
      tempMin: 20,
      tempMax: 100,
      pressureMin: 0.5,
      pressureMax: 2.0,
      levelMin: 10,
      levelMax: 95,
      flowMin: 5,
      flowMax: 15
    },
    isFaulty: false,
    activeFault: null
  }
}

export function createFault(faultType, severity = FaultSeverity.WARNING, duration = null) {
  return {
    id: `FAULT-${Date.now()}-${Math.random().toString(36).substr(2, 4).toUpperCase()}`,
    type: faultType,
    severity,
    startTime: Date.now(),
    duration,
    injected: false,
    resolved: false,
    resolvedTime: null
  }
}

export const PRESET_SCENARIOS = {
  basic_operation: {
    id: 'basic_operation',
    name: '基础操作训练',
    description: '学习反应釜的启停操作',
    initialEquipment: {
      'R-101': { state: EquipmentState.IDLE, metrics: { temperature: 25, pressure: 1.0, level: 50, flow: 0, speed: 0, vibration: 0 } }
    },
    steps: [
      { title: '检查状态', description: '确认设备空闲', expectedAction: 'check', timeout: 10 },
      { title: '启动预热', description: '启动搅拌器', expectedAction: 'start', timeout: 30 },
      { title: '监控温度', description: '观察温度上升', expectedAction: 'monitor', timeout: 60 },
      { title: '正常停机', description: '逐步降温停机', expectedAction: 'stop', timeout: 45 }
    ],
    scoring: {
      responseTime: { max: 30, weight: 0.3 },
      accuracy: { weight: 0.5 },
      faultHandling: { weight: 0.2 }
    }
  },

  emergency_response: {
    id: 'emergency_response',
    name: '故障应急处理',
    description: '处理温度过高紧急情况',
    initialEquipment: {
      'R-101': { state: EquipmentState.RUNNING, metrics: { temperature: 70, pressure: 1.5, level: 60, flow: 10, speed: 80, vibration: 5 } }
    },
    injectedFaults: [
      { equipmentId: 'R-101', type: FaultType.TEMPERATURE_HIGH, severity: FaultSeverity.CRITICAL, delay: 5000 }
    ],
    steps: [
      { title: '发现报警', description: '温度超过80°C', expectedAction: 'check_alarm', timeout: 15 },
      { title: '确认故障', description: '检查设备状态', expectedAction: 'diagnose', timeout: 20 },
      { title: '采取行动', description: '停止设备', expectedAction: 'emergency_stop', timeout: 30 },
      { title: '记录报告', description: '填写事故报告', expectedAction: 'report', timeout: 45 }
    ],
    scoring: {
      responseTime: { max: 60, weight: 0.4 },
      accuracy: { weight: 0.4 },
      faultHandling: { weight: 0.2 }
    }
  },

  pressure_control: {
    id: 'pressure_control',
    name: '压力控制训练',
    description: '学习压力异常的识别与处理',
    initialEquipment: {
      'R-101': { state: EquipmentState.RUNNING, metrics: { temperature: 60, pressure: 1.2, level: 55, flow: 10, speed: 80, vibration: 5 } }
    },
    injectedFaults: [
      { equipmentId: 'R-101', type: FaultType.PRESSURE_HIGH, severity: FaultSeverity.WARNING, delay: 3000 }
    ],
    steps: [
      { title: '监测压力', description: '观察压力变化趋势', expectedAction: 'monitor', timeout: 20 },
      { title: '识别异常', description: '压力超过1.8atm', expectedAction: 'diagnose', timeout: 15 },
      { title: '采取措施', description: '调节安全阀', expectedAction: 'adjust', timeout: 25 },
      { title: '确认恢复', description: '压力恢复正常范围', expectedAction: 'verify', timeout: 20 }
    ],
    scoring: {
      responseTime: { max: 45, weight: 0.35 },
      accuracy: { weight: 0.45 },
      faultHandling: { weight: 0.2 }
    }
  }
}

export class SimulationEngine {
  constructor() {
    this.equipment = new Map()
    this.scenarios = new Map()
    this.currentScenario = null
    this.simulationTime = 0
    this.isRunning = false
    this.isPaused = false
    this.isSimulating = false
    this.recordings = []
    this.maxRecordingLength = 1000
    this.listeners = []
    this.faultInjectionEnabled = false
    this.simulationSpeed = 1.0
    this.startTimestamp = null
    this.lastUpdate = 0
    this.updateInterval = 100
  }

  addEquipment(equipment) {
    this.equipment.set(equipment.id, equipment)
  }

  getEquipment(id) {
    return this.equipment.get(id)
  }

  getAllEquipment() {
    return Array.from(this.equipment.values())
  }

  setEquipmentState(equipmentId, newState) {
    const equipment = this.equipment.get(equipmentId)
    if (!equipment) return false

    const oldState = equipment.state
    equipment.state = newState
    equipment.stateStartTime = Date.now()

    this.notifyListeners('stateChange', {
      equipmentId,
      oldState,
      newState,
      equipment: { ...equipment }
    })

    return true
  }

  injectFault(equipmentId, faultType, severity = FaultSeverity.WARNING, duration = 30000) {
    const equipment = this.equipment.get(equipmentId)
    if (!equipment) return null

    const fault = createFault(faultType, severity, duration)
    fault.injected = true
    fault.injectedBy = 'manual'

    equipment.faults.push(fault)
    equipment.isFaulty = true
    equipment.activeFault = fault

    this.applyFaultEffect(equipment, fault)

    this.notifyListeners('faultInjected', {
      equipmentId,
      fault: { ...fault }
    })

    return fault
  }

  applyFaultEffect(equipment, fault) {
    switch (fault.type) {
      case FaultType.TEMPERATURE_HIGH:
        equipment.metrics.temperature = equipment.settings.tempMax + 10
        break
      case FaultType.TEMPERATURE_LOW:
        equipment.metrics.temperature = equipment.settings.tempMin - 5
        break
      case FaultType.PRESSURE_HIGH:
        equipment.metrics.pressure = equipment.settings.pressureMax + 0.5
        break
      case FaultType.PRESSURE_LOW:
        equipment.metrics.pressure = equipment.settings.pressureMin - 0.2
        break
      case FaultType.LEVEL_HIGH:
        equipment.metrics.level = equipment.settings.levelMax + 5
        break
      case FaultType.LEVEL_LOW:
        equipment.metrics.level = equipment.settings.levelMin - 5
        break
      case FaultType.FLOW_BLOCKED:
        equipment.metrics.flow = 0
        break
      case FaultType.MOTOR_OVERLOAD:
        equipment.metrics.speed = 0
        equipment.metrics.vibration = 100
        break
      case FaultType.SENSOR_DRIFT:
        equipment.metrics.temperature += (Math.random() - 0.5) * 10
        break
      case FaultType.VALVE_STUCK:
        equipment.metrics.flow = equipment.metrics.flow * 0.1
        break
    }

    this.setEquipmentState(equipment.id, EquipmentState.FAULT)
  }

  updatePhysics(deltaTime) {
    this.equipment.forEach(eq => {
      const dt = deltaTime / 1000

      if (eq.state === EquipmentState.RUNNING && !eq.isFaulty) {
        const heatGain = 0.5 * dt
        const heatLoss = (eq.metrics.temperature - 25) * 0.02 * dt
        eq.metrics.temperature += heatGain - heatLoss
        eq.metrics.temperature = Math.max(25, Math.min(eq.settings.tempMax - 1, eq.metrics.temperature))

        const pressureGain = 0.02 * dt
        const pressureLoss = (eq.metrics.pressure - 1.0) * 0.01 * dt
        eq.metrics.pressure += pressureGain - pressureLoss
        eq.metrics.pressure = Math.max(0.8, Math.min(eq.settings.pressureMax - 0.1, eq.metrics.pressure))

        const inflow = eq.settings.flowMax * 0.6
        const outflow = eq.settings.flowMin * 0.3
        eq.metrics.level += (inflow - outflow) * 0.5 * dt
        eq.metrics.level = Math.max(20, Math.min(90, eq.metrics.level))

        eq.metrics.flow = eq.settings.flowMax * (0.6 + Math.sin(Date.now() / 2000) * 0.1)
        eq.metrics.speed = 100 * (0.8 + Math.sin(Date.now() / 3000) * 0.1)
        eq.metrics.vibration = 5 + Math.random() * 3
      }

      if (eq.isFaulty && eq.activeFault) {
        const fault = eq.activeFault
        switch (fault.type) {
          case FaultType.TEMPERATURE_HIGH:
            eq.metrics.temperature += 2 * dt
            if (eq.metrics.temperature > 120) {
              this.injectSecondaryFault(eq.id, FaultType.PRESSURE_HIGH)
            }
            break
          case FaultType.TEMPERATURE_LOW:
            eq.metrics.temperature -= 1 * dt
            if (eq.metrics.temperature < 10) {
              eq.metrics.temperature = 10
            }
            break
          case FaultType.PRESSURE_HIGH:
            eq.metrics.pressure += 0.05 * dt
            if (eq.metrics.pressure > 2.5) {
              this.injectSecondaryFault(eq.id, FaultType.TEMPERATURE_HIGH)
            }
            break
          case FaultType.PRESSURE_LOW:
            eq.metrics.pressure -= 0.02 * dt
            if (eq.metrics.pressure < 0.3) {
              eq.metrics.pressure = 0.3
            }
            break
          case FaultType.LEVEL_HIGH:
            eq.metrics.level += 0.5 * dt
            if (eq.metrics.level > 100) {
              eq.metrics.level = 100
            }
            break
          case FaultType.LEVEL_LOW:
            eq.metrics.level -= 0.3 * dt
            if (eq.metrics.level < 5) {
              eq.metrics.level = 5
            }
            break
          case FaultType.FLOW_BLOCKED:
            eq.metrics.flow = 0
            break
          case FaultType.MOTOR_OVERLOAD:
            eq.metrics.speed = 0
            eq.metrics.vibration = 100
            break
          case FaultType.SENSOR_DRIFT:
            eq.metrics.temperature += (Math.random() - 0.5) * 0.5
            break
          case FaultType.VALVE_STUCK:
            eq.metrics.flow *= 0.99
            break
        }
      }

      if (eq.state === EquipmentState.IDLE && !eq.isFaulty) {
        eq.metrics.temperature += (25 - eq.metrics.temperature) * 0.01
        eq.metrics.pressure += (1.0 - eq.metrics.pressure) * 0.01
        eq.metrics.flow *= 0.95
        eq.metrics.speed *= 0.95
        eq.metrics.vibration *= 0.9
      }
    })
  }

  injectSecondaryFault(equipmentId, faultType) {
    const equipment = this.equipment.get(equipmentId)
    if (!equipment) return

    const hasFault = equipment.faults.some(f => f.type === faultType)
    if (!hasFault) {
      this.injectFault(equipmentId, faultType, FaultSeverity.CRITICAL)
    }
  }

  tick(timestamp) {
    if (!this.isSimulating) return

    if (this.lastUpdate === 0) this.lastUpdate = timestamp
    const deltaTime = (timestamp - this.lastUpdate) * this.simulationSpeed

    if (deltaTime >= this.updateInterval) {
      this.updatePhysics(deltaTime)
      this.recordState()
      this.simulationTime += deltaTime
      this.notifyListeners('tick', { simulationTime: this.simulationTime })
      this.lastUpdate = timestamp
    }

    if (this.isSimulating) {
      requestAnimationFrame((t) => this.tick(t))
    }
  }

  startSimulation() {
    this.isSimulating = true
    this.isRunning = true
    this.isPaused = false
    this.lastUpdate = 0
    requestAnimationFrame((t) => this.tick(t))
    this.notifyListeners('started', {})
  }

  pauseSimulation() {
    this.isSimulating = false
    this.isPaused = true
    this.notifyListeners('paused', { simulationTime: this.simulationTime })
  }

  resumeSimulation() {
    this.isSimulating = true
    this.isPaused = false
    this.lastUpdate = 0
    requestAnimationFrame((t) => this.tick(t))
    this.notifyListeners('resumed', { simulationTime: this.simulationTime })
  }

  stopSimulation() {
    this.isSimulating = false
    this.isRunning = false
    this.isPaused = false
    this.notifyListeners('stopped', { simulationTime: this.simulationTime })
  }

  resolveFault(equipmentId, faultId) {
    const equipment = this.equipment.get(equipmentId)
    if (!equipment) return false

    const fault = equipment.faults.find(f => f.id === faultId)
    if (!fault) return false

    fault.resolved = true
    fault.resolvedTime = Date.now()

    equipment.faults = equipment.faults.filter(f => f.id !== faultId)
    equipment.isFaulty = equipment.faults.length > 0
    equipment.activeFault = equipment.faults[0] || null

    if (!equipment.isFaulty) {
      this.setEquipmentState(equipment.id, EquipmentState.IDLE)
    }

    this.notifyListeners('faultResolved', {
      equipmentId,
      fault: { ...fault }
    })

    return true
  }

  createScenario(name, description = '') {
    const scenario = {
      id: `SCENARIO-${Date.now()}`,
      name,
      description,
      createdAt: new Date().toISOString(),
      initialStates: new Map(),
      injectedFaults: [],
      duration: 0,
      steps: [],
      completed: false
    }

    this.scenarios.set(scenario.id, scenario)
    return scenario
  }

  addScenarioStep(scenarioId, step) {
    const scenario = this.scenarios.get(scenarioId)
    if (!scenario) return false

    scenario.steps.push({
      id: scenario.steps.length + 1,
      timestamp: this.simulationTime,
      action: step.action,
      description: step.description,
      expectedResult: step.expectedResult,
      score: 0
    })

    return true
  }

  startScenario(scenarioId) {
    const scenario = this.scenarios.get(scenarioId)
    if (!scenario) return false

    this.currentScenario = scenario
    this.simulationTime = 0
    this.recordings = []
    this.startSimulation()

    scenario.equipment.forEach((state, equipmentId) => {
      const equipment = this.equipment.get(equipmentId)
      if (equipment) {
        this.setEquipmentState(equipmentId, state)
      }
    })

    this.notifyListeners('scenarioStarted', { scenario: { ...scenario } })
    return true
  }

  pause() {
    this.pauseSimulation()
  }

  resume() {
    this.resumeSimulation()
  }

  stop() {
    this.stopSimulation()
  }

  start() {
    this.startSimulation()
  }

  rewind(steps = 10) {
    if (this.recordings.length <= steps) {
      this.recordings = []
      this.simulationTime = 0
    } else {
      this.recordings = this.recordings.slice(0, -steps)
      this.simulationTime = Math.max(0, this.simulationTime - steps)
    }

    if (this.recordings.length > 0) {
      const lastState = this.recordings[this.recordings.length - 1]
      this.restoreState(lastState.state)
    }

    this.notifyListeners('rewound', {
      steps,
      simulationTime: this.simulationTime,
      recordingsCount: this.recordings.length
    })
  }

  setSimulationSpeed(speed) {
    this.simulationSpeed = Math.max(0.1, Math.min(10, speed))
    this.notifyListeners('speedChanged', { speed: this.simulationSpeed })
  }

  recordState() {
    const state = {
      timestamp: Date.now(),
      simulationTime: this.simulationTime,
      equipment: new Map(),
      metrics: {}
    }

    this.equipment.forEach((eq, id) => {
      state.equipment.set(id, {
        state: eq.state,
        faults: [...eq.faults],
        metrics: { ...eq.metrics }
      })
    })

    this.recordings.push(state)

    if (this.recordings.length > this.maxRecordingLength) {
      this.recordings.shift()
    }
  }

  restoreState(state) {
    state.equipment.forEach((eqState, id) => {
      const equipment = this.equipment.get(id)
      if (equipment) {
        equipment.state = eqState.state
        equipment.faults = [...eqState.faults]
        equipment.metrics = { ...eqState.metrics }
      }
    })
  }

  getRecording(index) {
    return this.recordings[index] || null
  }

  getCurrentState() {
    const state = {
      simulationTime: this.simulationTime,
      isRunning: this.isRunning,
      isPaused: this.isPaused,
      currentScenario: this.currentScenario ? { ...this.currentScenario } : null,
      equipment: [],
      recordingLength: this.recordings.length
    }

    this.equipment.forEach(eq => {
      state.equipment.push({
        id: eq.id,
        name: eq.name,
        type: eq.type,
        state: eq.state,
        isFaulty: eq.isFaulty,
        activeFault: eq.activeFault,
        metrics: { ...eq.metrics }
      })
    })

    return state
  }

  addListener(callback) {
    this.listeners.push(callback)
  }

  removeListener(callback) {
    this.listeners = this.listeners.filter(l => l !== callback)
  }

  notifyListeners(type, data) {
    this.listeners.forEach(listener => listener(type, data, this.getCurrentState()))
  }

  reset() {
    this.equipment.forEach(eq => {
      eq.state = EquipmentState.IDLE
      eq.faults = []
      eq.isFaulty = false
      eq.activeFault = null
      eq.metrics = {
        temperature: 25.0,
        pressure: 1.0,
        level: 50.0,
        flow: 0,
        speed: 0,
        vibration: 0
      }
    })

    this.simulationTime = 0
    this.recordings = []
    this.isRunning = false
    this.isPaused = false
    this.currentScenario = null

    this.notifyListeners('reset', {})
  }

  dispose() {
    this.reset()
    this.equipment.clear()
    this.scenarios.clear()
    this.listeners = []
  }

  loadScenario(scenarioId) {
    const scenario = PRESET_SCENARIOS[scenarioId]
    if (!scenario) return null

    this.reset()

    Object.entries(scenario.initialEquipment).forEach(([id, config]) => {
      const eq = this.equipment.get(id)
      if (eq) {
        eq.state = config.state || EquipmentState.IDLE
        eq.metrics = { ...config.metrics }
      }
    })

    if (scenario.injectedFaults) {
      scenario.injectedFaults.forEach(fault => {
        setTimeout(() => {
          this.injectFault(fault.equipmentId, fault.type, fault.severity)
        }, fault.delay)
      })
    }

    return scenario
  }

  getScenario(scenarioId) {
    return PRESET_SCENARIOS[scenarioId] || null
  }

  getAllScenarios() {
    return Object.keys(PRESET_SCENARIOS)
  }
}

export const simulationEngine = new SimulationEngine()
export default simulationEngine