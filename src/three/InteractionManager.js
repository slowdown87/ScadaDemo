import * as THREE from 'three'

export class InteractionManager {
  constructor(camera, domElement, scene, outlinePass = null) {
    this.camera = camera
    this.domElement = domElement
    this.scene = scene
    this.outlinePass = outlinePass

    this.raycaster = new THREE.Raycaster()
    this.mouse = new THREE.Vector2()

    this.selectedObject = null
    this.hoveredObject = null

    this.deviceRegistry = new Map()

    this.onDeviceClick = null
    this.onDeviceHover = null
    this.onDeviceLeave = null
    this.onDeviceDoubleClick = null

    this._boundOnClick = this.onClick.bind(this)
    this._boundOnDoubleClick = this.onDoubleClick.bind(this)
    this._boundOnMouseMove = this.onMouseMove.bind(this)
    this._boundOnTouchStart = this.onTouchStart.bind(this)

    this.lastClickTime = 0
    this.doubleClickDelay = 300

    this.enabled = true
  }

  setOutlinePass(outlinePass) {
    this.outlinePass = outlinePass
  }

  init() {
    this.domElement.addEventListener('click', this._boundOnClick)
    this.domElement.addEventListener('dblclick', this._boundOnDoubleClick)
    this.domElement.addEventListener('mousemove', this._boundOnMouseMove)
    this.domElement.addEventListener('touchstart', this._boundOnTouchStart, { passive: false })
  }

  dispose() {
    this.domElement.removeEventListener('click', this._boundOnClick)
    this.domElement.removeEventListener('dblclick', this._boundOnDoubleClick)
    this.domElement.removeEventListener('mousemove', this._boundOnMouseMove)
    this.domElement.removeEventListener('touchstart', this._boundOnTouchStart)
    this.clearHighlight()
  }

  registerDevice(id, object, data = {}) {
    object.userData.deviceId = id
    object.userData.deviceData = data
    this.deviceRegistry.set(id, { object, data })
  }

  getDeviceObject(id) {
    const device = this.deviceRegistry.get(id)
    return device ? device.object : null
  }

  updateMouse(event) {
    const rect = this.domElement.getBoundingClientRect()
    const clientX = event.clientX || (event.touches && event.touches[0]?.clientX) || 0
    const clientY = event.clientY || (event.touches && event.touches[0]?.clientY) || 0

    this.mouse.x = ((clientX - rect.left) / rect.width) * 2 - 1
    this.mouse.y = -((clientY - rect.top) / rect.height) * 2 + 1
  }

  raycast() {
    this.raycaster.setFromCamera(this.mouse, this.camera)
    const intersects = this.raycaster.intersectObjects(this.scene, true)

    if (intersects.length > 0) {
      let target = intersects[0].object

      while (target && !target.userData.deviceId) {
        target = target.parent
      }

      if (target?.userData.deviceId) {
        return { object: target, point: intersects[0].point, deviceId: target.userData.deviceId }
      }
    }

    return null
  }

  onClick(event) {
    if (!this.enabled) return
    this.updateMouse(event)

    const now = Date.now()
    const isDoubleClick = now - this.lastClickTime < this.doubleClickDelay
    this.lastClickTime = now

    if (isDoubleClick) return

    const hit = this.raycast()
    if (hit) {
      this.selectDevice(hit.deviceId)
      if (this.onDeviceClick) {
        this.onDeviceClick(hit.deviceId, hit.object.userData.deviceData, hit.point)
      }
    } else {
      this.deselectDevice()
    }
  }

  onDoubleClick(event) {
    if (!this.enabled) return
    this.updateMouse(event)

    const hit = this.raycast()
    if (hit) {
      if (this.onDeviceDoubleClick) {
        this.onDeviceDoubleClick(hit.deviceId, hit.object.userData.deviceData, hit.point)
      }
    }
  }

  onMouseMove(event) {
    if (!this.enabled) return
    this.updateMouse(event)

    const hit = this.raycast()
    if (hit) {
      if (this.hoveredObject !== hit.object) {
        this.clearHover()
        this.hoveredObject = hit.object
        this.setHoverHighlight(hit.object)
        if (this.onDeviceHover) {
          this.onDeviceHover(hit.deviceId, hit.object.userData.deviceData)
        }
      }
    } else {
      this.clearHover()
      if (this.hoveredObject && this.onDeviceLeave) {
        this.onDeviceLeave()
      }
    }
  }

  onTouchStart(event) {
    if (!this.enabled) return
    if (event.touches.length === 1) {
      event.preventDefault()
      this.updateMouse(event)
      const hit = this.raycast()
      if (hit) {
        this.selectDevice(hit.deviceId)
        if (this.onDeviceClick) {
          this.onDeviceClick(hit.deviceId, hit.object.userData.deviceData, hit.point)
        }
      } else {
        this.deselectDevice()
      }
    }
  }

  setHoverHighlight(object) {
    if (!object || object === this.selectedObject) return
    if (!this.outlinePass) return

    const deviceObjects = this.getDeviceMeshes(object)
    this.outlinePass.selectedObjects = deviceObjects
    this.outlinePass.visibleEdgeColor.set(0x00aaff)
  }

  clearHover() {
    if (this.hoveredObject && this.hoveredObject !== this.selectedObject) {
      this.hoveredObject = null
      if (this.outlinePass && !this.selectedObject) {
        this.outlinePass.selectedObjects = []
      }
    }
  }

  getDeviceMeshes(object) {
    const meshes = []
    const visited = new Set()

    const collectMeshes = (obj) => {
      if (visited.has(obj)) return
      visited.add(obj)

      if (obj.isMesh && obj.material) {
        meshes.push(obj)
      }
      if (obj.children) {
        obj.children.forEach(collectMeshes)
      }
    }

    collectMeshes(object)
    return meshes
  }

  selectDevice(deviceId) {
    const device = this.deviceRegistry.get(deviceId)
    if (!device) return

    if (this.selectedObject) {
      this.clearHighlight()
    }

    this.selectedObject = device.object

    if (this.outlinePass) {
      const meshes = this.getDeviceMeshes(device.object)
      this.outlinePass.selectedObjects = meshes
      this.outlinePass.visibleEdgeColor.set(0xffcc00)
    }

    device.object.traverse((child) => {
      if (child.isMesh && child !== device.object) {
        child.userData.wasClickable = child.userData.clickable
        child.userData.clickable = true
      }
    })
  }

  deselectDevice() {
    this.clearHighlight()
    this.selectedObject = null
  }

  clearHighlight() {
    if (this.selectedObject) {
      this.selectedObject.traverse((child) => {
        if (child.isMesh) {
          child.userData.clickable = child.userData.wasClickable
        }
      })
      this.selectedObject = null
    }

    if (this.outlinePass) {
      this.outlinePass.selectedObjects = []
    }
  }

  getSelectedDevice() {
    if (!this.selectedObject) return null
    return {
      deviceId: this.selectedObject.userData.deviceId,
      data: this.selectedObject.userData.deviceData
    }
  }
}
