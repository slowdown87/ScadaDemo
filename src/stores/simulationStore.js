import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  simulationEngine,
  EquipmentState,
  EquipmentStateLabels,
  EquipmentStateColors,
  FaultType,
  FaultTypeLabels,
  FaultSeverity
} from '@/mock/simulationEngine'
import { usePlantStore } from './plantStore'

export const useSimulationStore = defineStore('simulation', () => {
  const isInitialized = ref(false)
  const isRunning = ref(false)
  const isPaused = ref(false)
  const simulationTime = ref(0)
  const simulationSpeed = ref(1.0)
  const currentScenario = ref(null)
  const recordings = ref([])
  const equipment = ref([])
  const faults = ref([])
  const scenarios = ref([])
  const operations = ref([])

  let updateInterval = null
  let recordInterval = null

  const equipmentByState = computed(() => {
    const grouped = {}
    Object.values(EquipmentState).forEach(state => {
      grouped[state] = equipment.value.filter(eq => eq.state === state)
    })
    return grouped
  })

  const faultyEquipment = computed(() =>
    equipment.value.filter(eq => eq.isFaulty)
  )

  const equipmentStats = computed(() => {
    const stats = {}
    Object.values(EquipmentState).forEach(state => {
      stats[state] = equipment.value.filter(eq => eq.state === state).length
    })
    stats.total = equipment.value.length
    stats.faulty = faultyEquipment.value.length
    return stats
  })

  function initialize(equipmentList = []) {
    if (isInitialized.value) return

    simulationEngine.reset()

    equipmentList.forEach(eq => {
      simulationEngine.addEquipment(eq)
    })

    equipment.value = simulationEngine.getAllEquipment().map(eq => ({
      id: eq.id,
      name: eq.name,
      type: eq.type,
      state: eq.state,
      isFaulty: eq.isFaulty,
      activeFault: eq.activeFault,
      metrics: { ...eq.metrics },
      settings: { ...eq.settings }
    }))

    simulationEngine.addListener(handleSimulationEvent)

    isInitialized.value = true
  }

  function handleSimulationEvent(type, data) {
    switch (type) {
      case 'stateChange':
        updateEquipmentState(data.equipmentId, data.newState)
        operations.value.push({
          type: 'stateChange',
          equipmentId: data.equipmentId,
          oldState: data.oldState,
          newState: data.newState,
          timestamp: Date.now()
        })
        break

      case 'faultInjected':
        faults.value.push(data.fault)
        updateEquipmentFault(data.equipmentId, data.fault)
        operations.value.push({
          type: 'faultInjected',
          equipmentId: data.equipmentId,
          faultType: data.fault.type,
          timestamp: Date.now()
        })
        break

      case 'faultResolved':
        faults.value = faults.value.filter(f => f.id !== data.fault.id)
        updateEquipmentFault(data.equipmentId, null)
        operations.value.push({
          type: 'faultResolved',
          equipmentId: data.equipmentId,
          faultId: data.fault.id,
          timestamp: Date.now()
        })
        break

      case 'scenarioStarted':
        currentScenario.value = data.scenario
        break

      case 'paused':
        isPaused.value = true
        break

      case 'resumed':
        isPaused.value = false
        break

      case 'stopped':
        isRunning.value = false
        isPaused.value = false
        break

      case 'rewound':
        simulationTime.value = data.simulationTime
        recordings.value = simulationEngine.recordings.map(r => ({
          timestamp: r.timestamp,
          simulationTime: r.simulationTime
        }))
        break

      case 'speedChanged':
        simulationSpeed.value = data.speed
        break

      case 'reset':
        simulationTime.value = 0
        recordings.value = []
        currentScenario.value = null
        faults.value = []
        equipment.value.forEach(eq => {
          eq.state = EquipmentState.IDLE
          eq.isFaulty = false
          eq.activeFault = null
        })
        break
    }
  }

  function updateEquipmentState(equipmentId, newState) {
    const eq = equipment.value.find(e => e.id === equipmentId)
    if (eq) {
      eq.state = newState
    }
  }

  function updateEquipmentFault(equipmentId, fault) {
    const eq = equipment.value.find(e => e.id === equipmentId)
    if (eq) {
      eq.isFaulty = fault !== null
      eq.activeFault = fault
    }
  }

  function start(scenarioId = null) {
    if (scenarioId) {
      simulationEngine.startScenario(scenarioId)
    } else {
      simulationEngine.start()
    }

    isRunning.value = true
    isPaused.value = false

    updateInterval = setInterval(() => {
      if (!isPaused.value) {
        simulationTime.value += 100 * simulationSpeed.value
        updateEquipmentMetrics()
        syncToPlantStore()
      }
    }, 100)

    recordInterval = setInterval(() => {
      if (!isPaused.value) {
        simulationEngine.recordState()
        recordings.value = simulationEngine.recordings.map(r => ({
          timestamp: r.timestamp,
          simulationTime: r.simulationTime
        }))
      }
    }, 1000)
  }

  function pause() {
    simulationEngine.pause()
    isPaused.value = true
  }

  function resume() {
    simulationEngine.resume()
    isPaused.value = false
  }

  function stop() {
    simulationEngine.stop()
    isRunning.value = false
    isPaused.value = false

    if (updateInterval) {
      clearInterval(updateInterval)
      updateInterval = null
    }
    if (recordInterval) {
      clearInterval(recordInterval)
      recordInterval = null
    }
  }

  function rewind(steps = 10) {
    simulationEngine.rewind(steps)
    const lastRecording = simulationEngine.recordings[simulationEngine.recordings.length - 1]
    if (lastRecording) {
      equipment.value.forEach(eq => {
        const eqState = lastRecording.state.equipment.get(eq.id)
        if (eqState) {
          eq.state = eqState.state
          eq.metrics = { ...eqState.metrics }
          eq.faults = [...eqState.faults]
          eq.isFaulty = eqState.faults.length > 0
          eq.activeFault = eqState.faults[0] || null
        }
      })
    }
    simulationTime.value = simulationEngine.simulationTime
  }

  function reset() {
    stop()
    simulationEngine.reset()
    simulationTime.value = 0
    recordings.value = []
    currentScenario.value = null
    faults.value = []
    equipment.value.forEach(eq => {
      eq.state = EquipmentState.IDLE
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
  }

  function setSpeed(speed) {
    simulationEngine.setSimulationSpeed(speed)
    simulationSpeed.value = speed
  }

  function injectFault(equipmentId, faultType, severity = FaultSeverity.WARNING, duration = 30000) {
    const fault = simulationEngine.injectFault(equipmentId, faultType, severity, duration)
    if (fault) {
      faults.value.push(fault)
      const eq = equipment.value.find(e => e.id === equipmentId)
      if (eq) {
        eq.isFaulty = true
        eq.activeFault = fault
        eq.metrics = { ...simulationEngine.getEquipment(equipmentId).metrics }
      }
    }
    return fault
  }

  function resolveFault(equipmentId, faultId) {
    const success = simulationEngine.resolveFault(equipmentId, faultId)
    if (success) {
      faults.value = faults.value.filter(f => f.id !== faultId)
      const eq = equipment.value.find(e => e.id === equipmentId)
      if (eq) {
        eq.isFaulty = faults.value.some(f => f.id === faultId)
        eq.activeFault = faults.value.find(f => f.id === faultId) || null
      }
    }
    return success
  }

  function updateEquipmentMetrics() {
    equipment.value.forEach(eq => {
      const simEq = simulationEngine.getEquipment(eq.id)
      if (simEq) {
        eq.metrics = { ...simEq.metrics }
      }
    })
  }

  function syncToPlantStore() {
    const plant = usePlantStore()

    equipment.value.forEach(eq => {
      const deviceId = mapSimToPlantId(eq.id)
      if (!deviceId) return

      const updateData = {}
      let hasUpdate = false

      if (eq.type === 'reactor') {
        if (eq.metrics.temperature !== undefined) {
          updateData.reactorTemp = eq.metrics.temperature
          hasUpdate = true
        }
        if (eq.metrics.pressure !== undefined) {
          updateData.reactorPressure = eq.metrics.pressure
          hasUpdate = true
        }
      }

      if (eq.type === 'tank') {
        if (eq.metrics.level !== undefined) {
          if (eq.id.includes('TK-101')) {
            updateData.tankLevel = eq.metrics.level
            hasUpdate = true
          }
        }
      }

      if (eq.metrics.flow !== undefined) {
        updateData.flowRate = eq.metrics.flow
        hasUpdate = true
      }

      if (hasUpdate) {
        plant.updateDevice(deviceId, updateData)
      }

      if (eq.isFaulty && eq.activeFault) {
        plant.triggerAlarm({
          deviceId: deviceId,
          level: eq.activeFault.severity === 'critical' ? 4 : 3,
          code: `SIM_${eq.activeFault.type.toUpperCase()}`,
          message: `${eq.name}: ${FaultTypeLabels[eq.activeFault.type]}`,
          value: eq.metrics[getFaultMetric(eq.activeFault.type)],
          threshold: null
        })
      }
    })
  }

  function mapSimToPlantId(simId) {
    const mapping = {
      'R-101': 'R-101',
      'TK-101': 'TK-101',
      'TK-102': 'TK-102',
      'B-101': 'B-101',
      'P-101': 'P-101'
    }
    return mapping[simId] || null
  }

  function getFaultMetric(faultType) {
    const metrics = {
      'TEMPERATURE_HIGH': 'temperature',
      'TEMPERATURE_LOW': 'temperature',
      'PRESSURE_HIGH': 'pressure',
      'PRESSURE_LOW': 'pressure',
      'LEVEL_HIGH': 'level',
      'LEVEL_LOW': 'level'
    }
    return metrics[faultType] || null
  }

  function createScenario(name, description) {
    const scenario = simulationEngine.createScenario(name, description)
    scenarios.value.push({
      id: scenario.id,
      name: scenario.name,
      description: scenario.description,
      createdAt: scenario.createdAt,
      steps: []
    })
    return scenario
  }

  function addScenarioStep(scenarioId, step) {
    simulationEngine.addScenarioStep(scenarioId, step)
    const scenario = scenarios.value.find(s => s.id === scenarioId)
    if (scenario) {
      scenario.steps.push({
        id: scenario.steps.length + 1,
        ...step
      })
    }
  }

  function getEquipmentById(id) {
    return equipment.value.find(eq => eq.id === id)
  }

  function getFaultByEquipment(equipmentId) {
    return faults.value.filter(f => {
      const eq = equipment.value.find(e => e.id === equipmentId)
      return eq && eq.activeFault && eq.activeFault.id === f.id
    })
  }

  function getOperations() {
    return [...operations.value].reverse()
  }

  function clearOperations() {
    operations.value = []
  }

  return {
    isInitialized,
    isRunning,
    isPaused,
    simulationTime,
    simulationSpeed,
    currentScenario,
    recordings,
    equipment,
    faults,
    scenarios,
    operations,
    equipmentByState,
    faultyEquipment,
    equipmentStats,
    EquipmentState,
    EquipmentStateLabels,
    EquipmentStateColors,
    FaultType,
    FaultTypeLabels,
    FaultSeverity,
    initialize,
    start,
    pause,
    resume,
    stop,
    reset,
    rewind,
    setSpeed,
    injectFault,
    resolveFault,
    createScenario,
    addScenarioStep,
    getEquipmentById,
    getFaultByEquipment,
    getOperations,
    clearOperations,
    syncToPlantStore,
    mapSimToPlantId
  }
})