import * as THREE from 'three'
import { COLORS, DIMENSIONS, SEGMENTS } from '../constants.js'
import { materials } from '../materials.js'

export function createConveyor(scene) {
  const conveyorGroup = new THREE.Group()
  conveyorGroup.position.set(15, 0, 15)

  const frameMaterial = materials.roughMetal(COLORS.equipment.conveyor)
  const beltMaterial = materials.rubber(0x2a2a2a)

  const beltGeometry = new THREE.BoxGeometry(
    DIMENSIONS.conveyor.beltWidth,
    DIMENSIONS.conveyor.beltHeight,
    DIMENSIONS.conveyor.beltDepth
  )
  const belt = new THREE.Mesh(beltGeometry, beltMaterial)
  belt.position.y = DIMENSIONS.conveyor.beltHeight / 2 + 3
  belt.receiveShadow = true
  conveyorGroup.add(belt)

  const sideRailGeometry = new THREE.BoxGeometry(
    DIMENSIONS.conveyor.beltWidth,
    DIMENSIONS.conveyor.sideRailHeight,
    DIMENSIONS.conveyor.sideRailThickness
  )
  const sideRail1 = new THREE.Mesh(sideRailGeometry, frameMaterial)
  sideRail1.position.set(0, DIMENSIONS.conveyor.beltHeight / 2 + 3 + 0.2, 1.5)
  conveyorGroup.add(sideRail1)

  const sideRail2 = new THREE.Mesh(sideRailGeometry, frameMaterial)
  sideRail2.position.set(0, DIMENSIONS.conveyor.beltHeight / 2 + 3 + 0.2, -1.5)
  conveyorGroup.add(sideRail2)

  const legGeometry = new THREE.BoxGeometry(
    DIMENSIONS.conveyor.legWidth,
    DIMENSIONS.conveyor.legHeight,
    DIMENSIONS.conveyor.legWidth
  )

  const legPositions = [
    [-11, 1.5, -1.3], [-11, 1.5, 1.3],
    [11, 1.5, -1.3], [11, 1.5, 1.3],
    [0, 1.5, -1.3], [0, 1.5, 1.3]
  ]

  legPositions.forEach(pos => {
    const leg = new THREE.Mesh(legGeometry, frameMaterial)
    leg.position.set(...pos)
    leg.castShadow = true
    conveyorGroup.add(leg)
  })

  const rollerGeometry = new THREE.CylinderGeometry(
    DIMENSIONS.conveyor.rollerRadius,
    DIMENSIONS.conveyor.rollerRadius,
    DIMENSIONS.conveyor.beltDepth + 0.5,
    SEGMENTS.smallSphere
  )
  const rollerMaterial = materials.metal(COLORS.industrial.steelLight)

  const rollers = []
  for (let i = -11; i <= 11; i += 2) {
    const roller = new THREE.Mesh(rollerGeometry, rollerMaterial)
    roller.rotation.x = Math.PI / 2
    roller.position.set(i, DIMENSIONS.conveyor.rollerRadius + 3, 0)
    conveyorGroup.add(roller)
    rollers.push(roller)
  }

  const drumGeometry = new THREE.CylinderGeometry(
    DIMENSIONS.conveyor.drumRadius,
    DIMENSIONS.conveyor.drumRadius,
    DIMENSIONS.conveyor.beltDepth + 0.5,
    SEGMENTS.smallSphere
  )
  const drumMaterial = materials.metal(COLORS.industrial.steelLight)

  const drum1 = new THREE.Mesh(drumGeometry, drumMaterial)
  drum1.rotation.x = Math.PI / 2
  drum1.position.set(-12, DIMENSIONS.conveyor.drumRadius + 3, 0)
  drum1.castShadow = true
  conveyorGroup.add(drum1)

  const drum2 = new THREE.Mesh(drumGeometry, drumMaterial)
  drum2.rotation.x = Math.PI / 2
  drum2.position.set(12, DIMENSIONS.conveyor.drumRadius + 3, 0)
  drum2.castShadow = true
  conveyorGroup.add(drum2)

  const products = createConveyorProducts()
  products.forEach(product => conveyorGroup.add(product))
  conveyorGroup.userData.products = products

  scene.add(conveyorGroup)

  return {
    group: conveyorGroup,
    rollerStart: rollers[0],
    rollerEnd: rollers[rollers.length - 1],
    products
  }
}

function createConveyorProducts() {
  const products = []
  const productGeometry = new THREE.BoxGeometry(
    DIMENSIONS.conveyor.productSize,
    DIMENSIONS.conveyor.productSize,
    DIMENSIONS.conveyor.productSize
  )
  const productMaterial = materials.emissive(COLORS.indicators.product, 0.3)

  const positions = [-15, -10, -5, 0, 5, 10, 15]

  positions.forEach(xPos => {
    const product = new THREE.Mesh(productGeometry, productMaterial.clone())
    product.position.set(xPos, DIMENSIONS.conveyor.productSize / 2 + 3.25, 0)
    product.castShadow = true
    products.push(product)
  })

  return products
}
