import * as THREE from 'three'
import { COLORS, MATERIAL_PROPS } from './constants.js'

class MaterialLibrary {
  constructor() {
    this._materials = new Map()
  }

  get(key) {
    return this._materials.get(key)
  }

  has(key) {
    return this._materials.has(key)
  }

  set(key, material) {
    this._materials.set(key, material)
  }

  metal(color, props = {}) {
    const key = `metal_${color}_${JSON.stringify(props)}`
    if (this.has(key)) return this.get(key)

    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: MATERIAL_PROPS.metal.roughness,
      metalness: MATERIAL_PROPS.metal.metalness,
      ...props
    })
    this.set(key, material)
    return material
  }

  steel(color, props = {}) {
    const key = `steel_${color}_${JSON.stringify(props)}`
    if (this.has(key)) return this.get(key)

    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: MATERIAL_PROPS.steel.roughness,
      metalness: MATERIAL_PROPS.steel.metalness,
      ...props
    })
    this.set(key, material)
    return material
  }

  roughMetal(color, props = {}) {
    const key = `roughMetal_${color}_${JSON.stringify(props)}`
    if (this.has(key)) return this.get(key)

    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: MATERIAL_PROPS.roughMetal.roughness,
      metalness: MATERIAL_PROPS.roughMetal.metalness,
      ...props
    })
    this.set(key, material)
    return material
  }

  plastic(color, props = {}) {
    const key = `plastic_${color}_${JSON.stringify(props)}`
    if (this.has(key)) return this.get(key)

    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: MATERIAL_PROPS.plastic.roughness,
      metalness: MATERIAL_PROPS.plastic.metalness,
      ...props
    })
    this.set(key, material)
    return material
  }

  rubber(color, props = {}) {
    const key = `rubber_${color}_${JSON.stringify(props)}`
    if (this.has(key)) return this.get(key)

    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: MATERIAL_PROPS.rubber.roughness,
      metalness: MATERIAL_PROPS.rubber.metalness,
      ...props
    })
    this.set(key, material)
    return material
  }

  glass(color = COLORS.indicators.liquid, props = {}) {
    const key = `glass_${color}_${JSON.stringify(props)}`
    if (this.has(key)) return this.get(key)

    const material = new THREE.MeshStandardMaterial({
      color,
      roughness: MATERIAL_PROPS.glass.roughness,
      metalness: MATERIAL_PROPS.glass.metalness,
      transparent: MATERIAL_PROPS.glass.transparent,
      opacity: MATERIAL_PROPS.glass.opacity,
      ...props
    })
    this.set(key, material)
    return material
  }

  emissive(color, intensity = 0.8, props = {}) {
    const key = `emissive_${color}_${intensity}_${JSON.stringify(props)}`
    if (this.has(key)) return this.get(key)

    const material = new THREE.MeshStandardMaterial({
      color,
      emissive: color,
      emissiveIntensity: intensity,
      roughness: MATERIAL_PROPS.emissive.roughness,
      metalness: MATERIAL_PROPS.emissive.metalness,
      ...props
    })
    this.set(key, material)
    return material
  }

  ground() {
    if (this.has('ground')) return this.get('ground')
    const material = new THREE.MeshStandardMaterial({
      color: COLORS.industrial.ground,
      roughness: MATERIAL_PROPS.ground.roughness,
      metalness: MATERIAL_PROPS.ground.metalness
    })
    this.set('ground', material)
    return material
  }

  getStandardMaterials() {
    return {
      reactorBody: this.metal(COLORS.equipment.reactor),
      tankBody: this.metal(COLORS.equipment.tank),
      pipe: this.metal(COLORS.equipment.pipe),
      pipeElbow: this.steel(COLORS.equipment.pipe),
      valveBody: this.metal(COLORS.equipment.valve),
      valveWheel: this.plastic(COLORS.equipment.valveWheel),
      conveyorFrame: this.roughMetal(COLORS.equipment.conveyor),
      conveyorBelt: this.rubber(0x2a2a2a),
      structure: this.roughMetal(COLORS.equipment.structure),
      insulation: this.roughMetal(COLORS.equipment.insulation),
      ground: this.ground(),
      safetyYellow: this.emissive(COLORS.safety.yellow, 0.1),
      indicatorRunning: this.emissive(COLORS.indicators.running, 0.8),
      indicatorAlarm: this.emissive(COLORS.indicators.alarm, 1.0),
      indicatorWarning: this.emissive(COLORS.indicators.warning, 0.8),
      liquid: this.glass(COLORS.indicators.liquid, { opacity: 0.3 }),
      product: this.emissive(COLORS.indicators.product, 0.3),
      instrumentPanel: this.roughMetal(0x404040, { roughness: 0.7, metalness: 0.3 }),
      instrumentScreen: this.emissive(0x00aaff, 0.5),
      instrumentButton: this.emissive(COLORS.indicators.running, 0.5),
      instrumentLight: this.emissive(COLORS.indicators.running, 0.9),
      workerBody: this.roughMetal(COLORS.worker.body, { roughness: 0.7, metalness: 0.3 }),
      workerHead: this.roughMetal(COLORS.worker.head, { roughness: 0.8, metalness: 0.1 }),
      workerHelmet: this.emissive(COLORS.worker.helmet, 0.2),
      lamp: this.roughMetal(0x303030),
      lampGlow: this.emissive(COLORS.lights.lamp, 1.0),
      white: this.metal(COLORS.safety.white, { roughness: 0.6, metalness: 0.2 }),
      black: this.metal(COLORS.industrial.black)
    }
  }

  dispose() {
    this._materials.forEach(material => {
      material.dispose()
    })
    this._materials.clear()
  }
}

export const materials = new MaterialLibrary()

export function createEmissiveMaterial(color, intensity) {
  return new THREE.MeshStandardMaterial({
    color,
    emissive: color,
    emissiveIntensity: intensity,
    roughness: 0.2,
    metalness: 0.5
  })
}

export function createGlassMaterial(color = 0x88ccff, opacity = 0.4) {
  return new THREE.MeshStandardMaterial({
    color,
    transparent: true,
    opacity,
    roughness: 0.05,
    metalness: 0.3
  })
}

export default materials
