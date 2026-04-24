export const COLORS = {
  industrial: {
    ground: 0x808080,
    gridMain: 0x606060,
    gridSub: 0x505050,
    white: 0xffffff,
    black: 0x202020,
    gray: 0x808080,
    steel: 0xe8e8e8,
    steelDark: 0xc8c8c8,
    steelLight: 0xd4d4d4
  },
  safety: {
    yellow: 0xffcc00,
    white: 0xffffff,
    hazard: 0xffcc00
  },
  equipment: {
    reactor: 0xe8e8e8,
    tank: 0xe0e0e0,
    pipe: 0xc8c8c8,
    conveyor: 0xc0c0c0,
    structure: 0xb8b8b8,
    valve: 0xe8e8e8,
    valveWheel: 0xd04000,
    insulation: 0x8b7355
  },
  indicators: {
    running: 0x36d399,
    stopped: 0x808080,
    alarm: 0xff4757,
    warning: 0xff9f43,
    caution: 0xffdd00,
    info: 0x54a0ff,
    liquid: 0x00aaff,
    product: 0x36d399
  },
  worker: {
    body: 0x3366cc,
    head: 0xffcc99,
    helmet: 0xffcc00
  },
  lights: {
    ambient: 0xffffff,
    lamp: 0xffffee,
    lampGlow: 0xffffee
  },
  particles: {
    flow: 0x00aaff,
    dust: 0x88aacc
  }
}

export const DIMENSIONS = {
  scene: {
    fogDensity: 0.004,
    groundSize: 200,
    gridSize: 100,
    maxCameraDistance: 120,
    minCameraDistance: 20
  },
  reactor: {
    bodyRadius: 5,
    bodyRadiusBottom: 5.5,
    bodyHeight: 15,
    topDomeRadius: 5,
    rimRadius: 5.2,
    rimTube: 0.35,
    legRadiusTop: 0.6,
    legRadiusBottom: 0.8,
    legHeight: 4,
    nozzleRadius: 0.6,
    nozzleLength: 1.5,
    flangeRadius: 0.9,
    flangeThickness: 0.3,
    indicatorRadius: 0.5,
    sightGlassRadius: 0.35,
    sightGlassLength: 2,
    shaftRadius: 0.3,
    shaftHeight: 12,
    hubRadius: 1,
    hubHeight: 0.8,
    bladeWidth: 6,
    bladeHeight: 0.25,
    bladeDepth: 1.2,
    baffleWidth: 0.25,
    baffleHeight: 10,
    baffleDepth: 0.6,
    supportRingRadius: 6,
    supportRingTube: 0.25
  },
  tank: {
    defaultRadius: 4,
    defaultHeight: 12,
    roofRadiusSegments: 64,
    bodyRadiusSegments: 64,
    bottomRadiusExtra: 0.5,
    bottomThickness: 0.5,
    levelRadiusExtra: 0.2,
    levelHeightRatio: 0.6,
    ladderRailWidth: 0.08,
    ladderRailGap: 0.3,
    platformWidth: 3,
    platformDepth: 2,
    railingHeight: 0.9,
    nameplateWidth: 2,
    nameplateHeight: 0.8
  },
  pipe: {
    mainRadius: 0.5,
    verticalRadius: 0.4,
    flangeRadius: 0.9,
    flangeThickness: 0.3
  },
  valve: {
    bodyRadius: 0.6,
    bodyHeight: 1.5,
    wheelRadius: 0.5,
    wheelTube: 0.08,
    stemRadius: 0.15,
    stemHeight: 0.8
  },
  conveyor: {
    beltWidth: 25,
    beltHeight: 0.25,
    beltDepth: 3,
    sideRailHeight: 0.4,
    sideRailThickness: 0.15,
    legWidth: 0.4,
    legHeight: 3,
    rollerRadius: 0.4,
    drumRadius: 0.8,
    productSize: 1.8
  },
  platform: {
    mainWidth: 8,
    mainDepth: 5,
    height: 8,
    thickness: 0.12,
    railWidth: 0.06,
    railHeight: 1.1,
    ladderWidth: 0.08,
    rungWidth: 0.6,
    rungHeight: 0.05
  },
  structure: {
    columnWidth: 0.6,
    columnHeight: 15,
    beamWidth: 60,
    beamHeight: 0.4,
    beamDepth: 0.4
  },
  worker: {
    bodyRadius: 0.3,
    bodyHeight: 1.2,
    headRadius: 0.25,
    helmetRadius: 0.28,
    legRadius: 0.12,
    legHeight: 0.6,
    walkRadius: 25
  },
  instrument: {
    panelWidth: 4,
    panelHeight: 3,
    panelDepth: 0.25,
    screenWidth: 1.5,
    screenHeight: 1,
    buttonRadius: 0.1,
    buttonHeight: 0.04,
    lightRadius: 0.07
  },
  ceilingLights: {
    poleRadius: 0.15,
    poleHeight: 25,
    lampWidth: 2,
    lampHeight: 0.3,
    lampDepth: 0.6,
    glowWidth: 1.8,
    glowHeight: 0.1,
    lightIntensity: 0.8,
    lightRange: 40
  }
}

export const SEGMENTS = {
  cylinder: 64,
  torus: 64,
  sphere: 64,
  pipe: 32,
  smallCylinder: 32,
  smallSphere: 24,
  rod: 16,
  bolt: 12,
  fine: 48,
  coarse: 16
}

export const POSITIONS = {
  camera: {
    default: { pos: [50, 40, 60], target: [0, 8, 0] },
    views: {
      front: { pos: [0, 20, 70], target: [0, 8, 0] },
      top: { pos: [0, 90, 0.1], target: [0, 0, 0] },
      side: { pos: [70, 20, 0], target: [0, 8, 0] },
      iso: { pos: [45, 35, 50], target: [0, 8, 0] }
    }
  },
  mainLight: { pos: [60, 100, 80] },
  fillLight: { pos: [-60, 80, -60] },
  floorReflectLight: { pos: [0, 1, 0], intensity: 0.3, range: 100 },
  ceilingLights: [
    [-30, 25, -30], [0, 25, -30], [30, 25, -30],
    [-30, 25, 0], [30, 25, 0],
    [-30, 25, 30], [0, 25, 30], [30, 25, 30]
  ],
  tankZones: [
    { x: -20, z: -15, radius: 8 },
    { x: -7, z: -15, radius: 6 },
    { x: 10, z: -15, radius: 7 }
  ],
  tanks: [
    { x: -25, label: 'TK-101', capacity: 100 },
    { x: -10, label: 'TK-102', capacity: 80 },
    { x: 12, label: 'TK-103', capacity: 120 }
  ],
  walkway: { x: 25, z: 0, width: 3, length: 60 },
  columns: [
    [-30, 7.5, -30], [-30, 7.5, 30], [30, 7.5, -30], [30, 7.5, 30],
    [-30, 7.5, -10], [30, 7.5, -10], [-30, 7.5, 10], [30, 7.5, 10]
  ],
  instrumentPanel: { x: 20, y: 2, z: 20 },
  conveyor: { x: 15, y: 0, z: 15 },
  reactor: { x: 0, y: 0, z: 0 }
}

export const MATERIAL_PROPS = {
  metal: {
    roughness: 0.15,
    metalness: 0.95
  },
  steel: {
    roughness: 0.1,
    metalness: 0.98
  },
  roughMetal: {
    roughness: 0.25,
    metalness: 0.9
  },
  plastic: {
    roughness: 0.4,
    metalness: 0.6
  },
  rubber: {
    roughness: 0.9,
    metalness: 0.1
  },
  glass: {
    roughness: 0.05,
    metalness: 0.3,
    transparent: true,
    opacity: 0.4
  },
  emissive: {
    roughness: 0.2,
    metalness: 0.5
  },
  ground: {
    roughness: 0.9,
    metalness: 0.1
  }
}

export const ANIMATION = {
  worker: {
    speed: 0.2,
    rotationSpeed: 0.5
  },
  stirrer: {
    baseSpeed: 0.03,
    maxSpeedRatio: 1500
  },
  roller: {
    baseSpeed: 0.05,
    maxSpeedRatio: 1500
  },
  conveyor: {
    baseSpeed: 0.08,
    maxSpeedRatio: 1500,
    productResetX: 20,
    productStartX: -15
  },
  particles: {
    flowBaseSpeed: 0.1,
    flowResetX: 15,
    flowStartX: -25,
    dustVelocity: { x: 0.02, yMin: 0.01, yMax: 0.04, z: 0.02 }
  }
}

export default {
  COLORS,
  DIMENSIONS,
  SEGMENTS,
  POSITIONS,
  MATERIAL_PROPS,
  ANIMATION
}
