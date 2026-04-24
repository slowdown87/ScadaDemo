import * as THREE from 'three'
import { DIMENSIONS, SEGMENTS } from './constants.js'

class GeometryLibrary {
  constructor() {
    this._geometries = new Map()
  }

  get(key) {
    return this._geometries.get(key)
  }

  has(key) {
    return this._geometries.has(key)
  }

  set(key, geometry) {
    this._geometries.set(key, geometry)
  }

  cylinder(rt, rb, h, rs = SEGMENTS.cylinder, hs = 1) {
    const key = `cyl_${rt}_${rb}_${h}_${rs}_${hs}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.CylinderGeometry(rt, rb, h, rs, hs)
    this.set(key, geometry)
    return geometry
  }

  sphere(r, ws = SEGMENTS.sphere, hs = SEGMENTS.sphere) {
    const key = `sph_${r}_${ws}_${hs}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.SphereGeometry(r, ws, hs)
    this.set(key, geometry)
    return geometry
  }

  halfSphere(r, ws = SEGMENTS.sphere, hs = SEGMENTS.sphere / 2) {
    const key = `hsph_${r}_${ws}_${hs}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.SphereGeometry(r, ws, hs, 0, Math.PI * 2, 0, Math.PI / 2)
    this.set(key, geometry)
    return geometry
  }

  box(w, h, d) {
    const key = `box_${w}_${h}_${d}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.BoxGeometry(w, h, d)
    this.set(key, geometry)
    return geometry
  }

  torus(r, t, rs = SEGMENTS.torus, ts = SEGMENTS.torus) {
    const key = `tor_${r}_${t}_${rs}_${ts}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.TorusGeometry(r, t, rs, ts)
    this.set(key, geometry)
    return geometry
  }

  ring(inR, outR, s = SEGMENTS.fine) {
    const key = `ring_${inR}_${outR}_${s}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.RingGeometry(inR, outR, s)
    this.set(key, geometry)
    return geometry
  }

  plane(size) {
    const key = `plane_${size}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.PlaneGeometry(size, size)
    this.set(key, geometry)
    return geometry
  }

  planeRect(w, h) {
    const key = `planeRect_${w}_${h}`
    if (this.has(key)) return this.get(key)
    const geometry = new THREE.PlaneGeometry(w, h)
    this.set(key, geometry)
    return geometry
  }

  createReactorBody() {
    const { bodyRadius, bodyRadiusBottom, bodyHeight } = DIMENSIONS.reactor
    const geo = new THREE.Group()

    const body = new THREE.Mesh(
      this.cylinder(bodyRadius, bodyRadiusBottom, bodyHeight, SEGMENTS.cylinder),
      null
    )
    body.position.y = bodyHeight / 2
    body.userData.castShadow = true
    body.userData.receiveShadow = true
    geo.add(body)

    return geo
  }

  createTankBody(radius, height) {
    const geo = new THREE.Group()

    const body = new THREE.Mesh(
      this.cylinder(radius, radius, height, SEGMENTS.cylinder),
      null
    )
    body.position.y = height / 2
    body.userData.castShadow = true
    body.userData.receiveShadow = true
    geo.add(body)

    const roof = new THREE.Mesh(
      this.halfSphere(radius),
      null
    )
    roof.position.y = height
    roof.userData.castShadow = true
    geo.add(roof)

    return geo
  }

  createPipe(radius, height, radialSegments = SEGMENTS.pipe) {
    return this.cylinder(radius, radius, height, radialSegments)
  }

  dispose() {
    this._geometries.forEach(geometry => {
      geometry.dispose()
    })
    this._geometries.clear()
  }
}

export const geometries = new GeometryLibrary()

export default geometries
