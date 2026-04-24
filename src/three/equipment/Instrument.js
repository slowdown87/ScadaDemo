import * as THREE from 'three'
import { COLORS, DIMENSIONS, SEGMENTS } from '../constants.js'
import { materials } from '../materials.js'

export function createInstrumentPanel(scene) {
  const instrumentGroup = new THREE.Group()

  const panelMaterial = materials.roughMetal(0x404040, { roughness: 0.7, metalness: 0.3 })

  const panelGeometry = new THREE.BoxGeometry(
    DIMENSIONS.instrument.panelWidth,
    DIMENSIONS.instrument.panelHeight,
    DIMENSIONS.instrument.panelDepth
  )
  const panel = new THREE.Mesh(panelGeometry, panelMaterial)
  panel.position.set(20, 2, 20)
  panel.castShadow = true
  instrumentGroup.add(panel)

  const screenMaterial = materials.emissive(0x00aaff, 0.5)
  const screenGeometry = new THREE.BoxGeometry(
    DIMENSIONS.instrument.screenWidth,
    DIMENSIONS.instrument.screenHeight,
    0.03
  )
  const screen = new THREE.Mesh(screenGeometry, screenMaterial)
  screen.position.set(19.3, 2.3, 20.15)
  instrumentGroup.add(screen)

  const buttonMaterial = materials.emissive(COLORS.indicators.running, 0.5)
  const buttonGeometry = new THREE.CylinderGeometry(
    DIMENSIONS.instrument.buttonRadius,
    DIMENSIONS.instrument.buttonRadius,
    DIMENSIONS.instrument.buttonHeight,
    SEGMENTS.bolt
  )

  for (let i = 0; i < 4; i++) {
    const button = new THREE.Mesh(buttonGeometry, buttonMaterial)
    button.rotation.x = Math.PI / 2
    button.position.set(20.5 + (i - 1.5) * 0.3, 1.4, 20.15)
    instrumentGroup.add(button)
  }

  const indicatorLightMaterial = materials.emissive(COLORS.indicators.running, 0.9)
  const indicatorLightGeometry = new THREE.SphereGeometry(
    DIMENSIONS.instrument.lightRadius,
    SEGMENTS.bolt,
    SEGMENTS.bolt
  )

  for (let i = 0; i < 3; i++) {
    const light = new THREE.Mesh(indicatorLightGeometry, indicatorLightMaterial)
    light.position.set(18.8 + i * 0.25, 2.8, 20.15)
    instrumentGroup.add(light)
  }

  scene.add(instrumentGroup)

  return instrumentGroup
}
