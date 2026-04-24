import * as THREE from 'three'

export class InteractionManager {
  constructor(camera, domElement, scene) {
    this.camera = camera
    this.domElement = domElement
    this.scene = scene

    this.raycaster = new THREE.Raycaster()
    this.mouse = new THREE.Vector2()

    this.selectedObject = null
    this.hoveredObject = null
    this.highlightMaterial = null

    this.deviceRegistry = new Map()

    this.onDeviceClick = null
    this.onDeviceHover = null
    this.onDeviceLeave = null

    this._boundOnClick = this.onClick.bind(this)
    this._boundOnMouseMove = this.onMouseMove.bind(this)
    this._boundOnTouchStart = this.onTouchStart.bind(this)

    this.enabled = true
  }

  init() {
    this.domElement.addEventListener('click', this._boundOnClick)
    this.domElement.addEventListener('mousemove', this._boundOnMouseMove)
    this.domElement.addEventListener('touchstart', this._boundOnTouchStart, { passive: false })
  }

  dispose() {
    this.domElement.removeEventListener('click', this._boundOnClick)
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

    const originalMaterial = object.userData.originalMaterial
    if (!originalMaterial && object.material) {
      object.userData.originalMaterial = object.material
      object.material = object.material.clone()
      object.material.emissive = new THREE.Color(0x00aaff)
      object.material.emissiveIntensity = 0.3
    }
  }

  clearHover() {
    if (this.hoveredObject && this.hoveredObject !== this.selectedObject) {
      const original = this.hoveredObject.userData.originalMaterial
      if (original) {
        this.hoveredObject.material = original
        this.hoveredObject.userData.originalMaterial = null
      }
      this.hoveredObject = null
    }
  }

  selectDevice(deviceId) {
    const device = this.deviceRegistry.get(deviceId)
    if (!device) return

    if (this.selectedObject) {
      this.clearHighlight()
    }

    this.selectedObject = device.object

    const originalMaterial = device.object.userData.originalMaterial
    if (!originalMaterial && device.object.material) {
      device.object.userData.originalMaterial = device.object.material
      device.object.material = device.object.material.clone()
    }

    if (device.object.material) {
      device.object.material.emissive = new THREE.Color(0xffcc00)
      device.object.material.emissiveIntensity = 0.5
    }

    device.object.traverse((child) => {
      if (child !== device.object && child.material) {
        if (!child.userData.selectedOriginalMaterial) {
          child.userData.selectedOriginalMaterial = child.material
          child.material = child.material.clone()
        }
        child.material.emissive = new THREE.Color(0xffcc00)
        child.material.emissiveIntensity = 0.3
      }
    })
  }

  deselectDevice() {
    this.clearHighlight()
    this.selectedObject = null
  }

  clearHighlight() {
    if (this.selectedObject) {
      const device = this.deviceRegistry.get(this.selectedObject.userData.deviceId)
      if (device) {
        this.restoreMaterial(device.object)
        device.object.traverse((child) => {
          if (child !== device.object) {
            const original = child.userData.selectedOriginalMaterial
            if (original) {
              child.material = original
              child.userData.selectedOriginalMaterial = null
            }
          }
        })
      }
      this.selectedObject = null
    }
  }

  restoreMaterial(object) {
    const original = object.userData.originalMaterial
    if (original) {
      object.material = original
      object.userData.originalMaterial = null
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
