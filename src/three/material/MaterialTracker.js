import * as THREE from 'three'
import { LotStatus, LotStatusColors, ProcessLocations } from '@/models/materialLot'

const LOCATION_3D_POSITIONS = {
  [ProcessLocations.RAW_MATERIAL_STORAGE]: new THREE.Vector3(-25, 0, 15),
  [ProcessLocations.REACTOR_LOADING]: new THREE.Vector3(-8, 5, 5),
  [ProcessLocations.REACTOR]: new THREE.Vector3(0, 5, 0),
  [ProcessLocations.MIXING_TANK]: new THREE.Vector3(10, 5, 0),
  [ProcessLocations.QUALITY_CONTROL]: new THREE.Vector3(20, 0, 10),
  [ProcessLocations.PRODUCT_STORAGE]: new THREE.Vector3(25, 0, 15),
  [ProcessLocations.SHIPPING]: new THREE.Vector3(30, 0, 20)
}

export class MaterialTracker {
  constructor(scene) {
    this.scene = scene
    this.lotMeshes = new Map()
    this.lotAnimations = new Map()
    this.trailLines = new Map()
    this.materials = this.createMaterials()
    this.needsUpdate = false
  }

  createMaterials() {
    return {
      [LotStatus.IN_TRANSIT]: new THREE.MeshStandardMaterial({
        color: LotStatusColors[LotStatus.IN_TRANSIT],
        emissive: LotStatusColors[LotStatus.IN_TRANSIT],
        emissiveIntensity: 0.5,
        metalness: 0.3,
        roughness: 0.4
      }),
      [LotStatus.STORED]: new THREE.MeshStandardMaterial({
        color: LotStatusColors[LotStatus.STORED],
        emissive: LotStatusColors[LotStatus.STORED],
        emissiveIntensity: 0.3,
        metalness: 0.5,
        roughness: 0.5
      }),
      [LotStatus.IN_PROCESS]: new THREE.MeshStandardMaterial({
        color: LotStatusColors[LotStatus.IN_PROCESS],
        emissive: LotStatusColors[LotStatus.IN_PROCESS],
        emissiveIntensity: 0.6,
        metalness: 0.3,
        roughness: 0.4
      }),
      [LotStatus.QC_PENDING]: new THREE.MeshStandardMaterial({
        color: LotStatusColors[LotStatus.QC_PENDING],
        emissive: LotStatusColors[LotStatus.QC_PENDING],
        emissiveIntensity: 0.8,
        metalness: 0.2,
        roughness: 0.3
      }),
      [LotStatus.COMPLETED]: new THREE.MeshStandardMaterial({
        color: LotStatusColors[LotStatus.COMPLETED],
        emissive: LotStatusColors[LotStatus.COMPLETED],
        emissiveIntensity: 0.2,
        metalness: 0.6,
        roughness: 0.3
      }),
      [LotStatus.REJECTED]: new THREE.MeshStandardMaterial({
        color: LotStatusColors[LotStatus.REJECTED],
        emissive: LotStatusColors[LotStatus.REJECTED],
        emissiveIntensity: 0.8,
        metalness: 0.2,
        roughness: 0.4
      })
    }
  }

  createLotMesh(lot) {
    const size = 1.5 + Math.min(lot.quantity / 2000, 1)
    const geometry = new THREE.BoxGeometry(size, size, size)
    const material = this.materials[lot.status] || this.materials[LotStatus.STORED]
    const mesh = new THREE.Mesh(geometry, material)

    mesh.castShadow = true
    mesh.receiveShadow = true
    mesh.userData.lotId = lot.id
    mesh.userData.type = 'materialLot'

    const targetPos = LOCATION_3D_POSITIONS[lot.currentLocation]
    if (targetPos) {
      mesh.position.copy(targetPos).add(new THREE.Vector3(
        (Math.random() - 0.5) * 2,
        size / 2,
        (Math.random() - 0.5) * 2
      ))
    }

    this.lotMeshes.set(lot.id, mesh)
    this.scene.add(mesh)

    this.createTrailLine(lot)

    this.needsUpdate = true
    return mesh
  }

  createTrailLine(lot) {
    if (lot.history.length < 2) return

    const points = lot.history.map(h => {
      const pos = LOCATION_3D_POSITIONS[h.location]
      return pos ? pos.clone().add(new THREE.Vector3(0, 1, 0)) : new THREE.Vector3(0, 1, 0)
    })

    const geometry = new THREE.BufferGeometry().setFromPoints(points)
    const material = new THREE.LineBasicMaterial({
      color: LotStatusColors[lot.status],
      opacity: 0.5,
      transparent: true
    })

    const line = new THREE.Line(geometry, material)
    this.trailLines.set(lot.id, line)
    this.scene.add(line)
  }

  updateLotMesh(lot) {
    let mesh = this.lotMeshes.get(lot.id)

    if (!mesh) {
      mesh = this.createLotMesh(lot)
      return
    }

    mesh.material = this.materials[lot.status] || mesh.material

    if (lot.status === LotStatus.IN_TRANSIT && lot.targetLocation) {
      this.animateLotMovement(lot)
    } else {
      const targetPos = LOCATION_3D_POSITIONS[lot.currentLocation]
      if (targetPos) {
        const offset = new THREE.Vector3(
          (Math.random() - 0.5) * 0.1,
          0,
          (Math.random() - 0.5) * 0.1
        )
        mesh.position.copy(targetPos).add(offset).add(new THREE.Vector3(0, 1, 0))
      }
    }

    mesh.rotation.y += 0.01
    this.needsUpdate = true
  }

  animateLotMovement(lot) {
    const mesh = this.lotMeshes.get(lot.id)
    if (!mesh) return

    const startPos = mesh.position.clone()
    const endPos = LOCATION_3D_POSITIONS[lot.targetLocation]
    if (!endPos) return

    const offset = new THREE.Vector3(
      (Math.random() - 0.5) * 2,
      1,
      (Math.random() - 0.5) * 2
    )
    const targetPos = endPos.clone().add(offset)

    const animation = {
      lotId: lot.id,
      startPos,
      endPos: targetPos,
      startTime: Date.now(),
      duration: 2000,
      onComplete: () => {
        this.lotAnimations.delete(lot.id)
        if (lot.targetLocation) {
          lot.currentLocation = lot.targetLocation
          lot.targetLocation = null
        }
      }
    }

    this.lotAnimations.set(lot.id, animation)
    this.needsUpdate = true
  }

  updateAnimations() {
    const now = Date.now()
    const completedAnimations = []

    this.lotAnimations.forEach((anim, lotId) => {
      const elapsed = now - anim.startTime
      const progress = Math.min(elapsed / anim.duration, 1)
      const eased = this.easeInOutCubic(progress)

      const mesh = this.lotMeshes.get(lotId)
      if (mesh) {
        mesh.position.lerpVectors(anim.startPos, anim.endPos, eased)
        mesh.rotation.y += 0.05

        const height = 2 + Math.sin(progress * Math.PI) * 0.5
        mesh.position.y = anim.startPos.y + (anim.endPos.y - anim.startPos.y) * eased + height * (1 - progress)
      }

      if (progress >= 1) {
        completedAnimations.push(lotId)
      }
    })

    completedAnimations.forEach(lotId => {
      const anim = this.lotAnimations.get(lotId)
      if (anim && anim.onComplete) {
        anim.onComplete()
      }
    })
  }

  easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2
  }

  highlightLot(lotId) {
    const mesh = this.lotMeshes.get(lotId)
    if (mesh) {
      const originalEmissive = mesh.material.emissiveIntensity
      mesh.material = mesh.material.clone()
      mesh.material.emissiveIntensity = 1.5
      setTimeout(() => {
        if (mesh.material) {
          mesh.material.emissiveIntensity = originalEmissive
        }
      }, 500)
      this.needsUpdate = true
    }
  }

  getMeshAtPosition(position) {
    const raycaster = new THREE.Raycaster()
    raycaster.setFromCamera(position, null)
    const intersects = raycaster.intersectObjects(Array.from(this.lotMeshes.values()))
    if (intersects.length > 0) {
      return intersects[0].object.userData.lotId
    }
    return null
  }

  removeLotMesh(lotId) {
    const mesh = this.lotMeshes.get(lotId)
    if (mesh) {
      this.scene.remove(mesh)
      mesh.geometry.dispose()
      this.lotMeshes.delete(lotId)
    }

    const trail = this.trailLines.get(lotId)
    if (trail) {
      this.scene.remove(trail)
      trail.geometry.dispose()
      this.trailLines.delete(lotId)
    }

    const animation = this.lotAnimations.get(lotId)
    if (animation) {
      this.lotAnimations.delete(lotId)
    }

    this.needsUpdate = true
  }

  updateFromStore(materialStore) {
    const storeLots = materialStore.lots
    const currentLotIds = new Set(storeLots.map(l => l.id))

    this.lotMeshes.forEach((mesh, lotId) => {
      if (!currentLotIds.has(lotId)) {
        this.removeLotMesh(lotId)
      }
    })

    storeLots.forEach(lot => {
      this.updateLotMesh(lot)
    })

    this.updateAnimations()
  }

  get3DPosition(lotId) {
    const mesh = this.lotMeshes.get(lotId)
    return mesh ? mesh.position.clone() : null
  }

  dispose() {
    this.lotMeshes.forEach((mesh, lotId) => {
      this.removeLotMesh(lotId)
    })

    Object.values(this.materials).forEach(material => {
      material.dispose()
    })

    this.materials = {}
    this.scene = null
  }
}

export default MaterialTracker