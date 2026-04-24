import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js'
import { SSAOPass } from 'three/addons/postprocessing/SSAOPass.js'
import { OutlinePass } from 'three/addons/postprocessing/OutlinePass.js'
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'

import { POSITIONS, ANIMATION } from './constants.js'
import { materials } from './materials.js'
import { geometries } from './geometries.js'
import { setupLights, updateLightShadow, disposeLights } from './lighting/Lights.js'
import { createGround } from './environment/Ground.js'
import { createReactor } from './equipment/Reactor.js'
import { createTanks, createLowDetailTank } from './equipment/Tank.js'
import { createPipeNetwork } from './equipment/PipeNetwork.js'
import { createConveyor } from './equipment/Conveyor.js'
import { createPlatforms, createSupportStructures } from './equipment/Structure.js'
import { createInstrumentPanel } from './equipment/Instrument.js'
import { createWorkers } from './equipment/Workers.js'
import { createFlowParticles, createDustParticles, updateParticles, updateFlowParticles } from './equipment/Particles.js'
import { lodManager } from './LODManager.js'
import { MaterialTracker } from './material/MaterialTracker.js'

export class Plant3D {
  constructor(container) {
    this.container = container
    this.scene = null
    this.camera = null
    this.renderer = null
    this.controls = null
    this.composer = null
    this.lights = null

    this.equipment = {}
    this.particles = {}
    this.materialTracker = null
    this.animationId = null

    this.data = {
      tankLevel: 50,
      flowRate: 0,
      reactorTemp: 25,
      reactorPressure: 1.0,
      motorSpeed: 0,
      productCount: 0
    }

    this.needsRender = true
    this.needsShadowUpdate = false
    this.isRunning = false
  }

  init() {
    this.setupScene()
    this.setupCamera()
    this.setupRenderer()
    this.setupControls()
    this.lights = setupLights(this.scene, {
      shadowMapSize: 2048,
      shadowAutoUpdate: false
    })
    this.setupPostProcessing()

    this.createIndustrialPlant()
    this.createParticles()
    this.materialTracker = new MaterialTracker(this.scene)
    this.needsRender = true
    this.animate()

    return this
  }

  setupScene() {
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x8090a0)
    this.scene.fog = new THREE.FogExp2(0x8090a0, 0.004)
  }

  setupCamera() {
    const aspect = this.container.clientWidth / this.container.clientHeight
    this.camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 500)
    this.camera.position.set(50, 40, 60)
    this.camera.lookAt(0, 8, 0)
  }

  setupRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: 'high-performance'
    })
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight)
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.shadowMap.autoUpdate = false
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1.2
    this.container.appendChild(this.renderer.domElement)

    this.resizeObserver = new ResizeObserver(() => {
      this.handleResize()
    })
    this.resizeObserver.observe(this.container)
  }

  handleResize() {
    const width = this.container.clientWidth
    const height = this.container.clientHeight

    if (width === 0 || height === 0) return

    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(width, height)
    this.composer.setSize(width, height)

    if (this.ssaoPass) {
      this.ssaoPass.setSize(width, height)
    }
    if (this.outlinePass) {
      this.outlinePass.setSize(width, height)
    }

    this.needsRender = true
  }

  setupControls() {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableDamping = true
    this.controls.dampingFactor = 0.03
    this.controls.maxDistance = 120
    this.controls.minDistance = 20
    this.controls.maxPolarAngle = Math.PI / 2.1
    this.controls.target.set(0, 8, 0)
  }

  setupPostProcessing() {
    this.composer = new EffectComposer(this.renderer)
    const renderPass = new RenderPass(this.scene, this.camera)
    this.composer.addPass(renderPass)

    const width = this.container.clientWidth
    const height = this.container.clientHeight

    this.ssaoPass = new SSAOPass(this.scene, this.camera, width, height)
    this.ssaoPass.kernelRadius = 16
    this.ssaoPass.minDistance = 0.005
    this.ssaoPass.maxDistance = 0.1
    this.composer.addPass(this.ssaoPass)

    this.outlinePass = new OutlinePass(width, height, this.scene, this.camera)
    this.outlinePass.edgeStrength = 3.0
    this.outlinePass.edgeGlow = 0.5
    this.outlinePass.edgeThickness = 1.0
    this.outlinePass.pulsePeriod = 0
    this.outlinePass.visibleEdgeColor.set(0x00aaff)
    this.outlinePass.hiddenEdgeColor.set(0x004488)
    this.composer.addPass(this.outlinePass)

    const outputPass = new OutputPass()
    this.composer.addPass(outputPass)
  }

  createIndustrialPlant() {
    createGround(this.scene)

    const reactor = createReactor(this.scene)
    this.equipment.reactor = reactor.group
    this.equipment.stirrer = reactor.stirrer
    this.equipment.reactorIndicator = reactor.indicator

    const tanks = createTanks(this.scene)
    this.equipment.tanks = tanks.group

    tanks.tanks.forEach((tank, index) => {
      const tankId = `tank_${index}`
      const tankLow = createLowDetailTank(tank.userData.capacity || 100, tank.userData.deviceId)
      tankLow.visible = false
      tank.add(tankLow)
      lodManager.register(tankId, tank, null, tankLow)
    })

    this.equipment.tankLevel1 = tanks.tanks[0].children.find(
      c => c.type === 'Mesh' && c.geometry.type === 'CylinderGeometry'
    )

    const pipes = createPipeNetwork(this.scene)
    this.equipment.pipes = pipes.group
    this.equipment.valve1 = pipes.valves[0]?.group
    this.equipment.valve2 = pipes.valves[1]?.group
    this.equipment.valve3 = pipes.valves[2]?.group
    this.equipment.valve4 = pipes.valves[3]?.group

    const conveyor = createConveyor(this.scene)
    this.equipment.conveyor = conveyor.group
    this.equipment.rollerStart = conveyor.rollerStart
    this.equipment.rollerEnd = conveyor.rollerEnd
    this.equipment.conveyorProducts = conveyor.products

    const platforms = createPlatforms(this.scene)
    this.equipment.platforms = platforms

    const structures = createSupportStructures(this.scene)
    this.equipment.structures = structures

    const instrument = createInstrumentPanel(this.scene)
    this.equipment.instruments = instrument

    const workers = createWorkers(this.scene)
    this.equipment.workers = workers.workers
  }

  createParticles() {
    this.equipment.flowParticles = createFlowParticles(this.scene)
    this.particles.dust = createDustParticles(this.scene)
  }

  animate() {
    this.isRunning = true
    this.animationId = requestAnimationFrame(() => this.animate())

    if (!this.needsRender) {
      return
    }

    this.controls.update()

    lodManager.update(this.camera)

    if (this.needsShadowUpdate) {
      this.renderer.shadowMap.update()
      this.needsShadowUpdate = false
    }

    this.composer.render()
    this.needsRender = false

    const time = Date.now() * 0.001
    this.updateAnimations(time)
  }

  updateAnimations(time) {
    if (this.equipment.stirrer && this.data.motorSpeed > 0) {
      const speed = this.data.motorSpeed / ANIMATION.stirrer.maxSpeedRatio
      this.equipment.stirrer.rotation.y += ANIMATION.stirrer.baseSpeed * speed
      this.needsRender = true
    }

    if (this.equipment.rollerStart && this.data.motorSpeed > 0) {
      const speed = this.data.motorSpeed / ANIMATION.roller.maxSpeedRatio
      this.equipment.rollerStart.rotation.z += ANIMATION.roller.baseSpeed * speed
      this.equipment.rollerEnd.rotation.z += ANIMATION.roller.baseSpeed * speed
      this.needsRender = true
    }

    if (this.equipment.conveyorProducts && this.data.motorSpeed > 0) {
      const speed = this.data.motorSpeed / ANIMATION.conveyor.maxSpeedRatio
      this.equipment.conveyorProducts.forEach(product => {
        product.position.x += ANIMATION.conveyor.baseSpeed * speed
        if (product.position.x > ANIMATION.conveyor.productResetX) {
          product.position.x = ANIMATION.conveyor.productStartX
        }
      })
      this.needsRender = true
    }

    if (this.equipment.workers) {
      const workerCount = this.equipment.workers.length
      this.equipment.workers.forEach((worker, index) => {
        const offset = index * Math.PI * 2 / workerCount
        const radius = ANIMATION.worker.speed * 25
        worker.position.x = Math.cos(time * ANIMATION.worker.speed + offset) * radius + 10
        worker.position.z = Math.sin(time * ANIMATION.worker.speed + offset) * radius
        worker.rotation.y = time * ANIMATION.worker.rotationSpeed + offset
      })
      this.needsRender = true
    }

    if (this.equipment.flowParticles) {
      updateFlowParticles(this.equipment.flowParticles, this.data.flowRate)
      this.needsRender = true
    }

    if (this.particles.dust) {
      updateParticles(this.particles.dust, this.data)
      this.needsRender = true
    }

    if (this.materialTracker) {
      if (this.materialTracker.needsUpdate) {
        this.needsRender = true
        this.materialTracker.needsUpdate = false
      }
    }
  }

  updateData(data) {
    const oldData = { ...this.data }
    this.data = { ...this.data, ...data }
    this.updateVisuals()

    if (this.data.motorSpeed !== oldData.motorSpeed && this.data.motorSpeed > 0) {
      this.needsRender = true
    }
  }

  updateVisuals() {
    if (this.equipment.tankLevel1) {
      const levelScale = Math.max(0.1, this.data.tankLevel / 100)
      this.equipment.tankLevel1.scale.y = levelScale
      this.equipment.tankLevel1.position.y = 1 + 7.2 * levelScale / 2
    }

    if (this.equipment.reactorIndicator) {
      const temp = this.data.reactorTemp
      let color = 0x36d399
      let intensity = 0.8

      if (temp > 80) {
        color = 0xff4757
        intensity = 1.5
      } else if (temp > 60) {
        color = 0xff9f43
        intensity = 1.2
      } else if (temp > 40) {
        color = 0xffdd00
        intensity = 1
      }

      this.equipment.reactorIndicator.material.color.setHex(color)
      this.equipment.reactorIndicator.material.emissive.setHex(color)
      this.equipment.reactorIndicator.material.emissiveIntensity = intensity
      this.needsRender = true
    }

    if (this.equipment.valve1) {
      const isOpen = this.data.flowRate > 0
      const valveIntensity = isOpen ? 1 : 0.2
      for (let i = 1; i <= 4; i++) {
        const valve = this.equipment[`valve${i}`]
        if (valve && valve.children[0]) {
          valve.children[0].material.emissiveIntensity = valveIntensity
        }
      }
      this.needsRender = true
    }
  }

  setCameraView(view) {
    const viewConfigs = POSITIONS.camera.views
    if (viewConfigs[view]) {
      const { pos, target } = viewConfigs[view]
      this.camera.position.set(...pos)
      this.controls.target.set(...target)
      this.controls.update()
      this.needsRender = true
      this.needsShadowUpdate = true
    }
  }

  updateMaterialTracker(materialStore) {
    if (this.materialTracker) {
      this.materialTracker.updateFromStore(materialStore)
      this.needsRender = true
    }
  }

  highlightMaterialLot(lotId) {
    if (this.materialTracker) {
      this.materialTracker.highlightLot(lotId)
      this.needsRender = true
    }
  }

  getMaterialTracker() {
    return this.materialTracker
  }

  resize() {
    if (!this.container) return

    const width = this.container.clientWidth
    const height = this.container.clientHeight

    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(width, height)
    this.composer.setSize(width, height)

    this.needsRender = true
    this.needsShadowUpdate = true
  }

  dispose() {
    this.isRunning = false

    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
      this.animationId = null
    }

    if (this.controls) {
      this.controls.dispose()
      this.controls = null
    }

    if (this.lights) {
      disposeLights(this.lights)
      this.lights = null
    }

    if (this.composer) {
      this.composer.dispose()
      this.composer = null
    }

    if (this.renderer) {
      this.renderer.dispose()
      this.renderer.forceContextLoss()
      if (this.container && this.renderer.domElement) {
        this.container.removeChild(this.renderer.domElement)
      }
      this.renderer = null
    }

    if (this.scene) {
      this.disposeSceneObjects()
      this.scene.clear()
      this.scene = null
    }

    lodManager.dispose()
    materials.dispose()
    geometries.dispose()

    if (this.materialTracker) {
      this.materialTracker.dispose()
      this.materialTracker = null
    }

    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
      this.resizeObserver = null
    }

    this.equipment = {}
    this.particles = {}
  }

  disposeSceneObjects() {
    const disposeObject = (obj) => {
      if (obj instanceof THREE.Mesh) {
        if (obj.geometry) {
          obj.geometry.dispose()
        }
        if (obj.material) {
          if (Array.isArray(obj.material)) {
            obj.material.forEach(m => m.dispose())
          } else {
            obj.material.dispose()
          }
        }
      }
    }

    const traverseAndDispose = (obj) => {
      if (obj.userData && obj.userData.dispose) {
        obj.userData.dispose()
      }

      if (obj.traverse) {
        obj.traverse(disposeObject)
      } else if (obj.children) {
        obj.children.forEach(child => {
          disposeObject(child)
          if (child.dispose) child.dispose()
        })
      }

      if (obj.dispose) {
        obj.dispose()
      }
    }

    traverseAndDispose(this.scene)
  }
}

export default Plant3D
