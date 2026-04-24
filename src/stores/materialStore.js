import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import {
  LotStatus,
  LotStatusLabels,
  LotStatusColors,
  createMaterialLot,
  createLocationHistoryEntry,
  ProcessLocations,
  ProcessSteps
} from '@/models/materialLot'

export const useMaterialStore = defineStore('material', () => {
  const lots = ref([])
  const selectedLotId = ref(null)
  const isTracking = ref(false)
  const trackingUpdateInterval = ref(null)

  const selectedLot = computed(() =>
    lots.value.find(lot => lot.id === selectedLotId.value) || null
  )

  const activeLots = computed(() =>
    lots.value.filter(lot =>
      lot.status !== LotStatus.COMPLETED && lot.status !== LotStatus.REJECTED
    )
  )

  const inTransitLots = computed(() =>
    lots.value.filter(lot => lot.status === LotStatus.IN_TRANSIT)
  )

  const storedLots = computed(() =>
    lots.value.filter(lot => lot.status === LotStatus.STORED)
  )

  const inProcessLots = computed(() =>
    lots.value.filter(lot => lot.status === LotStatus.IN_PROCESS)
  )

  const lotsByLocation = computed(() => {
    const grouped = {}
    lots.value.forEach(lot => {
      const loc = lot.currentLocation
      if (!grouped[loc]) {
        grouped[loc] = []
      }
      grouped[loc].push(lot)
    })
    return grouped
  })

  const lotStats = computed(() => ({
    total: lots.value.length,
    inTransit: inTransitLots.value.length,
    stored: storedLots.value.length,
    inProcess: inProcessLots.value.length,
    completed: lots.value.filter(l => l.status === LotStatus.COMPLETED).length,
    rejected: lots.value.filter(l => l.status === LotStatus.REJECTED).length
  }))

  function addLot(options = {}) {
    const lot = createMaterialLot({
      ...options,
      history: options.history || [
        createLocationHistoryEntry(options.currentLocation || ProcessLocations.RAW_MATERIAL_STORAGE, 'created')
      ]
    })
    lots.value.push(lot)
    return lot
  }

  function removeLot(lotId) {
    const index = lots.value.findIndex(lot => lot.id === lotId)
    if (index !== -1) {
      lots.value.splice(index, 1)
    }
    if (selectedLotId.value === lotId) {
      selectedLotId.value = null
    }
  }

  function getLot(lotId) {
    return lots.value.find(lot => lot.id === lotId)
  }

  function updateLotStatus(lotId, newStatus, location = null) {
    const lot = getLot(lotId)
    if (!lot) return false

    const oldStatus = lot.status
    lot.status = newStatus
    lot.updatedAt = new Date().toISOString()

    if (location) {
      lot.currentLocation = location
    }

    lot.history.push(createLocationHistoryEntry(
      location || lot.currentLocation,
      `status:${oldStatus}->${newStatus}`
    ))

    return true
  }

  function moveLot(lotId, targetLocation, inTransit = true) {
    const lot = getLot(lotId)
    if (!lot) return false

    if (inTransit) {
      lot.status = LotStatus.IN_TRANSIT
      lot.targetLocation = targetLocation
    }

    lot.history.push(createLocationHistoryEntry(
      targetLocation,
      inTransit ? 'departed' : 'arrived'
    ))

    if (!inTransit) {
      lot.currentLocation = targetLocation
      lot.status = determineNextStatus(lot)
      lot.targetLocation = null
    }

    lot.updatedAt = new Date().toISOString()
    return true
  }

  function determineNextStatus(lot) {
    const nextStep = lot.processStep + 1
    if (nextStep >= ProcessSteps.length) {
      return LotStatus.COMPLETED
    }
    const stepInfo = ProcessSteps[nextStep]
    if (stepInfo.name === '质检') {
      return LotStatus.QC_PENDING
    }
    return LotStatus.IN_PROCESS
  }

  function advanceProcessStep(lotId) {
    const lot = getLot(lotId)
    if (!lot) return false

    const currentStepInfo = ProcessSteps[lot.processStep]
    const nextStep = lot.processStep + 1

    if (nextStep >= ProcessSteps.length) {
      lot.status = LotStatus.COMPLETED
      lot.processStep = nextStep
      lot.history.push(createLocationHistoryEntry(lot.currentLocation, 'process:completed'))
      lot.updatedAt = new Date().toISOString()
      return true
    }

    const nextStepInfo = ProcessSteps[nextStep]
    lot.processStep = nextStep
    lot.currentLocation = nextStepInfo.location
    lot.status = determineNextStatus(lot)
    lot.history.push(createLocationHistoryEntry(
      nextStepInfo.location,
      `process:step${nextStep}:${nextStepInfo.name}`
    ))
    lot.updatedAt = new Date().toISOString()
    return true
  }

  function selectLot(lotId) {
    selectedLotId.value = lotId
  }

  function clearSelection() {
    selectedLotId.value = null
  }

  function getLotTrajectory(lotId) {
    const lot = getLot(lotId)
    if (!lot) return []
    return lot.history.map(h => h.location)
  }

  function getLotsAtLocation(location) {
    return lots.value.filter(lot => lot.currentLocation === location)
  }

  function clearAllLots() {
    lots.value = []
    selectedLotId.value = null
    stopTracking()
  }

  function startTracking(updateFn = null) {
    if (isTracking.value) return
    isTracking.value = true

    trackingUpdateInterval.value = setInterval(() => {
      if (updateFn) {
        updateFn()
      }
    }, 100)
  }

  function stopTracking() {
    if (trackingUpdateInterval.value) {
      clearInterval(trackingUpdateInterval.value)
      trackingUpdateInterval.value = null
    }
    isTracking.value = false
  }

  function initializeDemoLots() {
    clearAllLots()

    addLot({
      id: 'LOT-20260424-001',
      materialId: 'MAT-PE-001',
      materialName: '聚乙烯颗粒 A级',
      quantity: 5000,
      unit: 'kg',
      status: LotStatus.STORED,
      currentLocation: ProcessLocations.RAW_MATERIAL_STORAGE,
      properties: { density: 0.95, viscosity: 'low', color: 'natural' }
    })

    addLot({
      id: 'LOT-20260424-002',
      materialId: 'MAT-PE-002',
      materialName: '聚乙烯颗粒 B级',
      quantity: 3000,
      unit: 'kg',
      status: LotStatus.IN_PROCESS,
      currentLocation: ProcessLocations.REACTOR,
      processStep: 2,
      properties: { density: 0.94, viscosity: 'medium', color: 'natural' }
    })

    addLot({
      id: 'LOT-20260424-003',
      materialId: 'MAT-PP-001',
      materialName: '聚丙烯颗粒',
      quantity: 2000,
      unit: 'kg',
      status: LotStatus.IN_TRANSIT,
      currentLocation: ProcessLocations.REACTOR_LOADING,
      targetLocation: ProcessLocations.REACTOR,
      processStep: 1,
      properties: { density: 0.90, viscosity: 'high', color: 'white' }
    })

    addLot({
      id: 'LOT-20260424-004',
      materialId: 'MAT-FG-001',
      materialName: '成品塑料粒子',
      quantity: 1500,
      unit: 'kg',
      status: LotStatus.QC_PENDING,
      currentLocation: ProcessLocations.QUALITY_CONTROL,
      processStep: 3,
      properties: { density: 0.93, viscosity: 'low', color: 'natural' }
    })

    addLot({
      id: 'LOT-20260424-005',
      materialId: 'MAT-FG-002',
      materialName: '成品塑料粒子',
      quantity: 8000,
      unit: 'kg',
      status: LotStatus.COMPLETED,
      currentLocation: ProcessLocations.PRODUCT_STORAGE,
      processStep: 4,
      properties: { density: 0.93, viscosity: 'low', color: 'natural' }
    })
  }

  return {
    lots,
    selectedLotId,
    isTracking,
    selectedLot,
    activeLots,
    inTransitLots,
    storedLots,
    inProcessLots,
    lotsByLocation,
    lotStats,
    LotStatus,
    LotStatusLabels,
    LotStatusColors,
    ProcessLocations,
    ProcessSteps,
    addLot,
    removeLot,
    getLot,
    updateLotStatus,
    moveLot,
    advanceProcessStep,
    selectLot,
    clearSelection,
    getLotTrajectory,
    getLotsAtLocation,
    clearAllLots,
    startTracking,
    stopTracking,
    initializeDemoLots
  }
})