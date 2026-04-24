export const LotStatus = {
  IN_TRANSIT: 'in_transit',
  STORED: 'stored',
  IN_PROCESS: 'in_process',
  QC_PENDING: 'qc_pending',
  COMPLETED: 'completed'
}

export const MaterialType = {
  RAW: 'raw',
  INTERMEDIATE: 'intermediate',
  FINISHED: 'finished'
}

export const QualityStatus = {
  PENDING: 'pending',
  PASSED: 'passed',
  FAILED: 'failed',
  WAIVED: 'waived'
}

export const PROCESS_STEPS = {
  STORAGE: 'storage',
  REACTOR: 'reactor',
  MIXING: 'mixing',
  QUALITY_CHECK: 'quality_check',
  PACKAGING: 'packaging'
}

export const DEFAULT_MATERIALS = [
  { id: 'MAT-001', name: '原料A', type: MaterialType.RAW, unit: 'kg' },
  { id: 'MAT-002', name: '原料B', type: MaterialType.RAW, unit: 'kg' },
  { id: 'MAT-003', name: '中间品X', type: MaterialType.INTERMEDIATE, unit: 'L' },
  { id: 'MAT-004', name: '成品Y', type: MaterialType.FINISHED, unit: 'pcs' }
]

export function generateLotId() {
  const timestamp = Date.now().toString(36).toUpperCase()
  const random = Math.random().toString(36).substring(2, 6).toUpperCase()
  return `LOT-${timestamp}-${random}`
}

export function createLocationHistory(location, step, timestamp = new Date()) {
  return {
    location,
    step,
    timestamp,
    duration: 0
  }
}

export function createMaterialLot(options = {}) {
  const {
    id = generateLotId(),
    materialId = 'MAT-001',
    materialName = '未知物料',
    quantity = 0,
    unit = 'kg',
    status = LotStatus.IN_TRANSIT,
    currentLocation = 'STORAGE-A',
    batchDate = new Date()
  } = options

  return {
    id,
    materialId,
    materialName,
    quantity,
    unit,
    status,
    currentLocation,
    batchDate,
    history: [],
    qualityStatus: QualityStatus.PENDING,
    processStep: PROCESS_STEPS.STORAGE,
    createdAt: new Date(),
    updatedAt: new Date()
  }
}
