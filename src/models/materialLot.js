export const LotStatus = {
  IN_TRANSIT: 'in_transit',
  STORED: 'stored',
  IN_PROCESS: 'in_process',
  QC_PENDING: 'qc_pending',
  COMPLETED: 'completed',
  REJECTED: 'rejected'
}

export const LotStatusLabels = {
  [LotStatus.IN_TRANSIT]: '运输中',
  [LotStatus.STORED]: '库存',
  [LotStatus.IN_PROCESS]: '加工中',
  [LotStatus.QC_PENDING]: '待质检',
  [LotStatus.COMPLETED]: '已完成',
  [LotStatus.REJECTED]: '已拒收'
}

export const LotStatusColors = {
  [LotStatus.IN_TRANSIT]: '#00aaff',
  [LotStatus.STORED]: '#36d399',
  [LotStatus.IN_PROCESS]: '#f7b731',
  [LotStatus.QC_PENDING]: '#fa5535',
  [LotStatus.COMPLETED]: '#26de81',
  [LotStatus.REJECTED]: '#fc5c65'
}

export function createMaterialLot(options = {}) {
  const now = new Date()
  return {
    id: options.id || `LOT-${Date.now()}-${Math.random().toString(36).substr(2, 4).toUpperCase()}`,
    materialId: options.materialId || 'MAT-001',
    materialName: options.materialName || '聚乙烯颗粒',
    quantity: options.quantity || 1000,
    unit: options.unit || 'kg',
    status: options.status || LotStatus.STORED,
    currentLocation: options.currentLocation || 'STORAGE-A1',
    sourceLocation: options.sourceLocation || null,
    targetLocation: options.targetLocation || null,
    batchDate: options.batchDate || now.toISOString(),
    expiryDate: options.expiryDate || new Date(now.getTime() + 365 * 24 * 60 * 60 * 1000).toISOString(),
    properties: options.properties || {
      density: 0.95,
      viscosity: 'medium',
      color: 'natural'
    },
    history: options.history || [],
    processStep: options.processStep || 0,
    qualityCheck: options.qualityCheck || null,
    createdAt: options.createdAt || now.toISOString(),
    updatedAt: options.updatedAt || now.toISOString()
  }
}

export function createLocationHistoryEntry(location, status, timestamp = null) {
  return {
    location,
    status,
    timestamp: timestamp || new Date().toISOString()
  }
}

export const ProcessLocations = {
  RAW_MATERIAL_STORAGE: 'RAW-STORAGE',
  REACTOR_LOADING: 'R-LOADING',
  REACTOR: 'R-101',
  MIXING_TANK: 'TK-MIX',
  QUALITY_CONTROL: 'QC-STATION',
  PRODUCT_STORAGE: 'PRODUCT-STORAGE',
  SHIPPING: 'SHIPPING'
}

export const ProcessSteps = [
  { id: 0, name: '原料入库', location: ProcessLocations.RAW_MATERIAL_STORAGE, duration: 0 },
  { id: 1, name: '反应釜加料', location: ProcessLocations.REACTOR_LOADING, duration: 300 },
  { id: 2, name: '反应加工', location: ProcessLocations.REACTOR, duration: 1800 },
  { id: 3, name: '质检', location: ProcessLocations.QUALITY_CONTROL, duration: 300 },
  { id: 4, name: '成品入库', location: ProcessLocations.PRODUCT_STORAGE, duration: 0 }
]
