import * as THREE from 'three'
import { COLORS, DIMENSIONS } from '../constants.js'
import { materials } from '../materials.js'

export function createFlowParticles(scene) {
  const particleCount = 50
  const geometry = new THREE.BufferGeometry()
  const positions = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = -25 + Math.random() * 40
    positions[i * 3 + 1] = 3 + Math.random() * 2
    positions[i * 3 + 2] = -15 + Math.random() * 5
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))

  const material = new THREE.PointsMaterial({
    color: COLORS.particles.flow,
    size: 0.3,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending
  })

  const particles = new THREE.Points(geometry, material)
  scene.add(particles)

  return particles
}

export function createDustParticles(scene) {
  const particleCount = 200
  const geometry = new THREE.BufferGeometry()
  const positions = new Float32Array(particleCount * 3)
  const velocities = []

  for (let i = 0; i < particleCount; i++) {
    positions[i * 3] = (Math.random() - 0.5) * 80
    positions[i * 3 + 1] = Math.random() * 30
    positions[i * 3 + 2] = (Math.random() - 0.5) * 80
    velocities.push({
      x: (Math.random() - 0.5) * 0.02,
      y: Math.random() * 0.03 + 0.01,
      z: (Math.random() - 0.5) * 0.02
    })
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))

  const material = new THREE.PointsMaterial({
    color: COLORS.particles.dust,
    size: 0.15,
    transparent: true,
    opacity: 0.6,
    blending: THREE.AdditiveBlending
  })

  const particles = new THREE.Points(geometry, material)
  scene.add(particles)

  return { mesh: particles, velocities }
}

export function updateParticles(particles, data) {
  if (!particles.mesh) return

  const positions = particles.mesh.geometry.attributes.position.array
  const velocities = particles.velocities

  for (let i = 0; i < velocities.length; i++) {
    positions[i * 3] += velocities[i].x
    positions[i * 3 + 1] += velocities[i].y
    positions[i * 3 + 2] += velocities[i].z

    if (positions[i * 3 + 1] > 35) {
      positions[i * 3] = (Math.random() - 0.5) * 80
      positions[i * 3 + 1] = 0
      positions[i * 3 + 2] = (Math.random() - 0.5) * 80
    }
  }

  particles.mesh.geometry.attributes.position.needsUpdate = true
}

export function updateFlowParticles(flowParticles, flowRate) {
  if (!flowParticles) return

  const positions = flowParticles.geometry.attributes.position.array
  const flowSpeed = flowRate / 50

  for (let i = 0; i < positions.length; i += 3) {
    positions[i] += 0.1 * flowSpeed
    if (positions[i] > 15) {
      positions[i] = -25
    }
  }

  flowParticles.geometry.attributes.position.needsUpdate = true
  flowParticles.material.opacity = Math.min(1, flowRate / 30)
}
