import * as THREE from 'three'
import { COLORS, DIMENSIONS, SEGMENTS } from '../constants.js'
import { materials } from '../materials.js'

export function createTanks(scene) {
  const tankGroup = new THREE.Group()
  const tankResults = []

  const tankConfigs = [
    { x: -25, label: 'TK-101', capacity: 100 },
    { x: -10, label: 'TK-102', capacity: 80 },
    { x: 12, label: 'TK-103', capacity: 120 }
  ]

  tankConfigs.forEach((config, index) => {
    const tank = createSingleTank(config.capacity, config.label)
    tank.position.set(config.x, 0, -15)
    tankGroup.add(tank)
    tankResults.push(tank)
  })

  scene.add(tankGroup)

  return {
    group: tankGroup,
    tanks: tankResults
  }
}

export function createSingleTank(capacity, label) {
  const tankGroup = new THREE.Group()
  tankGroup.userData.deviceId = label

  const height = DIMENSIONS.tank.defaultHeight + capacity / 30
  const radius = DIMENSIONS.tank.defaultRadius
  const bodyMaterial = materials.metal(COLORS.equipment.tank)

  const body = createTankBody(radius, height, bodyMaterial)
  tankGroup.add(body)

  const roof = createTankRoof(radius, height, bodyMaterial)
  tankGroup.add(roof)

  const bottom = createTankBottom(radius, height, bodyMaterial)
  tankGroup.add(bottom)

  const legs = createTankLegs(radius, height, bodyMaterial)
  tankGroup.add(legs)

  const level = createLevelIndicator(radius, height)
  tankGroup.add(level)

  const nozzles = createNozzles(radius, height)
  tankGroup.add(nozzles)

  const supportRings = createSupportRings(radius, height, bodyMaterial)
  tankGroup.add(supportRings)

  const ladder = createLadder(radius, height)
  tankGroup.add(ladder)

  const platform = createTankPlatform(radius, height)
  tankGroup.add(platform)

  const railings = createRailings(radius, height)
  railings.forEach(r => tankGroup.add(r))

  const nameplate = createTankNameplate(radius, height)
  nameplate.rotation.y = Math.PI / 2
  tankGroup.add(nameplate)

  return tankGroup
}

function createTankBody(radius, height, material) {
  const bodyGroup = new THREE.Group()

  const segments = SEGMENTS.cylinder
  const geometry = new THREE.CylinderGeometry(radius, radius, height, segments)
  const body = new THREE.Mesh(geometry, material)
  body.position.y = height / 2 + 2
  body.castShadow = true
  body.receiveShadow = true
  bodyGroup.add(body)

  const ribGeometry = new THREE.TorusGeometry(radius + 0.05, 0.08, 8, segments)
  const ribMaterial = materials.steel(COLORS.industrial.steelDark)
  const ribPositions = [0.25, 0.5, 0.75]
  ribPositions.forEach(ratio => {
    const rib = new THREE.Mesh(ribGeometry, ribMaterial)
    rib.position.y = height * ratio + 2
    rib.rotation.x = Math.PI / 2
    rib.castShadow = true
    bodyGroup.add(rib)
  })

  return bodyGroup
}

function createTankRoof(radius, height, material) {
  const roofGroup = new THREE.Group()

  const topDomeGeometry = new THREE.SphereGeometry(
    radius, SEGMENTS.cylinder, SEGMENTS.cylinder / 2, 0, Math.PI * 2, 0, Math.PI / 6
  )
  const topDome = new THREE.Mesh(topDomeGeometry, material)
  topDome.position.y = height + 2
  topDome.castShadow = true
  roofGroup.add(topDome)

  const rimGeometry = new THREE.TorusGeometry(
    DIMENSIONS.reactor.rimRadius, DIMENSIONS.reactor.rimTube, SEGMENTS.bolt, SEGMENTS.smallSphere
  )
  const rim = new THREE.Mesh(rimGeometry, materials.steel(COLORS.industrial.steelDark))
  rim.position.y = height + 2 + DIMENSIONS.reactor.topDomeRadius * 0.15
  rim.rotation.x = Math.PI / 2
  rim.castShadow = true
  roofGroup.add(rim)

  return roofGroup
}

function createTankBottom(radius, height, material) {
  const bottomGroup = new THREE.Group()

  const coneHeight = 2
  const coneGeometry = new THREE.CylinderGeometry(
    1, radius, coneHeight, SEGMENTS.fine
  )
  const cone = new THREE.Mesh(coneGeometry, material)
  cone.position.y = 1
  cone.castShadow = true
  cone.receiveShadow = true
  bottomGroup.add(cone)

  const legRingGeometry = new THREE.TorusGeometry(radius * 0.6, 0.15, 8, SEGMENTS.fine)
  const legRingMaterial = materials.steel(COLORS.industrial.steelDark)
  const legRing = new THREE.Mesh(legRingGeometry, legRingMaterial)
  legRing.position.y = coneHeight * 0.6
  legRing.rotation.x = Math.PI / 2
  legRing.castShadow = true
  bottomGroup.add(legRing)

  return bottomGroup
}

function createTankLegs(radius, height, material) {
  const legsGroup = new THREE.Group()
  const legCount = 4
  const legRadius = 0.2
  const legHeight = height * 0.4
  const legSpread = radius * 0.6

  for (let i = 0; i < legCount; i++) {
    const angle = (i / legCount) * Math.PI * 2 + Math.PI / 4
    const legGeometry = new THREE.CylinderGeometry(legRadius, legRadius * 1.2, legHeight, SEGMENTS.rod)
    const leg = new THREE.Mesh(legGeometry, material)
    leg.position.set(
      Math.cos(angle) * legSpread,
      legHeight / 2,
      Math.sin(angle) * legSpread
    )
    leg.castShadow = true
    legsGroup.add(leg)

    const footGeometry = new THREE.BoxGeometry(legRadius * 4, 0.15, legRadius * 4)
    const foot = new THREE.Mesh(footGeometry, materials.steel(COLORS.industrial.steelDark))
    foot.position.set(
      Math.cos(angle) * (legSpread + 0.2),
      0.075,
      Math.sin(angle) * (legSpread + 0.2)
    )
    foot.castShadow = true
    legsGroup.add(foot)

    const braceAngle = angle + Math.PI / legCount
    const braceLength = legSpread * 1.2
    const braceGeometry = new THREE.CylinderGeometry(0.06, 0.06, braceLength, SEGMENTS.rod)
    const brace = new THREE.Mesh(braceGeometry, materials.steel(COLORS.industrial.steelDark))
    brace.position.set(
      Math.cos(braceAngle) * legSpread * 0.5,
      legHeight * 0.5,
      Math.sin(braceAngle) * legSpread * 0.5
    )
    brace.rotation.z = Math.PI / 2
    brace.lookAt(
      Math.cos(braceAngle + Math.PI) * legSpread * 0.5,
      legHeight * 0.5,
      Math.sin(braceAngle + Math.PI) * legSpread * 0.5
    )
    brace.rotation.z = Math.PI / 2
    brace.castShadow = true
    legsGroup.add(brace)
  }

  return legsGroup
}

function createLevelIndicator(radius, height, options = {}) {
  const levelGroup = new THREE.Group()
  const levelRadius = radius - DIMENSIONS.tank.levelRadiusExtra

  const sightGlassGeometry = new THREE.CylinderGeometry(0.08, 0.08, height * 0.6, SEGMENTS.rod)
  const sightGlassMaterial = materials.glass(COLORS.indicators.liquid, { opacity: 0.5 })
  const sightGlass = new THREE.Mesh(sightGlassGeometry, sightGlassMaterial)
  sightGlass.position.set(radius + 0.5, height * 0.5 + 2, 0)
  levelGroup.add(sightGlass)

  const frameGeometry = new THREE.BoxGeometry(0.15, height * 0.6 + 0.2, 0.15)
  const frameMaterial = materials.metal(COLORS.industrial.steelDark)
  const frame = new THREE.Mesh(frameGeometry, frameMaterial)
  frame.position.set(radius + 0.5, height * 0.5 + 2, 0)
  levelGroup.add(frame)

  const scaleGeometry = new THREE.BoxGeometry(0.3, height * 0.6, 0.02)
  const scaleMaterial = materials.emissive(COLORS.safety.yellow, 0.3)
  const scale = new THREE.Mesh(scaleGeometry, scaleMaterial)
  scale.position.set(radius + 0.65, height * 0.5 + 2, 0)
  levelGroup.add(scale)

  return levelGroup
}

function createNozzles(radius, height) {
  const nozzlesGroup = new THREE.Group()
  const nozzleConfigs = [
    { y: height * 0.8 + 2, angle: 0, type: 'inlet' },
    { y: height * 0.3 + 2, angle: Math.PI * 0.5, type: 'outlet' },
    { y: height * 0.5 + 2, angle: Math.PI, type: 'sample' }
  ]

  nozzleConfigs.forEach(config => {
    const nozzleGroup = new THREE.Group()

    const flangeGeometry = new THREE.CylinderGeometry(0.4, 0.4, 0.2, SEGMENTS.smallSphere)
    const flangeMaterial = materials.metal(COLORS.industrial.steelDark)
    const flange = new THREE.Mesh(flangeGeometry, flangeMaterial)
    flange.rotation.z = Math.PI / 2
    flange.castShadow = true
    nozzleGroup.add(flange)

    const pipeGeometry = new THREE.CylinderGeometry(0.25, 0.25, 1.5, SEGMENTS.rod)
    const pipeMaterial = materials.metal(COLORS.equipment.pipe)
    const pipe = new THREE.Mesh(pipeGeometry, pipeMaterial)
    pipe.rotation.z = Math.PI / 2
    pipe.position.x = 0.85
    pipe.castShadow = true
    nozzleGroup.add(pipe)

    nozzleGroup.position.set(
      Math.cos(config.angle) * radius,
      config.y,
      Math.sin(config.angle) * radius
    )
    nozzleGroup.rotation.y = -config.angle

    nozzlesGroup.add(nozzleGroup)
  })

  return nozzlesGroup
}

function createSupportRings(radius, height, material) {
  const ringsGroup = new THREE.Group()
  const ringCount = 3
  const ringGeometry = new THREE.TorusGeometry(radius + 0.1, 0.12, 8, SEGMENTS.fine)
  const ringMaterial = materials.steel(COLORS.industrial.steelDark)

  for (let i = 0; i < ringCount; i++) {
    const ring = new THREE.Mesh(ringGeometry, ringMaterial)
    ring.position.y = (i + 1) * (height / (ringCount + 1)) + 2
    ring.rotation.x = Math.PI / 2
    ring.castShadow = true
    ringsGroup.add(ring)
  }

  return ringsGroup
}

function createLadder(radius, height) {
  const ladderGroup = new THREE.Group()
  const { ladderRailWidth, ladderRailGap } = DIMENSIONS.tank
  const railsMaterial = materials.metal(COLORS.industrial.steelLight, { roughness: 0.2, metalness: 0.9 })

  const railsGeometry = new THREE.BoxGeometry(ladderRailWidth, height * 0.7, ladderRailWidth)
  const rail1 = new THREE.Mesh(railsGeometry, railsMaterial)
  rail1.position.set(radius + ladderRailGap, height * 0.35 + 2, 0)
  ladderGroup.add(rail1)

  const rail2 = new THREE.Mesh(railsGeometry, railsMaterial)
  rail2.position.set(radius + ladderRailGap * 2, height * 0.35 + 2, 0)
  ladderGroup.add(rail2)

  const rungGeometry = new THREE.BoxGeometry(0.35, 0.06, 0.06)
  const rungCount = 8
  for (let i = 0; i < rungCount; i++) {
    const rung = new THREE.Mesh(rungGeometry, railsMaterial)
    rung.position.set(radius + ladderRailGap + 0.175, 3 + i * (height * 0.7 - 3) / (rungCount - 1), 0)
    ladderGroup.add(rung)
  }

  return ladderGroup
}

function createTankPlatform(radius, height) {
  const { platformWidth, platformDepth } = DIMENSIONS.tank
  const platformMaterial = materials.metal(COLORS.industrial.steelLight, { roughness: 0.3, metalness: 0.85 })

  const platformGeometry = new THREE.BoxGeometry(platformWidth, 0.15, platformDepth)
  const platform = new THREE.Mesh(platformGeometry, platformMaterial)
  platform.position.set(radius + 1, height + 3, 0)
  platform.castShadow = true
  platform.receiveShadow = true
  return platform
}

function createRailings(radius, height) {
  const railings = []
  const { railingHeight } = DIMENSIONS.tank
  const railingMaterial = materials.emissive(COLORS.safety.yellow, 0.1)
  const railingGeometry = new THREE.BoxGeometry(0.04, railingHeight, 0.04)

  const positions = [
    [radius + 0.5, height + 3.5, -0.9],
    [radius + 0.5, height + 3.5, 0.9],
    [radius + 1.9, height + 3.5, 0]
  ]

  positions.forEach(pos => {
    const railing = new THREE.Mesh(railingGeometry, railingMaterial)
    railing.position.set(...pos)
    railing.castShadow = true
    railings.push(railing)
  })

  return railings
}

function createTankNameplate(radius, height) {
  const { nameplateWidth, nameplateHeight } = DIMENSIONS.tank
  const group = new THREE.Group()

  const plateMaterial = materials.emissive(COLORS.safety.yellow, 0.1)
  const plateGeometry = new THREE.BoxGeometry(nameplateWidth, nameplateHeight, 0.1)
  const plate = new THREE.Mesh(plateGeometry, plateMaterial)
  plate.position.set(radius + 0.1, height * 0.6 + 2, 0)
  group.add(plate)

  const borderGeometry = new THREE.BoxGeometry(nameplateWidth + 0.1, nameplateHeight + 0.1, 0.05)
  const borderMaterial = materials.metal(COLORS.industrial.black)
  const border = new THREE.Mesh(borderGeometry, borderMaterial)
  border.position.set(radius + 0.1, height * 0.6 + 2, 0.03)
  group.add(border)

  return group
}

export function createLowDetailTank(capacity, label) {
  const tankGroup = new THREE.Group()
  tankGroup.userData.deviceId = label

  const height = DIMENSIONS.tank.defaultHeight + capacity / 30
  const radius = DIMENSIONS.tank.defaultRadius
  const bodyMaterial = materials.metal(COLORS.equipment.tank)

  const bodyGeometry = new THREE.CylinderGeometry(radius, radius, height + 2, SEGMENTS.coarse)
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = height / 2 + 2
  body.castShadow = true
  tankGroup.add(body)

  const roofGeometry = new THREE.SphereGeometry(
    radius, SEGMENTS.coarse, SEGMENTS.coarse / 2, 0, Math.PI * 2, 0, Math.PI / 6
  )
  const roof = new THREE.Mesh(roofGeometry, bodyMaterial)
  roof.position.y = height + 2
  tankGroup.add(roof)

  return tankGroup
}
