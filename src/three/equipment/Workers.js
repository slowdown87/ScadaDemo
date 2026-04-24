import * as THREE from 'three'
import { COLORS, DIMENSIONS } from '../constants.js'
import { materials } from '../materials.js'

export function createWorkers(scene) {
  const workersGroup = new THREE.Group()
  const workers = []

  const bodyMaterial = materials.roughMetal(COLORS.worker.body, { roughness: 0.7, metalness: 0.3 })
  const headMaterial = materials.roughMetal(COLORS.worker.head, { roughness: 0.8, metalness: 0.1 })
  const helmetMaterial = materials.emissive(COLORS.worker.helmet, 0.2)

  const workerCount = 3

  for (let i = 0; i < workerCount; i++) {
    const workerGroup = new THREE.Group()

    const bodyGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.worker.bodyRadius,
      DIMENSIONS.worker.bodyRadius,
      DIMENSIONS.worker.bodyHeight,
      16
    )
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
    body.position.y = 0.9
    workerGroup.add(body)

    const headGeometry = new THREE.SphereGeometry(
      DIMENSIONS.worker.headRadius,
      16,
      16
    )
    const head = new THREE.Mesh(headGeometry, headMaterial)
    head.position.y = 1.7
    workerGroup.add(head)

    const helmetGeometry = new THREE.SphereGeometry(
      DIMENSIONS.worker.helmetRadius,
      16,
      8,
      0,
      Math.PI * 2,
      0,
      Math.PI / 2
    )
    const helmet = new THREE.Mesh(helmetGeometry, helmetMaterial)
    helmet.position.y = 1.85
    workerGroup.add(helmet)

    const legGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.worker.legRadius,
      DIMENSIONS.worker.legRadius,
      DIMENSIONS.worker.legHeight,
      12
    )
    const leg1 = new THREE.Mesh(legGeometry, bodyMaterial)
    leg1.position.set(0.15, 0.3, 0)
    workerGroup.add(leg1)

    const leg2 = new THREE.Mesh(legGeometry, bodyMaterial)
    leg2.position.set(-0.15, 0.3, 0)
    workerGroup.add(leg2)

    workersGroup.add(workerGroup)
    workers.push(workerGroup)
  }

  scene.add(workersGroup)

  return {
    group: workersGroup,
    workers
  }
}
