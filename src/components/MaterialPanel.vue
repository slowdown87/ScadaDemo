<template>
  <div class="material-panel">
    <div class="panel-header">
      <span>◆ 物料追踪</span>
      <div class="header-actions">
        <button class="btn-icon" @click="initializeLots" title="初始化示例数据">
          <span>↻</span>
        </button>
        <button class="btn-icon" @click="toggleAutoUpdate" :class="{ active: autoUpdate }" title="自动更新">
          <span>⟳</span>
        </button>
      </div>
    </div>

    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">总数</span>
        <span class="stat-value">{{ materialStore.lotStats.total }}</span>
      </div>
      <div class="stat-item transit">
        <span class="stat-label">运输中</span>
        <span class="stat-value">{{ materialStore.lotStats.inTransit }}</span>
      </div>
      <div class="stat-item stored">
        <span class="stat-label">库存</span>
        <span class="stat-value">{{ materialStore.lotStats.stored }}</span>
      </div>
      <div class="stat-item processing">
        <span class="stat-label">加工</span>
        <span class="stat-value">{{ materialStore.lotStats.inProcess }}</span>
      </div>
    </div>

    <div class="lots-list">
      <div
        v-for="lot in materialStore.lots"
        :key="lot.id"
        :class="['lot-item', { selected: lot.id === materialStore.selectedLotId }]"
        @click="selectLot(lot)"
      >
        <div class="lot-header">
          <span class="lot-id">{{ lot.id }}</span>
          <span
            class="lot-status"
            :style="{ backgroundColor: materialStore.LotStatusColors[lot.status] }"
          >
            {{ materialStore.LotStatusLabels[lot.status] }}
          </span>
        </div>
        <div class="lot-info">
          <span class="lot-name">{{ lot.materialName }}</span>
          <span class="lot-quantity">{{ lot.quantity }} {{ lot.unit }}</span>
        </div>
        <div class="lot-location">
          <span class="location-icon">◈</span>
          <span>{{ getLocationName(lot.currentLocation) }}</span>
        </div>
        <div class="lot-actions" @click.stop>
          <button
            v-if="lot.status === LotStatus.STORED"
            class="action-btn start"
            @click="startProcess(lot.id)"
            title="开始加工"
          >
            ▶
          </button>
          <button
            v-if="lot.status === LotStatus.IN_PROCESS || lot.status === LotStatus.QC_PENDING"
            class="action-btn advance"
            @click="advanceStep(lot.id)"
            title="推进工序"
          >
            →
          </button>
          <button
            v-if="lot.status === LotStatus.IN_TRANSIT"
            class="action-btn complete"
            @click="arriveLot(lot.id)"
            title="到达"
          >
            ✓
          </button>
        </div>
      </div>

      <div v-if="materialStore.lots.length === 0" class="empty-state">
        <span>暂无物料批次</span>
        <button class="btn-primary" @click="initializeLots">加载示例数据</button>
      </div>
    </div>

    <div v-if="materialStore.selectedLot" class="lot-detail">
      <div class="detail-header">
        <span>批次详情</span>
        <button class="btn-close" @click="materialStore.clearSelection()">×</button>
      </div>
      <div class="detail-content">
        <div class="detail-row">
          <span class="detail-label">批次号</span>
          <span class="detail-value">{{ materialStore.selectedLot.id }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">物料</span>
          <span class="detail-value">{{ materialStore.selectedLot.materialName }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">数量</span>
          <span class="detail-value">{{ materialStore.selectedLot.quantity }} {{ materialStore.selectedLot.unit }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">当前工序</span>
          <span class="detail-value">
            {{ materialStore.ProcessSteps[materialStore.selectedLot.processStep]?.name || 'N/A' }}
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">当前位置</span>
          <span class="detail-value">{{ getLocationName(materialStore.selectedLot.currentLocation) }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">生产日期</span>
          <span class="detail-value">{{ formatDate(materialStore.selectedLot.batchDate) }}</span>
        </div>

        <div class="process-timeline">
          <div
            v-for="(step, index) in materialStore.ProcessSteps"
            :key="step.id"
            :class="['timeline-step', {
              completed: index <= materialStore.selectedLot.processStep,
              current: index === materialStore.selectedLot.processStep
            }]"
          >
            <div class="step-dot"></div>
            <div class="step-info">
              <span class="step-name">{{ step.name }}</span>
              <span class="step-location">{{ getLocationName(step.location) }}</span>
            </div>
          </div>
        </div>

        <div class="history-section">
          <div class="history-header">移动历史</div>
          <div class="history-list">
            <div
              v-for="(entry, index) in materialStore.selectedLot.history"
              :key="index"
              class="history-item"
            >
              <span class="history-time">{{ formatTime(entry.timestamp) }}</span>
              <span class="history-location">{{ getLocationName(entry.location) }}</span>
              <span class="history-action">{{ entry.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useMaterialStore } from '@/stores/materialStore'
import { LotStatus, ProcessLocations } from '@/models/materialLot'

const materialStore = useMaterialStore()

const autoUpdate = ref(false)
let updateInterval = null

const locationNames = {
  [ProcessLocations.RAW_MATERIAL_STORAGE]: '原料仓库',
  [ProcessLocations.REACTOR_LOADING]: '反应釜上料',
  [ProcessLocations.REACTOR]: '反应釜 R-101',
  [ProcessLocations.MIXING_TANK]: '混合罐',
  [ProcessLocations.QUALITY_CONTROL]: '质检站',
  [ProcessLocations.PRODUCT_STORAGE]: '成品仓库',
  [ProcessLocations.SHIPPING]: '发货区'
}

function getLocationName(locationId) {
  return locationNames[locationId] || locationId || '未知'
}

function formatDate(isoString) {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleDateString('zh-CN')
}

function formatTime(isoString) {
  if (!isoString) return 'N/A'
  const date = new Date(isoString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function selectLot(lot) {
  materialStore.selectLot(lot.id)
}

function initializeLots() {
  materialStore.initializeDemoLots()
}

function toggleAutoUpdate() {
  autoUpdate.value = !autoUpdate.value
  if (autoUpdate.value) {
    materialStore.startTracking()
  } else {
    materialStore.stopTracking()
  }
}

function startProcess(lotId) {
  materialStore.advanceProcessStep(lotId)
}

function advanceStep(lotId) {
  materialStore.advanceProcessStep(lotId)
}

function arriveLot(lotId) {
  const lot = materialStore.getLot(lotId)
  if (lot && lot.targetLocation) {
    materialStore.moveLot(lotId, lot.targetLocation, false)
  }
}

onMounted(() => {
  if (materialStore.lots.length === 0) {
    materialStore.initializeDemoLots()
  }
})

onUnmounted(() => {
  if (updateInterval) {
    clearInterval(updateInterval)
  }
  materialStore.stopTracking()
})
</script>

<style scoped>
.material-panel {
  background: rgba(26, 34, 53, 0.95);
  border: 1px solid rgba(0, 170, 255, 0.3);
  border-radius: 10px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 100%;
}

.panel-header {
  padding: 12px 15px;
  background: rgba(0, 170, 255, 0.1);
  border-bottom: 1px solid rgba(0, 170, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header span {
  color: var(--color-primary);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 1px;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: transparent;
  border: 1px solid rgba(0, 170, 255, 0.3);
  border-radius: 4px;
  color: var(--color-text-dim);
  width: 28px;
  height: 28px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(0, 170, 255, 0.2);
  color: var(--color-primary);
}

.btn-icon.active {
  background: rgba(0, 170, 255, 0.3);
  color: var(--color-primary);
}

.stats-bar {
  display: flex;
  padding: 10px;
  gap: 8px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: 8px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 6px;
}

.stat-label {
  display: block;
  font-size: 10px;
  color: var(--color-text-dim);
  margin-bottom: 4px;
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text);
  font-family: 'Courier New', monospace;
}

.stat-item.transit .stat-value {
  color: var(--color-primary);
}

.stat-item.stored .stat-value {
  color: var(--color-accent);
}

.stat-item.processing .stat-value {
  color: var(--color-warning);
}

.lots-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.lot-item {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 170, 255, 0.15);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.lot-item:hover {
  background: rgba(0, 170, 255, 0.1);
  border-color: rgba(0, 170, 255, 0.3);
}

.lot-item.selected {
  background: rgba(0, 170, 255, 0.15);
  border-color: var(--color-primary);
}

.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.lot-id {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text);
  font-family: 'Courier New', monospace;
}

.lot-status {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
}

.lot-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.lot-name {
  font-size: 12px;
  color: var(--color-text-dim);
}

.lot-quantity {
  font-size: 12px;
  color: var(--color-accent);
  font-family: 'Courier New', monospace;
}

.lot-location {
  font-size: 11px;
  color: var(--color-text-dim);
  display: flex;
  align-items: center;
  gap: 4px;
}

.location-icon {
  color: var(--color-primary);
}

.lot-actions {
  display: flex;
  gap: 6px;
  margin-top: 8px;
}

.action-btn {
  flex: 1;
  padding: 6px;
  border: 1px solid;
  border-radius: 4px;
  background: transparent;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn.start {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.action-btn.start:hover {
  background: rgba(54, 211, 153, 0.2);
}

.action-btn.advance {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.action-btn.advance:hover {
  background: rgba(0, 170, 255, 0.2);
}

.action-btn.complete {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.action-btn.complete:hover {
  background: rgba(38, 222, 129, 0.2);
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: var(--color-text-dim);
}

.empty-state span {
  display: block;
  margin-bottom: 15px;
}

.btn-primary {
  background: rgba(0, 170, 255, 0.2);
  border: 1px solid var(--color-primary);
  color: var(--color-primary);
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: rgba(0, 170, 255, 0.4);
}

.lot-detail {
  border-top: 1px solid rgba(0, 170, 255, 0.2);
  background: rgba(0, 0, 0, 0.2);
  max-height: 40%;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: rgba(0, 170, 255, 0.1);
  position: sticky;
  top: 0;
}

.detail-header span {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-primary);
}

.btn-close {
  background: transparent;
  border: none;
  color: var(--color-text-dim);
  font-size: 18px;
  cursor: pointer;
  line-height: 1;
}

.btn-close:hover {
  color: var(--color-text);
}

.detail-content {
  padding: 10px 15px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.detail-label {
  font-size: 11px;
  color: var(--color-text-dim);
}

.detail-value {
  font-size: 11px;
  color: var(--color-text);
  font-family: 'Courier New', monospace;
}

.process-timeline {
  margin-top: 15px;
  padding-left: 10px;
}

.timeline-step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  position: relative;
}

.timeline-step:not(:last-child)::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 15px;
  width: 2px;
  height: calc(100% + 4px);
  background: rgba(0, 170, 255, 0.2);
}

.timeline-step.completed::before {
  background: rgba(0, 170, 255, 0.5);
}

.step-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(0, 170, 255, 0.2);
  border: 2px solid rgba(0, 170, 255, 0.4);
  margin-right: 10px;
  flex-shrink: 0;
}

.timeline-step.completed .step-dot {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.timeline-step.current .step-dot {
  background: var(--color-warning);
  border-color: var(--color-warning);
  box-shadow: 0 0 8px rgba(247, 183, 49, 0.5);
}

.step-info {
  display: flex;
  flex-direction: column;
}

.step-name {
  font-size: 11px;
  color: var(--color-text);
  font-weight: 600;
}

.step-location {
  font-size: 10px;
  color: var(--color-text-dim);
}

.history-section {
  margin-top: 15px;
}

.history-header {
  font-size: 11px;
  font-weight: 600;
  color: var(--color-text-dim);
  margin-bottom: 8px;
}

.history-list {
  max-height: 100px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 10px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.history-time {
  color: var(--color-text-dim);
  font-family: 'Courier New', monospace;
}

.history-location {
  color: var(--color-text);
  flex: 1;
}

.history-action {
  color: var(--color-primary);
}
</style>