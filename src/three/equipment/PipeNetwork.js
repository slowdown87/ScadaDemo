import * as THREE from 'three'
import { COLORS, DIMENSIONS, SEGMENTS } from '../constants.js'
import { materials } from '../materials.js'

export function createPipeNetwork(scene) {
  const pipeGroup = new THREE.Group()
  const pipeResults = []

  const mainPipeMaterial = materials.metal(COLORS.equipment.pipe)
  const insulationMaterial = materials.roughMetal(0x8b7355, { roughness: 0.8, metalness: 0.2 })

  const mainPipe1 = createPipe(DIMENSIONS.pipe.mainRadius, 35, SEGMENTS.pipe, mainPipeMaterial)
  mainPipe1.position.set(-5, 10, 0)
  mainPipe1.rotation.z = Math.PI / 2
  pipeGroup.add(mainPipe1)
  pipeResults.push(mainPipe1)

  const insulation1 = createPipeInsulation(DIMENSIONS.pipe.mainRadius, 35, SEGMENTS.pipe, insulationMaterial)
  insulation1.position.set(-5, 10, 0)
  insulation1.rotation.z = Math.PI / 2
  pipeGroup.add(insulation1)

  const mainPipe2 = createPipe(DIMENSIONS.pipe.mainRadius, 20, SEGMENTS.pipe, mainPipeMaterial)
  mainPipe2.position.set(10, 10, -15)
  mainPipe2.rotation.x = Math.PI / 2
  pipeGroup.add(mainPipe2)
  pipeResults.push(mainPipe2)

  const insulation2 = createPipeInsulation(DIMENSIONS.pipe.mainRadius, 20, SEGMENTS.pipe, insulationMaterial)
  insulation2.position.set(10, 10, -15)
  insulation2.rotation.x = Math.PI / 2
  pipeGroup.add(insulation2)

  const branchPipe1 = createBranchPipe()
  pipeGroup.add(branchPipe1)
  pipeResults.push(branchPipe1)

  const verticalPipe1 = createPipe(DIMENSIONS.pipe.verticalRadius, 8, SEGMENTS.smallCylinder, mainPipeMaterial)
  verticalPipe1.position.set(-20, 4, -15)
  pipeGroup.add(verticalPipe1)

  const verticalPipe2 = createPipe(DIMENSIONS.pipe.verticalRadius, 8, SEGMENTS.smallCylinder, mainPipeMaterial)
  verticalPipe2.position.set(-5, 4, -15)
  pipeGroup.add(verticalPipe2)

  const elbow1 = createElbowWithFlanges(DIMENSIONS.pipe.mainRadius)
  elbow1.position.set(-20, 10, -15)
  pipeGroup.add(elbow1)

  const elbow2 = createElbowWithFlanges(DIMENSIONS.pipe.mainRadius)
  elbow2.position.set(-5, 10, -15)
  pipeGroup.add(elbow2)

  const valves = createValves()
  valves.forEach((valve, i) => {
    pipeGroup.add(valve.group)
    pipeResults.push(valve.group)
  })

  const flanges = createFlanges()
  flanges.forEach(flange => pipeGroup.add(flange))

  const supports = createPipeSupports()
  supports.forEach(support => pipeGroup.add(support))

  const instrumentImpulseLines = createInstrumentImpulseLines()
  instrumentImpulseLines.forEach(line => pipeGroup.add(line))

  scene.add(pipeGroup)

  return {
    group: pipeGroup,
    pipes: pipeResults,
    valves
  }
}

function createPipe(radius, height, radialSegments, material) {
  const geometry = new THREE.CylinderGeometry(radius, radius, height, radialSegments)
  const pipe = new THREE.Mesh(geometry, material)
  pipe.castShadow = true
  pipe.receiveShadow = true
  return pipe
}

function createPipeInsulation(radius, height, radialSegments, material) {
  const insulationThickness = 0.15
  const geometry = new THREE.CylinderGeometry(
    radius + insulationThickness,
    radius + insulationThickness,
    height,
    radialSegments
  )
  const insulation = new THREE.Mesh(geometry, material)
  insulation.castShadow = true
  return insulation
}

function createBranchPipe() {
  const branchGroup = new THREE.Group()
  const branchMaterial = materials.metal(COLORS.equipment.pipe)

  const branch1 = createPipe(DIMENSIONS.pipe.verticalRadius * 0.8, 15, SEGMENTS.smallCylinder, branchMaterial)
  branch1.position.set(-20, 17, -15)
  branchGroup.add(branch1)

  const elbow3d = createElbowWithFlanges(DIMENSIONS.pipe.verticalRadius * 0.8)
  elbow3d.position.set(-20, 24.5, -15)
  elbow3d.rotation.z = Math.PI
  branchGroup.add(elbow3d)

  const horizontalBranch = createPipe(DIMENSIONS.pipe.verticalRadius * 0.8, 10, SEGMENTS.smallCylinder, branchMaterial)
  horizontalBranch.position.set(-15, 24.5, -15)
  horizontalBranch.rotation.z = Math.PI / 2
  branchGroup.add(horizontalBranch)

  const teeFlange1 = createTeeFlange(DIMENSIONS.pipe.mainRadius, DIMENSIONS.pipe.verticalRadius * 0.8)
  teeFlange1.position.set(-20, 17, -15)
  branchGroup.add(teeFlange1)

  return branchGroup
}

function createElbowWithFlanges(radius) {
  const elbowGroup = new THREE.Group()
  const elbowMaterial = materials.steel(COLORS.equipment.pipe)
  const flangeMaterial = materials.steel(COLORS.industrial.steelDark)

  const curve = new THREE.QuadraticBezierCurve3(
    new THREE.Vector3(0, 0, 0),
    new THREE.Vector3(0, radius * 4, 0),
    new THREE.Vector3(0, radius * 4, radius * 4)
  )

  const tubeGeometry = new THREE.TubeGeometry(curve, SEGMENTS.smallSphere, radius, 16, false)
  const tube = new THREE.Mesh(tubeGeometry, elbowMaterial)
  tube.castShadow = true
  elbowGroup.add(tube)

  const flangeGeometry = new THREE.CylinderGeometry(
    radius * 1.8, radius * 1.8, radius * 0.3, SEGMENTS.smallSphere
  )

  const flange1 = new THREE.Mesh(flangeGeometry, flangeMaterial)
  flange1.position.set(0, -radius * 0.15, 0)
  flange1.rotation.x = Math.PI / 2
  flange1.castShadow = true
  elbowGroup.add(flange1)

  const flange2 = new THREE.Mesh(flangeGeometry, flangeMaterial)
  flange2.position.set(0, radius * 4 + radius * 0.15, radius * 4)
  flange2.rotation.x = Math.PI / 2
  flange2.castShadow = true
  elbowGroup.add(flange2)

  const boltCount = 6
  const boltGeometry = new THREE.CylinderGeometry(radius * 0.1, radius * 0.1, radius * 0.2, SEGMENTS.bolt)
  const boltMaterial = materials.metal(COLORS.industrial.black)

  for (let i = 0; i < boltCount; i++) {
    const angle = (i / boltCount) * Math.PI * 2
    const bolt1 = new THREE.Mesh(boltGeometry, boltMaterial)
    bolt1.position.set(
      Math.cos(angle) * radius * 1.4,
      -radius * 0.15,
      Math.sin(angle) * radius * 1.4
    )
    bolt1.castShadow = true
    elbowGroup.add(bolt1)
  }

  return elbowGroup
}

function createTeeFlange(mainRadius, branchRadius) {
  const teeGroup = new THREE.Group()
  const teeMaterial = materials.steel(COLORS.industrial.steelDark)

  const teeGeometry = new THREE.CylinderGeometry(
    mainRadius * 1.5, mainRadius * 1.5, branchRadius * 2, SEGMENTS.smallSphere
  )
  const tee = new THREE.Mesh(teeGeometry, teeMaterial)
  tee.rotation.x = Math.PI / 2
  tee.castShadow = true
  teeGroup.add(tee)

  const reinforcementGeometry = new THREE.TorusGeometry(mainRadius * 1.3, mainRadius * 0.2, 8, SEGMENTS.smallSphere)
  const reinforcement = new THREE.Mesh(reinforcementGeometry, teeMaterial)
  reinforcement.position.y = branchRadius
  reinforcement.rotation.x = Math.PI / 2
  reinforcement.castShadow = true
  teeGroup.add(reinforcement)

  return teeGroup
}

function createValves() {
  const valves = []
  const valveBodyMaterial = materials.metal(COLORS.equipment.valve)
  const valveWheelMaterial = materials.plastic(COLORS.equipment.valveWheel)
  const flangeMaterial = materials.steel(COLORS.industrial.steelDark)

  const valvePositions = [
    { x: -15, y: 10, z: -15 },
    { x: -10, y: 10, z: -15 },
    { x: 5, y: 10, z: -7.5 },
    { x: -12.5, y: 6, z: -15 }
  ]

  valvePositions.forEach((pos, index) => {
    const valveGroup = new THREE.Group()
    valveGroup.position.set(pos.x, pos.y, pos.z)

    const flangeGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.valve.bodyRadius * 1.5,
      DIMENSIONS.valve.bodyRadius * 1.5,
      DIMENSIONS.pipe.flangeThickness,
      SEGMENTS.smallSphere
    )
    const flange = new THREE.Mesh(flangeGeometry, flangeMaterial)
    flange.position.y = -DIMENSIONS.valve.bodyHeight / 2 - 0.1
    flange.rotation.x = Math.PI / 2
    flange.castShadow = true
    valveGroup.add(flange)

    const bodyGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.valve.bodyRadius,
      DIMENSIONS.valve.bodyRadius,
      DIMENSIONS.valve.bodyHeight,
      SEGMENTS.smallSphere
    )
    const body = new THREE.Mesh(bodyGeometry, valveBodyMaterial)
    body.castShadow = true
    body.receiveShadow = true
    valveGroup.add(body)

    const bonnetGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.valve.bodyRadius * 0.8,
      DIMENSIONS.valve.bodyRadius * 0.8,
      DIMENSIONS.valve.bodyHeight * 0.3,
      SEGMENTS.smallSphere
    )
    const bonnet = new THREE.Mesh(bonnetGeometry, valveBodyMaterial)
    bonnet.position.y = DIMENSIONS.valve.bodyHeight * 0.65
    bonnet.castShadow = true
    valveGroup.add(bonnet)

    const stemGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.valve.stemRadius,
      DIMENSIONS.valve.stemRadius,
      DIMENSIONS.valve.stemHeight,
      SEGMENTS.rod
    )
    const stem = new THREE.Mesh(stemGeometry, valveWheelMaterial)
    stem.position.y = DIMENSIONS.valve.bodyHeight * 0.8
    stem.castShadow = true
    valveGroup.add(stem)

    const handwheelGeometry = new THREE.TorusGeometry(
      DIMENSIONS.valve.wheelRadius,
      DIMENSIONS.valve.wheelTube,
      SEGMENTS.bolt,
      SEGMENTS.smallSphere
    )
    const handwheel = new THREE.Mesh(handwheelGeometry, valveWheelMaterial)
    handwheel.position.y = DIMENSIONS.valve.bodyHeight * 0.8 + DIMENSIONS.valve.stemHeight * 0.5
    handwheel.rotation.x = Math.PI / 2
    handwheel.castShadow = true
    valveGroup.add(handwheel)

    const indicatorGeometry = new THREE.BoxGeometry(
      DIMENSIONS.valve.wheelRadius * 0.8,
      0.05,
      DIMENSIONS.valve.wheelRadius * 0.1
    )
    const indicatorMaterial = materials.emissive(COLORS.indicators.running, 0.8)
    const indicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial)
    indicator.position.y = DIMENSIONS.valve.bodyHeight * 0.8 + DIMENSIONS.valve.stemHeight * 0.5
    indicator.rotation.x = Math.PI / 2
    valveGroup.add(indicator)

    valves.push({ group: valveGroup, index })
  })

  return valves
}

function createFlanges() {
  const flanges = []
  const flangeMaterial = materials.steel(COLORS.industrial.steelDark)

  const flangeConfigs = [
    { pos: [-20.5, 10, -15], rot: 'z', radius: DIMENSIONS.pipe.mainRadius },
    { pos: [-5.5, 10, -15], rot: 'z', radius: DIMENSIONS.pipe.mainRadius },
    { pos: [10.5, 10, -15], rot: 'z', radius: DIMENSIONS.pipe.mainRadius },
    { pos: [-20, 6, -15], rot: 'z', radius: DIMENSIONS.pipe.verticalRadius },
    { pos: [-5, 6, -15], rot: 'z', radius: DIMENSIONS.pipe.verticalRadius }
  ]

  flangeConfigs.forEach(config => {
    const flangeGroup = new THREE.Group()

    const flangeGeometry = new THREE.CylinderGeometry(
      config.radius * 1.8,
      config.radius * 1.8,
      DIMENSIONS.pipe.flangeThickness,
      SEGMENTS.smallSphere
    )
    const flange = new THREE.Mesh(flangeGeometry, flangeMaterial)
    flange.castShadow = true
    flangeGroup.add(flange)

    const boltCount = 6
    const boltGeometry = new THREE.CylinderGeometry(config.radius * 0.12, config.radius * 0.12, DIMENSIONS.pipe.flangeThickness * 1.5, SEGMENTS.bolt)
    const boltMaterial = materials.metal(COLORS.industrial.black)

    for (let i = 0; i < boltCount; i++) {
      const angle = (i / boltCount) * Math.PI * 2
      const bolt = new THREE.Mesh(boltGeometry, boltMaterial)
      bolt.position.set(
        Math.cos(angle) * config.radius * 1.4,
        0,
        Math.sin(angle) * config.radius * 1.4
      )
      bolt.castShadow = true
      flangeGroup.add(bolt)
    }

    flangeGroup.position.set(...config.pos)
    if (config.rot === 'z') {
      flangeGroup.rotation.z = Math.PI / 2
    }

    flanges.push(flangeGroup)
  })

  return flanges
}

function createPipeSupports() {
  const supports = []
  const bracketMaterial = materials.metal(COLORS.industrial.steelLight)
  const clampMaterial = materials.steel(COLORS.industrial.steelDark)

  const supportPositions = [
    { x: -15, y: 8, z: -15 },
    { x: 0, y: 8, z: -15 },
    { x: 5, y: 8, z: -15 },
    { x: -15, y: 3, z: -15 },
    { x: -5, y: 3, z: -15 }
  ]

  supportPositions.forEach((pos, index) => {
    const supportGroup = new THREE.Group()

    const clampGeometry = new THREE.CylinderGeometry(
      DIMENSIONS.pipe.mainRadius * 1.2,
      DIMENSIONS.pipe.mainRadius * 1.2,
      0.2,
      SEGMENTS.smallSphere
    )
    const clamp = new THREE.Mesh(clampGeometry, clampMaterial)
    clamp.rotation.x = Math.PI / 2
    clamp.castShadow = true
    supportGroup.add(clamp)

    const bracketGeometry = new THREE.BoxGeometry(0.3, 0.3, 2)
    const bracket1 = new THREE.Mesh(bracketGeometry, bracketMaterial)
    bracket1.position.set(0, 0, DIMENSIONS.pipe.mainRadius * 1.5)
    bracket1.castShadow = true
    supportGroup.add(bracket1)

    const bracket2 = new THREE.Mesh(bracketGeometry, bracketMaterial)
    bracket2.position.set(0, 0, -DIMENSIONS.pipe.mainRadius * 1.5)
    bracket2.castShadow = true
    supportGroup.add(bracket2)

    const verticalBarGeometry = new THREE.BoxGeometry(0.15, pos.y * 2, 0.15)
    const verticalBar = new THREE.Mesh(verticalBarGeometry, bracketMaterial)
    verticalBar.position.set(0, -pos.y, 0)
    verticalBar.castShadow = true
    supportGroup.add(verticalBar)

    supportGroup.position.set(pos.x, pos.y, pos.z)
    supports.push(supportGroup)
  })

  return supports
}

function createInstrumentImpulseLines() {
  const lines = []
  const capillaryMaterial = materials.steel(COLORS.industrial.steelDark)
  const instrumentFlangeMaterial = materials.metal(COLORS.industrial.gray)

  const impulseLineConfigs = [
    { x: 5.5, y: 15, z: 0, angle: Math.PI / 4 },
    { x: 6, y: 12, z: 0, angle: Math.PI / 3 }
  ]

  impulseLineConfigs.forEach((config, index) => {
    const lineGroup = new THREE.Group()

    const capillaryGeometry = new THREE.CylinderGeometry(0.05, 0.05, 3, SEGMENTS.rod)
    const capillary = new THREE.Mesh(capillaryGeometry, capillaryMaterial)
    capillary.position.y = 1.5
    capillary.rotation.z = config.angle
    capillary.castShadow = true
    lineGroup.add(capillary)

    const instrumentFlangeGeometry = new THREE.CylinderGeometry(0.2, 0.2, 0.1, SEGMENTS.smallSphere)
    const instrumentFlange = new THREE.Mesh(instrumentFlangeGeometry, instrumentFlangeMaterial)
    instrumentFlange.position.set(Math.cos(config.angle) * 1.5, 3, 0)
    instrumentFlange.castShadow = true
    lineGroup.add(instrumentFlange)

    const capillaryCoilGeometry = new THREE.TorusGeometry(0.3, 0.03, 8, 12)
    const capillaryCoil = new THREE.Mesh(capillaryCoilGeometry, capillaryMaterial)
    capillaryCoil.position.set(Math.cos(config.angle) * 0.8, 2.5, 0)
    capillaryCoil.rotation.y = Math.PI / 2
    capillaryCoil.rotation.z = config.angle
    lineGroup.add(capillaryCoil)

    lineGroup.position.set(config.x, config.y, config.z)
    lines.push(lineGroup)
  })

  return lines
}

export function createLowDetailPipeNetwork(scene) {
  const pipeGroup = new THREE.Group()
  const pipeMaterial = materials.metal(COLORS.equipment.pipe)

  const mainPipe1 = createPipe(DIMENSIONS.pipe.mainRadius, 35, SEGMENTS.coarse, pipeMaterial)
  mainPipe1.position.set(-5, 10, 0)
  mainPipe1.rotation.z = Math.PI / 2
  pipeGroup.add(mainPipe1)

  const mainPipe2 = createPipe(DIMENSIONS.pipe.mainRadius, 20, SEGMENTS.coarse, pipeMaterial)
  mainPipe2.position.set(10, 10, -15)
  mainPipe2.rotation.x = Math.PI / 2
  pipeGroup.add(mainPipe2)

  scene.add(pipeGroup)
  return pipeGroup
}
