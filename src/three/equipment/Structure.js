import * as THREE from 'three'
import { COLORS, DIMENSIONS, SEGMENTS } from '../constants.js'
import { materials } from '../materials.js'

export function createPlatforms(scene) {
  const platformGroup = new THREE.Group()

  const gratingMaterial = materials.roughMetal(COLORS.industrial.steelLight)
  const railMaterial = materials.emissive(COLORS.safety.yellow, 0.1)
  const ladderMaterial = materials.metal(COLORS.industrial.steelLight, { roughness: 0.25, metalness: 0.9 })

  const mainPlatformGeometry = new THREE.BoxGeometry(
    DIMENSIONS.platform.mainWidth,
    DIMENSIONS.platform.thickness,
    DIMENSIONS.platform.mainDepth
  )
  const mainPlatform = new THREE.Mesh(mainPlatformGeometry, gratingMaterial)
  mainPlatform.position.set(0, DIMENSIONS.platform.height, 8)
  mainPlatform.castShadow = true
  mainPlatform.receiveShadow = true
  platformGroup.add(mainPlatform)

  const railGeometry = new THREE.BoxGeometry(
    DIMENSIONS.platform.railWidth,
    DIMENSIONS.platform.railHeight,
    DIMENSIONS.platform.railWidth
  )

  const railPositions = [
    [4, DIMENSIONS.platform.height + 0.55, 10.4],
    [-4, DIMENSIONS.platform.height + 0.55, 10.4],
    [4, DIMENSIONS.platform.height + 0.55, 5.6],
    [-4, DIMENSIONS.platform.height + 0.55, 5.6]
  ]

  railPositions.forEach(pos => {
    const rail = new THREE.Mesh(railGeometry, railMaterial)
    rail.position.set(...pos)
    platformGroup.add(rail)
  })

  const topRailGeometry = new THREE.BoxGeometry(
    DIMENSIONS.platform.mainWidth + 0.3,
    DIMENSIONS.platform.railWidth,
    DIMENSIONS.platform.railWidth
  )

  const topRail1 = new THREE.Mesh(topRailGeometry, railMaterial)
  topRail1.position.set(0, DIMENSIONS.platform.height + 1.1, 10.4)
  platformGroup.add(topRail1)

  const topRail2 = new THREE.Mesh(topRailGeometry, railMaterial)
  topRail2.position.set(0, DIMENSIONS.platform.height + 1.1, 5.6)
  platformGroup.add(topRail2)

  const ladderGeometry = new THREE.BoxGeometry(
    DIMENSIONS.platform.ladderWidth,
    DIMENSIONS.platform.height,
    DIMENSIONS.platform.ladderWidth
  )

  const ladder1 = new THREE.Mesh(ladderGeometry, ladderMaterial)
  ladder1.position.set(5, DIMENSIONS.platform.height / 2, 8)
  platformGroup.add(ladder1)

  const rungGeometry = new THREE.BoxGeometry(
    DIMENSIONS.platform.rungWidth,
    DIMENSIONS.platform.rungHeight,
    DIMENSIONS.platform.ladderWidth
  )

  for (let i = 0; i < 5; i++) {
    const rung = new THREE.Mesh(rungGeometry, ladderMaterial)
    rung.position.set(4.6, 1.5 + i * 1.2, 8)
    platformGroup.add(rung)
  }

  scene.add(platformGroup)

  return platformGroup
}

export function createSupportStructures(scene) {
  const structureGroup = new THREE.Group()
  const beamMaterial = materials.roughMetal(COLORS.equipment.structure)

  const columnGeometry = new THREE.BoxGeometry(
    DIMENSIONS.structure.columnWidth,
    DIMENSIONS.structure.columnHeight,
    DIMENSIONS.structure.columnWidth
  )

  const columns = [
    [-30, 7.5, -30], [-30, 7.5, 30], [30, 7.5, -30], [30, 7.5, 30],
    [-30, 7.5, -10], [30, 7.5, -10], [-30, 7.5, 10], [30, 7.5, 10]
  ]

  columns.forEach(pos => {
    const column = new THREE.Mesh(columnGeometry, beamMaterial)
    column.position.set(...pos)
    column.castShadow = true
    structureGroup.add(column)
  })

  const horizontalBeamGeometry = new THREE.BoxGeometry(
    DIMENSIONS.structure.beamWidth,
    DIMENSIONS.structure.beamHeight,
    DIMENSIONS.structure.beamDepth
  )

  const beamPositions = [
    { y: 14, z: -30 }, { y: 14, z: 30 }, { y: 14, z: -10 }, { y: 14, z: 10 },
    { y: 7, z: -30 }, { y: 7, z: 30 }
  ]

  beamPositions.forEach(config => {
    const beam = new THREE.Mesh(horizontalBeamGeometry, beamMaterial)
    beam.position.set(0, config.y, config.z)
    structureGroup.add(beam)
  })

  const crossBeamGeometry = new THREE.BoxGeometry(
    DIMENSIONS.structure.beamDepth,
    DIMENSIONS.structure.beamHeight,
    DIMENSIONS.structure.beamWidth
  )

  const crossBeamPositions = [
    { y: 14, x: -30 }, { y: 14, x: 30 }, { y: 14, x: 0 },
    { y: 7, x: -30 }, { y: 7, x: 30 }
  ]

  crossBeamPositions.forEach(config => {
    const beam = new THREE.Mesh(crossBeamGeometry, beamMaterial)
    beam.position.set(config.x, config.y, 0)
    structureGroup.add(beam)
  })

  scene.add(structureGroup)

  return structureGroup
}
