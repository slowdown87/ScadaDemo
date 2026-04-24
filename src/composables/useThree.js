import { ref, shallowRef, onMounted, onUnmounted, type Ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

export function useThree(options) {
  const { container, antialias = true, alpha = true, shadowMapEnabled = true } = options

  const scene = shallowRef(null)
  const camera = shallowRef(null)
  const renderer = shallowRef(null)
  const controls = shallowRef(null)

  let animationId = null
  let isDisposed = false

  function initScene() {
    if (!container.value) {
      console.warn('[useThree] Container is null')
      return
    }

    scene.value = new THREE.Scene()
    if (alpha) {
      scene.value.background = null
    }

    camera.value = new THREE.PerspectiveCamera(
      60,
      container.value.clientWidth / container.value.clientHeight,
      0.1,
      1000
    )
    camera.value.position.set(0, 10, 20)

    renderer.value = new THREE.WebGLRenderer({
      antialias,
      alpha,
      powerPreference: 'high-performance'
    })
    renderer.value.setSize(container.value.clientWidth, container.value.clientHeight)
    renderer.value.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    container.value.appendChild(renderer.value.domElement)

    if (shadowMapEnabled) {
      renderer.value.shadowMap.enabled = true
      renderer.value.shadowMap.type = THREE.PCFSoftShadowMap
    }

    controls.value = new OrbitControls(camera.value, renderer.value.domElement)
    controls.value.enableDamping = true
    controls.value.dampingFactor = 0.05
  }

  function startRenderLoop(renderCallback) {
    if (isDisposed) return

    const animate = () => {
      animationId = requestAnimationFrame(animate)

      if (controls.value) {
        controls.value.update()
      }

      if (renderCallback) {
        renderCallback()
      }

      if (renderer.value && scene.value && camera.value) {
        renderer.value.render(scene.value, camera.value)
      }
    }

    animate()
  }

  function handleResize() {
    if (!container.value || !camera.value || !renderer.value) return

    camera.value.aspect = container.value.clientWidth / container.value.clientHeight
    camera.value.updateProjectionMatrix()
    renderer.value.setSize(container.value.clientWidth, container.value.clientHeight)
  }

  function dispose() {
    isDisposed = true

    if (animationId !== null) {
      cancelAnimationFrame(animationId)
    }

    if (controls.value) {
      controls.value.dispose()
    }

    if (renderer.value) {
      renderer.value.dispose()
      renderer.value.forceContextLoss()
      if (container.value && renderer.value.domElement) {
        container.value.removeChild(renderer.value.domElement)
      }
    }

    scene.value?.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.geometry?.dispose()
        if (Array.isArray(object.material)) {
          object.material.forEach(m => m.dispose())
        } else {
          object.material?.dispose()
        }
      }
    })

    scene.value?.clear()
    scene.value = null
    camera.value = null
    renderer.value = null
    controls.value = null
  }

  onMounted(() => {
    initScene()
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    dispose()
    window.removeEventListener('resize', handleResize)
  })

  return {
    scene,
    camera,
    renderer,
    controls,
    startRenderLoop,
    dispose
  }
}
