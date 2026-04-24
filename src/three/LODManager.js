import * as THREE from 'three'

export const LOD_LEVELS = {
  HIGH: { distance: 0, segments: 64 },
  MEDIUM: { distance: 50, segments: 32 },
  LOW: { distance: 100, segments: 16 }
}

export class LODManager {
  constructor() {
    this.lodObjects = new Map()
    this.enabled = true
    this.defaultLevel = LOD_LEVELS.HIGH
  }

  register(id, highMesh, mediumMesh, lowMesh) {
    this.lodObjects.set(id, {
      high: highMesh,
      medium: mediumMesh,
      low: lowMesh,
      currentLevel: LOD_LEVELS.HIGH,
      visible: true
    })
    this.setLevel(id, LOD_LEVELS.HIGH)
  }

  registerWithGenerator(id, generator, options = {}) {
    const high = generator(options.high)
    const medium = generator(options.medium)
    const low = generator(options.low)

    if (high) high.visible = false
    if (medium) medium.visible = false
    if (low) low.visible = true

    this.lodObjects.set(id, {
      high,
      medium,
      low,
      currentLevel: LOD_LEVELS.LOW,
      visible: true
    })

    return { high, medium, low }
  }

  setLevel(id, level) {
    const lod = this.lodObjects.get(id)
    if (!lod) return

    if (lod.high) lod.high.visible = level === LOD_LEVELS.HIGH
    if (lod.medium) lod.medium.visible = level === LOD_LEVELS.MEDIUM
    if (lod.low) lod.low.visible = level === LOD_LEVELS.LOW

    lod.currentLevel = level
  }

  update(camera) {
    if (!this.enabled) return

    const cameraPos = camera.position

    this.lodObjects.forEach((lod, id) => {
      if (!lod.high && !lod.medium && !lod.low) return

      const highObj = lod.high || lod.medium || lod.low
      if (!highObj) return

      const distance = cameraPos.distanceTo(highObj.position)

      let targetLevel
      if (distance < LOD_LEVELS.MEDIUM.distance) {
        targetLevel = LOD_LEVELS.HIGH
      } else if (distance < LOD_LEVELS.LOW.distance) {
        targetLevel = LOD_LEVELS.MEDIUM
      } else {
        targetLevel = LOD_LEVELS.LOW
      }

      if (lod.currentLevel !== targetLevel) {
        this.setLevel(id, targetLevel)
      }
    })
  }

  setEnabled(enabled) {
    this.enabled = enabled
  }

  getLODInfo(id) {
    return this.lodObjects.get(id)
  }

  dispose() {
    this.lodObjects.forEach(lod => {
      if (lod.high) {
        lod.high.traverse(child => {
          if (child.geometry) child.geometry.dispose()
        })
      }
      if (lod.medium) {
        lod.medium.traverse(child => {
          if (child.geometry) child.geometry.dispose()
        })
      }
      if (lod.low) {
        lod.low.traverse(child => {
          if (child.geometry) child.geometry.dispose()
        })
      }
    })
    this.lodObjects.clear()
  }
}

export const lodManager = new LODManager()

export default lodManager
