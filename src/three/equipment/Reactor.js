import * as THREE from 'three'
import { COLORS, DIMENSIONS, SEGMENTS } from '../constants.js'
import { materials } from '../materials.js'

export function createReactor(scene) {
  const reactor = new THREE.Group()
  reactor.position.set(0, 0, 0)

  const reactorBody = createReactorBody()
  reactor.add(reactorBody)

  const internals = createReactorInternals()
  reactor.add(internals.group)
  internals.stirrerGroup.position.y = DIMENSIONS.reactor.bodyHeight / 2 + 4

  const support = createReactorSupport()
  reactor.add(support)

  const nozzles = createReactorNozzles()
  reactor.add(nozzles.group)

  const indicator = createReactorIndicator()
  indicator.position.set(6, 14, 0)
  reactor.add(indicator)

  const sightGlass = createSightGlass()
  sightGlass.position.set(5.5, 8, 0)
  sightGlass.rotation.z = Math.PI / 2
  reactor.add(sightGlass)

  const nameplate = createNameplate()
  nameplate.position.set(5.5, 5, 0)
  nameplate.rotation.y = Math.PI / 2
  reactor.add(nameplate)

  scene.add(reactor)

  return {
    group: reactor,
    stirrer: internals.stirrerGroup,
    indicator,
    nozzles: nozzles.group
  }
}

function createReactorBody() {
  const group = new THREE.Group()

  const { bodyRadius, bodyRadiusBottom, bodyHeight } = DIMENSIONS.reactor
  const bodyMaterial = materials.metal(COLORS.equipment.reactor)

  const bodyGeometry = new THREE.CylinderGeometry(
    bodyRadius, bodyRadiusBottom, bodyHeight, SEGMENTS.cylinder
  )
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = bodyHeight / 2
  body.castShadow = true
  body.receiveShadow = true
  group.add(body)

  const topDomeGeometry = new THREE.SphereGeometry(
    bodyRadius, SEGMENTS.cylinder, SEGMENTS.cylinder / 2, 0, Math.PI * 2, 0, Math.PI / 2
  )
  const topDome = new THREE.Mesh(topDomeGeometry, bodyMaterial)
  topDome.position.y = bodyHeight
  topDome.castShadow = true
  group.add(topDome)

  const bottomDomeGeometry = new THREE.SphereGeometry(
    bodyRadiusBottom, SEGMENTS.cylinder, SEGMENTS.cylinder / 2, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2
  )
  const bottomDome = new THREE.Mesh(bottomDomeGeometry, bodyMaterial)
  bottomDome.position.y = 1.5
  bottomDome.castShadow = true
  group.add(bottomDome)

  const rimGeometry = new THREE.TorusGeometry(
    DIMENSIONS.reactor.rimRadius, DIMENSIONS.reactor.rimTube, SEGMENTS.cylinder / 2, SEGMENTS.cylinder
  )
  const rimMaterial = materials.steel(COLORS.industrial.steelLight)
  const rim = new THREE.Mesh(rimGeometry, rimMaterial)
  rim.position.y = bodyHeight
  rim.rotation.x = Math.PI / 2
  group.add(rim)

  return group
}

function createReactorInternals() {
  const group = new THREE.Group()
  const stirrerGroup = new THREE.Group()

  const { shaftRadius, shaftHeight, hubRadius, hubHeight, bladeWidth, bladeHeight, bladeDepth,
    baffleWidth, baffleHeight, baffleDepth } = DIMENSIONS.reactor
  const shaftMaterial = materials.steel(COLORS.industrial.steelLight)

  const shaftGeometry = new THREE.CylinderGeometry(shaftRadius, shaftRadius, shaftHeight, SEGMENTS.smallCylinder)
  const shaft = new THREE.Mesh(shaftGeometry, shaftMaterial)
  shaft.position.y = -shaftHeight / 2 + 2
  stirrerGroup.add(shaft)

  const hubGeometry = new THREE.CylinderGeometry(hubRadius, hubRadius, hubHeight, SEGMENTS.smallCylinder)
  const hub = new THREE.Mesh(hubGeometry, shaftMaterial)
  stirrerGroup.add(hub)

  const bladeMaterial = materials.steel(COLORS.industrial.steelLight, { roughness: 0.12, metalness: 0.98 })
  const bladeGeometry = new THREE.BoxGeometry(bladeWidth, bladeHeight, bladeDepth)

  for (let i = 0; i < 4; i++) {
    const blade = new THREE.Mesh(bladeGeometry, bladeMaterial)
    blade.position.y = -2 - i * 2.5
    blade.rotation.y = (Math.PI / 2) * i
    stirrerGroup.add(blade)
  }

  const baffleMaterial = materials.metal(COLORS.industrial.steelLight, { roughness: 0.15, metalness: 0.95 })
  const baffleGeometry = new THREE.BoxGeometry(baffleWidth, baffleHeight, baffleDepth)

  for (let i = 0; i < 4; i++) {
    const baffle = new THREE.Mesh(baffleGeometry, baffleMaterial)
    baffle.position.y = baffleHeight / 2
    baffle.rotation.y = (Math.PI / 4) + (Math.PI / 2) * i
    baffle.position.x = Math.cos((Math.PI / 4) + (Math.PI / 2) * i) * 3.5
    baffle.position.z = Math.sin((Math.PI / 4) + (Math.PI / 2) * i) * 3.5
    group.add(baffle)
  }

  group.add(stirrerGroup)

  return { group, stirrerGroup }
}

function createReactorSupport() {
  const group = new THREE.Group()
  const { legRadiusTop, legRadiusBottom, legHeight, supportRingRadius, supportRingTube } = DIMENSIONS.reactor
  const legMaterial = materials.metal(COLORS.industrial.steelLight, { roughness: 0.2, metalness: 0.9 })

  const legGeometry = new THREE.CylinderGeometry(legRadiusTop, legRadiusBottom, legHeight, SEGMENTS.coarse)

  const positions = [
    [3.5, 2, 3.5], [-3.5, 2, 3.5], [3.5, 2, -3.5], [-3.5, 2, -3.5]
  ]

  positions.forEach(pos => {
    const leg = new THREE.Mesh(legGeometry, legMaterial)
    leg.position.set(...pos)
    leg.castShadow = true
    group.add(leg)
  })

  const ringGeometry = new THREE.TorusGeometry(supportRingRadius, supportRingTube, SEGMENTS.coarse, SEGMENTS.fine)
  const ring = new THREE.Mesh(ringGeometry, legMaterial)
  ring.position.y = 0.5
  ring.rotation.x = Math.PI / 2
  group.add(ring)

  return group
}

function createReactorNozzles() {
  const group = new THREE.Group()
  const { nozzleRadius, nozzleLength, flangeRadius, flangeThickness } = DIMENSIONS.reactor
  const nozzleMaterial = materials.metal(COLORS.industrial.steelDark)

  const nozzleGeometry = new THREE.CylinderGeometry(nozzleRadius, nozzleRadius, nozzleLength, SEGMENTS.smallSphere)
  const flangeGeometry = new THREE.CylinderGeometry(flangeRadius, flangeRadius, flangeThickness, SEGMENTS.smallSphere)

  const nozzlePositions = [
    { pos: [5.5, 12, 0], rot: [0, 0, Math.PI / 2] },
    { pos: [-5.5, 10, 0], rot: [0, 0, -Math.PI / 2] },
    { pos: [0, 17, 5.5], rot: [Math.PI / 2, 0, 0] }
  ]

  nozzlePositions.forEach(config => {
    const nozzle = new THREE.Mesh(nozzleGeometry, nozzleMaterial)
    nozzle.position.set(...config.pos)
    nozzle.rotation.set(...config.rot)
    group.add(nozzle)

    const flange = new THREE.Mesh(flangeGeometry, nozzleMaterial)
    flange.position.set(...config.pos)
    flange.rotation.set(...config.rot)
    const offset = config.rot[2] === Math.PI / 2 ? 0.9 : config.rot[2] === -Math.PI / 2 ? -0.9 : 0
    flange.position.x += offset
    flange.position.y += config.rot[0] === Math.PI / 2 ? 0.9 : 0
    flange.position.z += config.rot[0] === Math.PI / 2 ? 0.9 : 0
    group.add(flange)
  })

  return { group }
}

function createReactorIndicator() {
  const { indicatorRadius } = DIMENSIONS.reactor
  const material = materials.emissive(COLORS.indicators.running, 0.8)
  const geometry = new THREE.SphereGeometry(indicatorRadius, SEGMENTS.smallSphere, SEGMENTS.smallSphere)
  const indicator = new THREE.Mesh(geometry, material)
  return indicator
}

function createSightGlass() {
  const { sightGlassRadius, sightGlassLength } = DIMENSIONS.reactor
  const material = materials.glass(COLORS.indicators.liquid, 0.4)
  const geometry = new THREE.CylinderGeometry(sightGlassRadius, sightGlassRadius, sightGlassLength, SEGMENTS.smallSphere)
  const sightGlass = new THREE.Mesh(geometry, material)
  return sightGlass
}

function createNameplate() {
  const { nameplateWidth, nameplateHeight } = DIMENSIONS.tank
  const group = new THREE.Group()

  const plateMaterial = materials.emissive(COLORS.safety.yellow, 0.1)
  const plateGeometry = new THREE.BoxGeometry(nameplateWidth, nameplateHeight, 0.1)
  const plate = new THREE.Mesh(plateGeometry, plateMaterial)
  group.add(plate)

  const borderGeometry = new THREE.BoxGeometry(nameplateWidth + 0.1, nameplateHeight + 0.1, 0.05)
  const borderMaterial = materials.metal(COLORS.industrial.black)
  const border = new THREE.Mesh(borderGeometry, borderMaterial)
  border.position.z = -0.03
  group.add(border)

  return group
}
