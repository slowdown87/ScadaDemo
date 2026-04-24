import * as THREE from 'three'
import { COLORS, DIMENSIONS, POSITIONS } from '../constants.js'

export function setupLights(scene, options = {}) {
  const lights = {
    ambient: null,
    hemisphere: null,
    main: null,
    fill: null,
    floorReflect: null,
    ceiling: []
  }

  lights.ambient = new THREE.AmbientLight(COLORS.industrial.white, 0.7)
  scene.add(lights.ambient)

  lights.hemisphere = new THREE.HemisphereLight(0xadd8e6, 0x808080, 0.8)
  scene.add(lights.hemisphere)

  const shadowConfig = options.shadowMapSize || 2048
  const shadowAutoUpdate = options.shadowAutoUpdate !== undefined ? options.shadowAutoUpdate : false

  lights.main = new THREE.DirectionalLight(COLORS.industrial.white, 1.2)
  lights.main.position.set(...POSITIONS.mainLight.pos)
  lights.main.castShadow = true
  lights.main.shadow.mapSize.width = shadowConfig
  lights.main.shadow.mapSize.height = shadowConfig
  lights.main.shadow.camera.near = DIMENSIONS.scene.maxCameraDistance / 100
  lights.main.shadow.camera.far = 300
  lights.main.shadow.camera.left = -120
  lights.main.shadow.camera.right = 120
  lights.main.shadow.camera.top = 120
  lights.main.shadow.camera.bottom = -120
  lights.main.shadow.bias = -0.0001
  lights.main.shadow.autoUpdate = shadowAutoUpdate
  scene.add(lights.main)

  lights.fill = new THREE.DirectionalLight(COLORS.industrial.white, 0.6)
  lights.fill.position.set(...POSITIONS.fillLight.pos)
  scene.add(lights.fill)

  const ceilingLights = createCeilingLights()
  ceilingLights.forEach(light => {
    scene.add(light.pole)
    scene.add(light.lamp)
    scene.add(light.glow)
    scene.add(light.pointLight)
  })
  lights.ceiling = ceilingLights

  lights.floorReflect = new THREE.PointLight(
    COLORS.industrial.white,
    POSITIONS.floorReflectLight.intensity,
    POSITIONS.floorReflectLight.range
  )
  lights.floorReflect.position.set(...POSITIONS.floorReflectLight.pos)
  scene.add(lights.floorReflect)

  return lights
}

function createCeilingLights() {
  const { poleRadius, poleHeight, lampWidth, lampHeight, lampDepth,
    glowWidth, glowHeight, lightIntensity, lightRange } = DIMENSIONS.ceilingLights

  const poleGeometry = new THREE.CylinderGeometry(poleRadius, poleRadius, poleHeight, 16)
  const poleMaterial = new THREE.MeshStandardMaterial({
    color: COLORS.industrial.gray,
    roughness: 0.5,
    metalness: 0.7
  })

  const lampGeometry = new THREE.BoxGeometry(lampWidth, lampHeight, lampDepth)
  const lampMaterial = new THREE.MeshStandardMaterial({
    color: 0x303030,
    roughness: 0.3,
    metalness: 0.8
  })

  const glowGeometry = new THREE.BoxGeometry(glowWidth, glowHeight, 0.5)
  const glowMaterial = new THREE.MeshStandardMaterial({
    color: COLORS.lights.lampGlow,
    emissive: COLORS.lights.lampGlow,
    emissiveIntensity: 1,
    roughness: 0.2
  })

  const lights = []

  POSITIONS.ceilingLights.forEach(pos => {
    const pole = new THREE.Mesh(poleGeometry, poleMaterial)
    pole.position.set(pos[0], pos[1] - poleHeight / 2, pos[2])
    pole.castShadow = true

    const lamp = new THREE.Mesh(lampGeometry, lampMaterial)
    lamp.position.set(pos[0], pos[1], pos[2])

    const glow = new THREE.Mesh(glowGeometry, glowMaterial)
    glow.position.set(pos[0], pos[1] - 0.15, pos[2])

    const pointLight = new THREE.PointLight(COLORS.lights.lamp, lightIntensity, lightRange)
    pointLight.position.set(pos[0], pos[1] - 1, pos[2])
    pointLight.castShadow = false

    lights.push({ pole, lamp, glow, pointLight })
  })

  return lights
}

export function updateLightShadow(lights, needsUpdate) {
  if (lights.main && lights.main.shadow.autoUpdate === false) {
    lights.main.shadow.needsUpdate = needsUpdate
  }
}

export function disposeLights(lights) {
  if (lights.ambient) {
    lights.ambient.dispose()
  }
  if (lights.hemisphere) {
    lights.hemisphere.dispose()
  }
  if (lights.main) {
    lights.main.dispose()
  }
  if (lights.fill) {
    lights.fill.dispose()
  }
  if (lights.floorReflect) {
    lights.floorReflect.dispose()
  }
  if (lights.ceiling) {
    lights.ceiling.forEach(light => {
      light.pointLight.dispose()
    })
  }
}
