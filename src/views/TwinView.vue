<template>
  <div class="twin-container">
    <SideNav />
    <main class="main-content">
      <header class="top-bar">
        <div class="header-left">
          <h1 class="page-title">◆ 数字孪生系统</h1>
          <span class="page-subtitle">方案B - Three.js 3D可视化</span>
        </div>
        <div class="header-right">
          <div class="view-controls">
            <button
              v-for="view in viewOptions"
              :key="view.key"
              :class="['view-btn', { active: currentView === view.key }]"
              @click="setView(view.key)"
            >
              {{ view.label }}
            </button>
          </div>
        </div>
      </header>

      <div class="twin-content">
        <div class="scene-container" ref="sceneContainer">
          <div class="loading-overlay" v-if="loading">
            <div class="loader"></div>
            <span>加载3D场景...</span>
          </div>
          <DevicePanel
            :visible="showDevicePanel"
            :device="selectedDevice"
            @close="closeDevicePanel"
            @control="handleDeviceControl"
          />
        </div>

        <div class="data-sidebar">
          <div class="data-panel">
            <div class="panel-header">
              <span>◆ 实时数据</span>
            </div>
            <div class="data-list">
              <div class="data-row">
                <span class="data-label">液位</span>
                <span class="data-value">{{ tankLevel }}%</span>
              </div>
              <div class="data-row">
                <span class="data-label">流量</span>
                <span class="data-value">{{ flowRate }} L/s</span>
              </div>
              <div class="data-row" :class="{ danger: reactorTemp > 80 }">
                <span class="data-label">温度</span>
                <span class="data-value">{{ reactorTemp }}°C</span>
              </div>
              <div class="data-row" :class="{ danger: reactorPressure > 1.5 }">
                <span class="data-label">压力</span>
                <span class="data-value">{{ reactorPressure }} atm</span>
              </div>
              <div class="data-row">
                <span class="data-label">电机</span>
                <span class="data-value">{{ motorSpeed }} RPM</span>
              </div>
              <div class="data-row">
                <span class="data-label">产量</span>
                <span class="data-value">{{ productCount }}</span>
              </div>
            </div>
          </div>

          <div class="control-panel">
            <div class="panel-header">
              <span>◆ 控制</span>
            </div>
            <div class="control-buttons">
              <button class="ctrl-btn start" :disabled="isRunning" @click="handleStart">
                <span>▶ 启动</span>
              </button>
              <button class="ctrl-btn stop" :disabled="!isRunning" @click="handleStop">
                <span>■ 停止</span>
              </button>
              <button class="ctrl-btn reset" @click="handleReset">
                <span>↻ 复位</span>
              </button>
            </div>
          </div>

          <MaterialPanel />

          <AlarmPanel
            v-if="hasAlarms || alarmHistory.length > 0"
            :alarms="alarms"
            :alarm-history="alarmHistory"
            :sound-enabled="soundEnabled"
            @acknowledge="handleAcknowledge"
            @acknowledge-all="handleAcknowledgeAll"
            @toggle-sound="toggleSound"
            @export-history="handleExportHistory"
          />

          <div class="info-panel">
            <div class="panel-header">
              <span>◆ 操作提示</span>
            </div>
            <ul class="tips-list">
              <li>鼠标左键：旋转视角</li>
              <li>鼠标右键：平移视角</li>
              <li>滚轮：缩放</li>
              <li>点击右上角按钮：切换视角</li>
              <li class="tip-highlight">点击设备：查看详情</li>
            </ul>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import * as THREE from 'three'
import { usePlantStore } from '@/stores/plantStore'
import { useAlarmStore } from '@/stores/alarmStore'
import { useMaterialStore } from '@/stores/materialStore'
import { useAlarmSound } from '@/composables/useAlarmSound'
import { Plant3D } from '@/three/Plant3D'
import { InteractionManager } from '@/three/InteractionManager'
import DevicePanel from '@/components/DevicePanel.vue'
import AlarmPanel from '@/components/AlarmPanel.vue'
import MaterialPanel from '@/components/MaterialPanel.vue'
import SideNav from '@/components/SideNav.vue'

const store = usePlantStore()
const alarmStore = useAlarmStore()
const materialStore = useMaterialStore()
const { playCriticalAlarm, playWarningAlarm, isEnabled: soundEnabled, toggle: toggleSound } = useAlarmSound()
const sceneContainer = ref(null)
const loading = ref(true)
const currentView = ref('iso')

const showDevicePanel = ref(false)
const selectedDevice = ref(null)

let plant3D = null
let interactionManager = null
let dataUpdateInterval = null

const viewOptions = [
  { key: 'front', label: '正面' },
  { key: 'top', label: '顶部' },
  { key: 'side', label: '侧面' },
  { key: 'iso', label: '等轴' }
]

const isRunning = computed(() => store.running)
const tankLevel = computed(() => store.tankLevel.toFixed(1))
const flowRate = computed(() => store.flowRate.toFixed(1))
const reactorTemp = computed(() => store.reactorTemp.toFixed(1))
const reactorPressure = computed(() => store.reactorPressure.toFixed(2))
const motorSpeed = computed(() => store.motorSpeed)
const productCount = computed(() => store.productCount)
const alarms = computed(() => store.alarms)
const alarmHistory = computed(() => store.alarmHistory)
const hasAlarms = computed(() => store.hasAlarms)

function setView(view) {
  currentView.value = view
  if (plant3D) {
    plant3D.setCameraView(view)
  }
}

function handleStart() {
  store.start()
}

function handleStop() {
  store.stop()
}

function handleReset() {
  store.reset()
}

function handleAcknowledge(alarmId) {
  store.acknowledgeAlarm(alarmId)
}

function handleAcknowledgeAll() {
  store.acknowledgeAll()
}

function handleExportHistory() {
  const data = alarmStore.exportHistory()
  const csv = [
    ['ID', '设备', '等级', '代码', '消息', '值', '阈值', '时间', '已确认', '确认人', '确认时间'].join(','),
    ...data.map(row => [
      row.id,
      row.deviceId,
      row.levelName,
      row.code,
      `"${row.message}"`,
      row.value,
      row.threshold,
      row.timestamp,
      row.acknowledged ? '是' : '否',
      row.acknowledgedBy || '',
      row.acknowledgedAt || ''
    ].join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `alarm_history_${new Date().toISOString().slice(0, 10)}.csv`
  link.click()
  URL.revokeObjectURL(url)
}

function closeDevicePanel() {
  showDevicePanel.value = false
  if (interactionManager) {
    interactionManager.deselectDevice()
  }
}

function handleDeviceControl(control) {
  if (control.type === 'start') {
    store.start()
  } else if (control.type === 'stop') {
    store.stop()
  }
}

function update3DScene() {
  if (plant3D) {
    plant3D.updateData({
      tankLevel: store.tankLevel,
      flowRate: store.flowRate,
      reactorTemp: store.reactorTemp,
      reactorPressure: store.reactorPressure,
      motorSpeed: store.motorSpeed,
      productCount: store.productCount
    })
    plant3D.updateMaterialTracker(materialStore)
  }

  if (showDevicePanel.value && selectedDevice.value) {
    const deviceId = selectedDevice.value.id
    let history = []

    if (deviceId === 'R-101') {
      history = store.temperatureHistory.slice(-30)
    } else if (deviceId.startsWith('TK')) {
      history = store.levelHistory.slice(-30)
    }

    selectedDevice.value = {
      ...selectedDevice.value,
      data: {
        temp: store.reactorTemp,
        pressure: store.reactorPressure,
        level: store.tankLevel,
        speed: store.motorSpeed,
        products: store.productCount,
        running: store.running,
        alarm: store.alarms.some(a => a.level === 'critical')
      },
      history
    }
  }
}

function setupInteraction() {
  if (!plant3D || !sceneContainer.value) return

  interactionManager = new InteractionManager(
    plant3D.camera,
    sceneContainer.value,
    plant3D.scene,
    plant3D.outlinePass
  )

  interactionManager.registerDevice('R-101', plant3D.equipment.reactor, {
    type: 'reactor',
    name: '反应釜 R-101'
  })

  interactionManager.registerDevice('TK-101', plant3D.equipment.tanks, {
    type: 'tank',
    name: '储罐 TK-101'
  })

  interactionManager.registerDevice('CONV-01', plant3D.equipment.conveyor, {
    type: 'conveyor',
    name: '传送带'
  })

  interactionManager.onDeviceClick = (deviceId, deviceData, point) => {
    let history = []
    let type = 'reactor'

    if (deviceId === 'R-101') {
      history = store.temperatureHistory.slice(-30)
      type = 'reactor'
    } else if (deviceId.startsWith('TK')) {
      history = store.levelHistory.slice(-30)
      type = 'tank'
    } else if (deviceId === 'CONV-01') {
      type = 'conveyor'
    }

    selectedDevice.value = {
      id: deviceId,
      type,
      data: {
        temp: store.reactorTemp,
        pressure: store.reactorPressure,
        level: store.tankLevel,
        speed: store.motorSpeed,
        products: store.productCount,
        running: store.running,
        alarm: store.alarms.some(a => a.level === 'critical')
      },
      history
    }
    showDevicePanel.value = true
  }

  interactionManager.onDeviceDoubleClick = (deviceId, deviceData, point) => {
    focusCameraOnDevice(deviceId)
  }

  interactionManager.init()
}

function focusCameraOnDevice(deviceId) {
  if (!plant3D || !interactionManager) return

  const deviceObject = interactionManager.getDeviceObject(deviceId)
  if (!deviceObject) return

  const box = new THREE.Box3().setFromObject(deviceObject)
  const center = box.getCenter(new THREE.Vector3())
  const size = box.getSize(new THREE.Vector3())
  const maxDim = Math.max(size.x, size.y, size.z)

  const distance = maxDim * 2.5
  const direction = new THREE.Vector3()
    .subVectors(plant3D.camera.position, center)
    .normalize()

  const targetPosition = center.clone().add(direction.multiplyScalar(distance))

  animateCameraTo(targetPosition, center)
}

function animateCameraTo(targetPosition, targetLookAt) {
  if (!plant3D || !plant3D.controls) return

  const startPosition = plant3D.camera.position.clone()
  const startTarget = plant3D.controls.target.clone()
  const duration = 800
  const startTime = Date.now()

  function animate() {
    const elapsed = Date.now() - startTime
    const progress = Math.min(elapsed / duration, 1)

    const easeProgress = 1 - Math.pow(1 - progress, 3)

    plant3D.camera.position.lerpVectors(startPosition, targetPosition, easeProgress)
    plant3D.controls.target.lerpVectors(startTarget, targetLookAt, easeProgress)
    plant3D.controls.update()

    if (progress < 1) {
      requestAnimationFrame(animate)
    }
  }

  animate()
}

onMounted(async () => {
  store.initStore()
  materialStore.initializeDemoLots()

  alarmStore.setOnAlarmCallback((level) => {
    if (level >= 5) {
      playCriticalAlarm()
    } else if (level >= 4) {
      playWarningAlarm()
    }
  })

  await new Promise(resolve => setTimeout(resolve, 100))

  if (sceneContainer.value) {
    plant3D = new Plant3D(sceneContainer.value)
    plant3D.init()
    loading.value = false

    setupInteraction()
    dataUpdateInterval = setInterval(update3DScene, 100)
  }
})

onUnmounted(() => {
  if (dataUpdateInterval) {
    clearInterval(dataUpdateInterval)
  }
  if (interactionManager) {
    interactionManager.dispose()
  }
  if (plant3D) {
    plant3D.dispose()
  }
  store.cleanup()
})
</script>

<style scoped>
.twin-container {
  display: flex;
  flex: 1;
  min-height: 0;
  background: var(--color-bg);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: hidden;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.3);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-primary);
  letter-spacing: 3px;
  margin: 0;
  text-shadow: 0 0 20px rgba(0, 170, 255, 0.4);
}

.page-subtitle {
  font-size: 12px;
  color: var(--color-text-dim);
  letter-spacing: 1px;
}

.header-right {
  display: flex;
  align-items: center;
}

.view-controls {
  display: flex;
  gap: 8px;
  background: rgba(26, 34, 53, 0.8);
  padding: 5px;
  border-radius: 8px;
  border: 1px solid rgba(0, 170, 255, 0.2);
}

.view-btn {
  background: transparent;
  border: none;
  color: var(--color-text-dim);
  padding: 8px 16px;
  border-radius: 5px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.view-btn:hover {
  background: rgba(0, 170, 255, 0.1);
  color: var(--color-text);
}

.view-btn.active {
  background: rgba(0, 170, 255, 0.2);
  color: var(--color-primary);
}

.twin-content {
  flex: 1;
  display: flex;
  gap: 20px;
  overflow: hidden;
  min-height: 0;
}

.scene-container {
  flex: 1;
  position: relative;
  background: rgba(10, 14, 23, 0.95);
  border-radius: 15px;
  border: 2px solid rgba(0, 170, 255, 0.3);
  overflow: hidden;
}

.scene-container canvas {
  display: block;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  background: rgba(10, 14, 23, 0.95);
  color: var(--color-text-dim);
  font-size: 14px;
}

.loader {
  width: 50px;
  height: 50px;
  border: 3px solid rgba(0, 170, 255, 0.2);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.data-sidebar {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.data-panel,
.control-panel,
.info-panel {
  background: rgba(26, 34, 53, 0.9);
  border: 1px solid rgba(0, 170, 255, 0.3);
  border-radius: 10px;
  overflow: hidden;
}

.panel-header {
  padding: 12px 15px;
  background: rgba(0, 170, 255, 0.1);
  border-bottom: 1px solid rgba(0, 170, 255, 0.2);
}

.panel-header span {
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
}

.data-list {
  padding: 10px 0;
}

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.data-row:last-child {
  border-bottom: none;
}

.data-row.danger {
  background: rgba(255, 71, 87, 0.1);
}

.data-label {
  color: var(--color-text-dim);
  font-size: 12px;
}

.data-value {
  color: var(--color-accent);
  font-size: 14px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.data-row.danger .data-value {
  color: #ff4757;
}

.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 15px;
}

.ctrl-btn {
  padding: 12px;
  border: 2px solid;
  border-radius: 8px;
  background: transparent;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ctrl-btn.start {
  border-color: #36d399;
  color: #36d399;
}

.ctrl-btn.start:hover:not(:disabled) {
  background: rgba(54, 211, 153, 0.15);
  box-shadow: 0 0 15px rgba(54, 211, 153, 0.3);
}

.ctrl-btn.start:disabled {
  border-color: #4a5568;
  color: #4a5568;
  cursor: not-allowed;
}

.ctrl-btn.stop {
  border-color: #ff4757;
  color: #ff4757;
}

.ctrl-btn.stop:hover:not(:disabled) {
  background: rgba(255, 71, 87, 0.15);
  box-shadow: 0 0 15px rgba(255, 71, 87, 0.3);
}

.ctrl-btn.stop:disabled {
  border-color: #4a5568;
  color: #4a5568;
  cursor: not-allowed;
}

.ctrl-btn.reset {
  border-color: #00aaff;
  color: #00aaff;
}

.ctrl-btn.reset:hover {
  background: rgba(0, 170, 255, 0.15);
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.3);
}

.tips-list {
  list-style: none;
  padding: 15px;
  margin: 0;
}

.tips-list li {
  color: var(--color-text-dim);
  font-size: 12px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.tips-list li:last-child {
  border-bottom: none;
}

.tips-list li::before {
  content: '▸ ';
  color: var(--color-primary);
}

.tips-list li.tip-highlight {
  color: #36d399;
  font-weight: 600;
}

.tips-list li.tip-highlight::before {
  content: '★ ';
  color: #36d399;
}
</style>
