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

  const height = DIMENSIONS.tank.defaultHeight + capacity / 30
  const radius = DIMENSIONS.tank.defaultRadius

  const bodyMaterial = materials.metal(COLORS.equipment.tank)

  const bodyGeometry = new THREE.CylinderGeometry(radius, radius, height, SEGMENTS.cylinder)
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = height / 2
  body.castShadow = true
  body.receiveShadow = true
  tankGroup.add(body)

  const roofGeometry = new THREE.SphereGeometry(
    radius, SEGMENTS.cylinder, SEGMENTS.cylinder / 2, 0, Math.PI * 2, 0, Math.PI / 6
  )
  const roof = new THREE.Mesh(roofGeometry, bodyMaterial)
  roof.position.y = height
  roof.castShadow = true
  tankGroup.add(roof)

  const bottomGeometry = new THREE.CylinderGeometry(
    radius + DIMENSIONS.tank.bottomRadiusExtra,
    radius + 1,
    DIMENSIONS.tank.bottomThickness,
    SEGMENTS.fine
  )
  const bottom = new THREE.Mesh(bottomGeometry, bodyMaterial)
  bottom.position.y = 0.25
  tankGroup.add(bottom)

  const levelGeometry = new THREE.CylinderGeometry(
    radius - DIMENSIONS.tank.levelRadiusExtra,
    radius - DIMENSIONS.tank.levelRadiusExtra,
    height * DIMENSIONS.tank.levelHeightRatio,
    SEGMENTS.fine,
    1,
    true
  )
  const levelMaterial = materials.glass(COLORS.indicators.liquid, 0.3)
  const level = new THREE.Mesh(levelGeometry, levelMaterial)
  level.position.y = height * 0.3
  tankGroup.add(level)

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

function createLadder(radius, height) {
  const ladderGroup = new THREE.Group()
  const { ladderRailWidth, ladderRailGap } = DIMENSIONS.tank
  const railsMaterial = materials.metal(COLORS.industrial.steelLight, { roughness: 0.2, metalness: 0.9 })

  const railsGeometry = new THREE.BoxGeometry(ladderRailWidth, height, ladderRailWidth)
  const rail1 = new THREE.Mesh(railsGeometry, railsMaterial)
  rail1.position.set(radius + ladderRailGap, height / 2, 0)
  ladderGroup.add(rail1)

  const rail2 = new THREE.Mesh(railsGeometry, railsMaterial)
  rail2.position.set(radius + ladderRailGap * 2, height / 2, 0)
  ladderGroup.add(rail2)

  const rungGeometry = new THREE.BoxGeometry(0.35, 0.06, 0.06)
  const rungCount = 8
  for (let i = 0; i < rungCount; i++) {
    const rung = new THREE.Mesh(rungGeometry, railsMaterial)
    rung.position.set(radius + ladderRailGap + 0.175, 1 + i * (height - 2) / (rungCount - 1), 0)
    ladderGroup.add(rung)
  }

  return ladderGroup
}

function createTankPlatform(radius, height) {
  const { platformWidth, platformDepth } = DIMENSIONS.tank
  const platformMaterial = materials.metal(COLORS.industrial.steelLight, { roughness: 0.3, metalness: 0.85 })

  const platformGeometry = new THREE.BoxGeometry(platformWidth, 0.15, platformDepth)
  const platform = new THREE.Mesh(platformGeometry, platformMaterial)
  platform.position.set(radius + 1, height + 0.5, 0)
  return platform
}

function createRailings(radius, height) {
  const railings = []
  const { railingHeight } = DIMENSIONS.tank
  const railingMaterial = materials.emissive(COLORS.safety.yellow, 0.1)
  const railingGeometry = new THREE.BoxGeometry(0.04, railingHeight, 0.04)

  const positions = [
    [radius + 0.5, height + 1, -0.9],
    [radius + 0.5, height + 1, 0.9],
    [radius + 1.9, height + 1, 0]
  ]

  positions.forEach(pos => {
    const railing = new THREE.Mesh(railingGeometry, railingMaterial)
    railing.position.set(...pos)
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
  plate.position.set(radius + 0.1, height / 2, 0)
  group.add(plate)

  const borderGeometry = new THREE.BoxGeometry(nameplateWidth + 0.1, nameplateHeight + 0.1, 0.05)
  const borderMaterial = materials.metal(COLORS.industrial.black)
  const border = new THREE.Mesh(borderGeometry, borderMaterial)
  border.position.set(radius + 0.1, height / 2, 0.03)
  group.add(border)

  return group
}
