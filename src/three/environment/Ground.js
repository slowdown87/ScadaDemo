import * as THREE from 'three'
import { COLORS, DIMENSIONS } from '../constants.js'
import { materials } from '../materials.js'

export function createGround(scene) {
  const groundGroup = new THREE.Group()

  const groundGeometry = new THREE.PlaneGeometry(
    DIMENSIONS.scene.groundSize,
    DIMENSIONS.scene.groundSize
  )
  const groundMaterial = materials.ground()
  const ground = new THREE.Mesh(groundGeometry, groundMaterial)
  ground.rotation.x = -Math.PI / 2
  ground.position.y = -0.05
  ground.receiveShadow = true
  groundGroup.add(ground)

  const gridHelper = new THREE.GridHelper(
    DIMENSIONS.scene.gridSize,
    DIMENSIONS.scene.gridSize,
    COLORS.industrial.gridMain,
    COLORS.industrial.gridSub
  )
  gridHelper.position.y = 0.01
  groundGroup.add(gridHelper)

  const floorMarkings = createFloorMarkings()
  floorMarkings.forEach(marking => groundGroup.add(marking))

  scene.add(groundGroup)
  return groundGroup
}

function createFloorMarkings() {
  const markings = []

  const yellowMaterial = materials.emissive(COLORS.safety.yellow, 0.1)
  const whiteMaterial = materials.metal(COLORS.safety.white, { roughness: 0.6, metalness: 0.2 })

  for (let z = -40; z <= 40; z += 10) {
    const lineGeometry = new THREE.BoxGeometry(100, 0.02, 0.15)
    const line = new THREE.Mesh(lineGeometry, whiteMaterial)
    line.position.set(0, 0.01, z)
    markings.push(line)
  }

  for (let i = -45; i < 45; i += 2) {
    const stripeGeometry = new THREE.BoxGeometry(0.3, 0.02, 0.3)
    const stripe = new THREE.Mesh(stripeGeometry, yellowMaterial)
    stripe.position.set(i, 0.01, 20)
    markings.push(stripe)
  }

  const tankZones = [
    { x: -20, z: -15, radius: 8 },
    { x: -7, z: -15, radius: 6 },
    { x: 10, z: -15, radius: 7 }
  ]

  tankZones.forEach(zone => {
    const circleGeometry = new THREE.RingGeometry(zone.radius, zone.radius + 0.2, 64)
    const circle = new THREE.Mesh(circleGeometry, yellowMaterial)
    circle.rotation.x = -Math.PI / 2
    circle.position.set(zone.x, 0.02, zone.z)
    markings.push(circle)
  })

  const walkwayGeometry = new THREE.BoxGeometry(3, 0.02, 60)
  const walkway1 = new THREE.Mesh(walkwayGeometry, whiteMaterial)
  walkway1.position.set(25, 0.02, 0)
  markings.push(walkway1)

  const walkway2 = walkway1.clone()
  walkway2.position.set(-25, 0.02, 0)
  markings.push(walkway2)

  const arrowGeometry = new THREE.BoxGeometry(0.5, 0.02, 2)
  for (let z = -25; z <= 25; z += 10) {
    const arrow = new THREE.Mesh(arrowGeometry, yellowMaterial)
    arrow.position.set(25, 0.02, z)
    markings.push(arrow)

    const arrow2 = new THREE.Mesh(arrowGeometry, yellowMaterial)
    arrow2.position.set(-25, 0.02, z)
    markings.push(arrow2)
  }

  return markings
}

export function createScene(scene) {
  scene.background = new THREE.Color(COLORS.industrial.fogColor || 0x8090a0)
  scene.fog = new THREE.FogExp2(0x8090a0, DIMENSIONS.scene.fogDensity)
}
