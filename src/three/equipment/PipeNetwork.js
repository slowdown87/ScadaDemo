import * as THREE from 'three'
import { COLORS, DIMENSIONS, SEGMENTS } from '../constants.js'
import { materials } from '../materials.js'

export function createPipeNetwork(scene) {
  const pipeGroup = new THREE.Group()

  const pipeMaterial = materials.metal(COLORS.equipment.pipe)
  const pipeResults = []

  const mainPipe1 = createPipe(DIMENSIONS.pipe.mainRadius, 35, SEGMENTS.pipe)
  mainPipe1.position.set(-5, 10, 0)
  mainPipe1.rotation.z = Math.PI / 2
  pipeGroup.add(mainPipe1)
  pipeResults.push(mainPipe1)

  const mainPipe2 = createPipe(DIMENSIONS.pipe.mainRadius, 20, SEGMENTS.pipe)
  mainPipe2.position.set(10, 10, -15)
  mainPipe2.rotation.x = Math.PI / 2
  pipeGroup.add(mainPipe2)

  const verticalPipe1 = createPipe(DIMENSIONS.pipe.verticalRadius, 8, SEGMENTS.smallCylinder)
  verticalPipe1.position.set(-20, 4, -15)
  pipeGroup.add(verticalPipe1)

  const verticalPipe2 = createPipe(DIMENSIONS.pipe.verticalRadius, 8, SEGMENTS.smallCylinder)
  verticalPipe2.position.set(-5, 4, -15)
  pipeGroup.add(verticalPipe2)

  const elbow1 = createElbow(DIMENSIONS.pipe.mainRadius)
  elbow1.position.set(-20, 10, -15)
  pipeGroup.add(elbow1)

  const elbow2 = createElbow(DIMENSIONS.pipe.mainRadius)
  elbow2.position.set(-5, 10, -15)
  pipeGroup.add(elbow2)

  const valves = createValves()
  valves.forEach((valve, i) => {
    pipeGroup.add(valve.group)
    pipeResults.push(valve.group)
  })

  const flanges = createFlanges()
  flanges.forEach(flange => pipeGroup.add(flange))

  scene.add(pipeGroup)

  return {
    group: pipeGroup,
    pipes: pipeResults,
    valves
  }
}

function createPipe(radius, height, radialSegments = SEGMENTS.pipe) {
  const geometry = new THREE.CylinderGeometry(radius, radius, height, radialSegments)
  const material = materials.metal(COLORS.equipment.pipe)
  const pipe = new THREE.Mesh(geometry, material)
  pipe.castShadow = true
  return pipe
}

function createElbow(radius) {
  const elbowGroup = new THREE.Group()
  const curve = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, 5, 0),
    new THREE.Vector3(0, 5, 5)
  )

  const tubeGeometry = new THREE.TubeGeometry(curve, SEGMENTS.smallSphere, radius, 16, false)
  const tubeMaterial = materials.steel(COLORS.equipment.pipe)
  const tube = new THREE.Mesh(tubeGeometry, tubeMaterial)
  tube.castShadow = true
  elbowGroup.add(tube)

  return elbowGroup
}

function createValves() {
  const valves = []
  const valveBodyMaterial = materials.metal(COLORS.equipment.valve)
  const valveWheelMaterial = materials.plastic(COLORS.equipment.valveWheel)

  const valvePositions = [
    { x: -15, y: 10, z: -15 },
    { x: -10, y: 10, z: -15 },
    { x: 5, y: 10, z: -7.5 },
    { x: -12.5, y: 6, z: -15 }
  ]

  valvePositions.forEach((pos, index) => {
    const valveGroup = new THREE.Group()
    valveGroup.position.set(pos.x, pos.y, pos.z)

    const bodyGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.valve.bodyRadius,
      DIMENSIONS.valve.bodyRadius,
      DIMENSIONS.valve.bodyHeight,
      SEGMENTS.smallSphere
    )
    const body = new THREE.Mesh(bodyGeometry, valveBodyMaterial)
    body.castShadow = true
    valveGroup.add(body)

    const handwheelGeometry = new THREE.TorusGeometry(
      DIMENSIONS.valve.wheelRadius,
      DIMENSIONS.valve.wheelTube,
      SEGMENTS.bolt,
      SEGMENTS.smallSphere
    )
    const handwheel = new THREE.Mesh(handwheelGeometry, valveWheelMaterial)
    handwheel.position.y = 1
    handwheel.rotation.x = Math.PI / 2
    valveGroup.add(handwheel)

    const stemGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.valve.stemRadius,
      DIMENSIONS.valve.stemRadius,
      DIMENSIONS.valve.stemHeight,
      SEGMENTS.rod
    )
    const stem = new THREE.Mesh(stemGeometry, valveWheelMaterial)
    stem.position.y = 0.6
    valveGroup.add(stem)

    valves.push({ group: valveGroup, index })
  })

  return valves
}

function createFlanges() {
  const flanges = []
  const flangeMaterial = materials.metal(COLORS.industrial.steelDark)

  const flangeGeometry = new THREE.CylinderGeometry(
    DIMENSIONS.pipe.flangeRadius,
    DIMENSIONS.pipe.flangeRadius,
    DIMENSIONS.pipe.flangeThickness,
    SEGMENTS.smallSphere
  )

  const positions = [
    [-20.5, 10, -15], [-5.5, 10, -15], [10.5, 10, -15],
    [-20, 6, -15], [-5, 6, -15]
  ]

  positions.forEach(pos => {
    const flange = new THREE.Mesh(flangeGeometry, flangeMaterial)
    flange.position.set(...pos)
    flange.rotation.z = Math.PI / 2
    flanges.push(flange)
  })

  return flanges
}
