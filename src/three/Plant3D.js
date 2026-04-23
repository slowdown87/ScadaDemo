import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

export class Plant3D {
  constructor(container) {
    this.container = container
    this.scene = null
    this.camera = null
    this.renderer = null
    this.controls = null
    this.equipment = {}
    this.animationId = null
    this.isRunning = false
    this.data = {
      tankLevel: 50,
      flowRate: 0,
      reactorTemp: 25,
      reactorPressure: 1.0,
      motorSpeed: 0,
      productCount: 0
    }
  }

  init() {
    this.setupScene()
    this.setupCamera()
    this.setupRenderer()
    this.setupControls()
    this.setupLights()
    this.createFactory()
    this.animate()
  }

  setupScene() {
    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x0a0e17)
    this.scene.fog = new THREE.Fog(0x0a0e17, 50, 150)
  }

  setupCamera() {
    const aspect = this.container.clientWidth / this.container.clientHeight
    this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000)
    this.camera.position.set(30, 25, 40)
    this.camera.lookAt(0, 0, 0)
  }

  setupRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    })
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight)
    this.renderer.setPixelRatio(window.devicePixelRatio)
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.container.appendChild(this.renderer.domElement)
  }

  setupControls() {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableDamping = true
    this.controls.dampingFactor = 0.05
    this.controls.maxDistance = 100
    this.controls.minDistance = 15
    this.controls.maxPolarAngle = Math.PI / 2.1
  }

  setupLights() {
    const ambientLight = new THREE.AmbientLight(0x404060, 0.5)
    this.scene.add(ambientLight)

    const mainLight = new THREE.DirectionalLight(0x00aaff, 1)
    mainLight.position.set(20, 30, 20)
    mainLight.castShadow = true
    mainLight.shadow.mapSize.width = 2048
    mainLight.shadow.mapSize.height = 2048
    this.scene.add(mainLight)

    const fillLight = new THREE.DirectionalLight(0x00ffee, 0.3)
    fillLight.position.set(-10, 10, -10)
    this.scene.add(fillLight)

    const pointLight1 = new THREE.PointLight(0x00aaff, 0.5, 50)
    pointLight1.position.set(0, 15, 0)
    this.scene.add(pointLight1)

    const pointLight2 = new THREE.PointLight(0xff4757, 0.3, 30)
    pointLight2.position.set(-15, 5, 10)
    this.scene.add(pointLight2)
  }

  createFactory() {
    this.createFloor()
    this.createReactor()
    this.createTanks()
    this.createPipes()
    this.createConveyor()
    this.createGrid()
  }

  createFloor() {
    const floorGeometry = new THREE.PlaneGeometry(100, 100)
    const floorMaterial = new THREE.MeshStandardMaterial({
      color: 0x121826,
      roughness: 0.8,
      metalness: 0.2
    })
    const floor = new THREE.Mesh(floorGeometry, floorMaterial)
    floor.rotation.x = -Math.PI / 2
    floor.position.y = 0
    floor.receiveShadow = true
    this.scene.add(floor)
  }

  createGrid() {
    const gridHelper = new THREE.GridHelper(100, 50, 0x00aaff, 0x1a2535)
    gridHelper.position.y = 0.01
    this.scene.add(gridHelper)
  }

  createReactor() {
    const reactorGroup = new THREE.Group()
    reactorGroup.position.set(0, 0, 0)

    const bodyGeometry = new THREE.CylinderGeometry(6, 6, 12, 32)
    const bodyMaterial = new THREE.MeshStandardMaterial({
      color: 0x3a4f6f,
      roughness: 0.3,
      metalness: 0.7
    })
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
    body.position.y = 6
    body.castShadow = true
    reactorGroup.add(body)

    const topGeometry = new THREE.SphereGeometry(6, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)
    const top = new THREE.Mesh(topGeometry, bodyMaterial)
    top.position.y = 12
    top.castShadow = true
    reactorGroup.add(top)

    const bottomGeometry = new THREE.SphereGeometry(6, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2)
    const bottom = new THREE.Mesh(bottomGeometry, bodyMaterial)
    bottom.position.y = 0
    bottom.castShadow = true
    reactorGroup.add(bottom)

    const rimGeometry = new THREE.TorusGeometry(6, 0.3, 16, 32)
    const rimMaterial = new THREE.MeshStandardMaterial({
      color: 0x00aaff,
      emissive: 0x00aaff,
      emissiveIntensity: 0.3
    })
    const rim = new THREE.Mesh(rimGeometry, rimMaterial)
    rim.position.y = 12
    rim.rotation.x = Math.PI / 2
    reactorGroup.add(rim)

    const stirrerGroup = new THREE.Group()
    stirrerGroup.position.y = 10
    this.equipment.stirrer = stirrerGroup
    reactorGroup.add(stirrerGroup)

    const bladeGeometry = new THREE.BoxGeometry(8, 0.3, 1)
    const bladeMaterial = new THREE.MeshStandardMaterial({
      color: 0x00ffee,
      emissive: 0x00ffee,
      emissiveIntensity: 0.5
    })
    const blade1 = new THREE.Mesh(bladeGeometry, bladeMaterial)
    stirrerGroup.add(blade1)

    const blade2 = new THREE.Mesh(bladeGeometry, bladeMaterial)
    blade2.rotation.y = Math.PI / 2
    stirrerGroup.add(blade2)

    const indicatorGeometry = new THREE.BoxGeometry(0.5, 0.5, 0.5)
    const indicatorMaterial = new THREE.MeshStandardMaterial({
      color: 0x36d399,
      emissive: 0x36d399,
      emissiveIntensity: 0.8
    })
    const indicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial)
    indicator.position.set(7, 8, 0)
    reactorGroup.add(indicator)
    this.equipment.reactorIndicator = indicator

    this.scene.add(reactorGroup)
    this.equipment.reactor = reactorGroup
  }

  createTanks() {
    const tankGroup = new THREE.Group()
    tankGroup.position.set(-20, 0, 0)

    const tankGeometry = new THREE.CylinderGeometry(4, 4, 10, 32)
    const tankMaterial = new THREE.MeshStandardMaterial({
      color: 0x2a3f5f,
      roughness: 0.3,
      metalness: 0.6
    })

    const tank1 = new THREE.Mesh(tankGeometry, tankMaterial)
    tank1.position.set(0, 5, 0)
    tank1.castShadow = true
    tankGroup.add(tank1)

    const tank2 = new THREE.Mesh(tankGeometry, tankMaterial.clone())
    tank2.position.set(15, 5, 0)
    tank2.castShadow = true
    tankGroup.add(tank2)

    const tank3 = new THREE.Mesh(tankGeometry.clone(), tankMaterial.clone())
    tank3.position.set(30, 5, 0)
    tank3.castShadow = true
    tankGroup.add(tank3)

    const capGeometry = new THREE.SphereGeometry(4, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2)
    const capMaterial = new THREE.MeshStandardMaterial({
      color: 0x3a4f6f,
      roughness: 0.3,
      metalness: 0.7
    })

    const cap1 = new THREE.Mesh(capGeometry, capMaterial)
    cap1.position.set(0, 10, 0)
    tankGroup.add(cap1)

    const cap2 = new THREE.Mesh(capGeometry.clone(), capMaterial.clone())
    cap2.position.set(15, 10, 0)
    tankGroup.add(cap2)

    const cap3 = new THREE.Mesh(capGeometry.clone(), capMaterial.clone())
    cap3.position.set(30, 10, 0)
    tankGroup.add(cap3)

    const levelGeometry = new THREE.CylinderGeometry(3.5, 3.5, 6, 32, 1, true)
    const levelMaterial = new THREE.MeshStandardMaterial({
      color: 0x00aaff,
      transparent: true,
      opacity: 0.4,
      side: THREE.DoubleSide
    })
    const level1 = new THREE.Mesh(levelGeometry, levelMaterial)
    level1.position.set(0, 4, 0)
    tankGroup.add(level1)
    this.equipment.tankLevel1 = level1

    const level2 = new THREE.Mesh(levelGeometry.clone(), levelMaterial.clone())
    level2.position.set(15, 4, 0)
    tankGroup.add(level2)
    this.equipment.tankLevel2 = level2

    const level3 = new THREE.Mesh(levelGeometry.clone(), levelMaterial.clone())
    level3.position.set(30, 4, 0)
    tankGroup.add(level3)
    this.equipment.tankLevel3 = level3

    this.scene.add(tankGroup)
    this.equipment.tanks = tankGroup
  }

  createPipes() {
    const pipeGroup = new THREE.Group()

    const pipeMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a5568,
      roughness: 0.4,
      metalness: 0.6
    })

    const pipeGeometry = new THREE.CylinderGeometry(0.3, 0.3, 15, 16)
    const pipe1 = new THREE.Mesh(pipeGeometry, pipeMaterial)
    pipe1.rotation.z = Math.PI / 2
    pipe1.position.set(-10, 8, 0)
    pipeGroup.add(pipe1)

    const pipe2 = new THREE.Mesh(pipeGeometry.clone(), pipeMaterial.clone())
    pipe2.rotation.z = Math.PI / 2
    pipe2.position.set(7.5, 8, 0)
    pipeGroup.add(pipe2)

    const pipe3 = new THREE.Mesh(pipeGeometry.clone(), pipeMaterial.clone())
    pipe3.rotation.z = Math.PI / 2
    pipe3.position.set(22.5, 8, 0)
    pipeGroup.add(pipe3)

    const verticalPipeGeometry = new THREE.CylinderGeometry(0.3, 0.3, 6, 16)
    const verticalPipe1 = new THREE.Mesh(verticalPipeGeometry, pipeMaterial.clone())
    verticalPipe1.position.set(-10, 2, 0)
    pipeGroup.add(verticalPipe1)

    const verticalPipe2 = new THREE.Mesh(verticalPipeGeometry.clone(), pipeMaterial.clone())
    verticalPipe2.position.set(7.5, 2, 0)
    pipeGroup.add(verticalPipe2)

    const verticalPipe3 = new THREE.Mesh(verticalPipeGeometry.clone(), pipeMaterial.clone())
    verticalPipe3.position.set(22.5, 2, 0)
    pipeGroup.add(verticalPipe3)

    const valveGeometry = new THREE.BoxGeometry(1.5, 1.5, 1.5)
    const valveMaterial = new THREE.MeshStandardMaterial({
      color: 0xf39c12,
      emissive: 0xf39c12,
      emissiveIntensity: 0.3
    })

    const valve1 = new THREE.Mesh(valveGeometry, valveMaterial)
    valve1.position.set(-10, 5, 0)
    pipeGroup.add(valve1)
    this.equipment.valve1 = valve1

    const valve2 = new THREE.Mesh(valveGeometry.clone(), valveMaterial.clone())
    valve2.position.set(7.5, 5, 0)
    pipeGroup.add(valve2)
    this.equipment.valve2 = valve2

    const valve3 = new THREE.Mesh(valveGeometry.clone(), valveMaterial.clone())
    valve3.position.set(22.5, 5, 0)
    pipeGroup.add(valve3)
    this.equipment.valve3 = valve3

    this.scene.add(pipeGroup)
    this.equipment.pipes = pipeGroup
  }

  createConveyor() {
    const conveyorGroup = new THREE.Group()
    conveyorGroup.position.set(15, 0, 15)

    const beltGeometry = new THREE.BoxGeometry(20, 0.5, 3)
    const beltMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a2535,
      roughness: 0.9
    })
    const belt = new THREE.Mesh(beltGeometry, beltMaterial)
    belt.position.y = 2
    conveyorGroup.add(belt)

    const legGeometry = new THREE.BoxGeometry(0.5, 2, 0.5)
    const legMaterial = new THREE.MeshStandardMaterial({
      color: 0x4a5568
    })

    const positions = [[-9, 1, 0], [9, 1, 0], [-9, 1, 2], [9, 1, 2]]
    positions.forEach(pos => {
      const leg = new THREE.Mesh(legGeometry, legMaterial)
      leg.position.set(...pos)
      conveyorGroup.add(leg)
    })

    const rollerGeometry = new THREE.CylinderGeometry(0.4, 0.4, 3, 16)
    const rollerMaterial = new THREE.MeshStandardMaterial({
      color: 0x3a4f6f,
      metalness: 0.8
    })

    for (let i = -8; i <= 8; i += 2) {
      const roller = new THREE.Mesh(rollerGeometry, rollerMaterial)
      roller.rotation.x = Math.PI / 2
      roller.position.set(i, 2.5, 0)
      conveyorGroup.add(roller)
      if (i === -8 || i === 8) {
        this.equipment[`roller${i === -8 ? 'Start' : 'End'}`] = roller
      }
    }

    const productGeometry = new THREE.BoxGeometry(1.5, 1.5, 1.5)
    const productMaterial = new THREE.MeshStandardMaterial({
      color: 0x36d399,
      emissive: 0x36d399,
      emissiveIntensity: 0.3
    })
    const product = new THREE.Mesh(productGeometry, productMaterial)
    product.position.set(-8, 4, 0)
    product.castShadow = true
    conveyorGroup.add(product)
    this.equipment.product = product

    this.scene.add(conveyorGroup)
    this.equipment.conveyor = conveyorGroup
  }

  updateData(data) {
    this.data = { ...this.data, ...data }
    this.updateVisuals()
  }

  updateVisuals() {
    if (this.equipment.tankLevel1) {
      const levelScale = this.data.tankLevel / 100
      this.equipment.tankLevel1.scale.y = levelScale
      this.equipment.tankLevel1.position.y = 1 + 6 * levelScale / 2
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
        intensity = 1
      }
      this.equipment.reactorIndicator.material.color.setHex(color)
      this.equipment.reactorIndicator.material.emissive.setHex(color)
      this.equipment.reactorIndicator.material.emissiveIntensity = intensity
    }

    if (this.equipment.valve1) {
      const isOpen = this.data.flowRate > 0
      this.equipment.valve1.material.emissiveIntensity = isOpen ? 0.8 : 0.2
      this.equipment.valve2.material.emissiveIntensity = isOpen ? 0.8 : 0.2
      this.equipment.valve3.material.emissiveIntensity = isOpen ? 0.8 : 0.2
    }

    if (this.equipment.product && this.data.motorSpeed > 0) {
      const pos = this.equipment.product.position.x
      const newPos = pos > 8 ? -8 : pos + 0.02
      this.equipment.product.position.x = newPos
    }
  }

  animate() {
    this.animationId = requestAnimationFrame(() => this.animate())

    if (this.equipment.stirrer && this.data.motorSpeed > 0) {
      this.equipment.stirrer.rotation.y += 0.05 * (this.data.motorSpeed / 1500)
    }

    if (this.equipment.rollerStart && this.data.motorSpeed > 0) {
      this.equipment.rollerStart.rotation.z += 0.1 * (this.data.motorSpeed / 1500)
      this.equipment.rollerEnd.rotation.z += 0.1 * (this.data.motorSpeed / 1500)
    }

    this.controls.update()
    this.renderer.render(this.scene, this.camera)
  }

  setCameraView(view) {
    const views = {
      front: { pos: [0, 15, 50], target: [0, 5, 0] },
      top: { pos: [0, 60, 0.1], target: [0, 0, 0] },
      side: { pos: [50, 15, 0], target: [0, 5, 0] },
      iso: { pos: [30, 25, 40], target: [0, 5, 0] }
    }

    if (views[view]) {
      const { pos, target } = views[view]
      this.camera.position.set(...pos)
      this.controls.target.set(...target)
      this.controls.update()
    }
  }

  resize() {
    if (!this.container) return
    const width = this.container.clientWidth
    const height = this.container.clientHeight
    this.camera.aspect = width / height
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(width, height)
  }

  dispose() {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
    }
    if (this.renderer) {
      this.renderer.dispose()
      this.container.removeChild(this.renderer.domElement)
    }
  }
}

export default Plant3D
