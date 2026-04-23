<template>
  <div class="plant-view">
    <div class="plant-header">
      <h2 class="plant-title">◆ 工艺流程监控</h2>
      <div class="plant-legend">
        <span class="legend-item running">● 运行</span>
        <span class="legend-item stopped">● 停止</span>
        <span class="legend-item alarm">● 报警</span>
      </div>
    </div>

    <div class="plant-container" ref="containerRef">
      <img
        :src="flowsheetSrc"
        alt="工艺流程图"
        class="flowsheet-image"
        :class="{ running: isRunning }"
      />

      <div class="data-overlay">
        <div class="data-label tank-level" :class="getAlarmClass('level')">
          <span class="label-value">{{ tankLevel }}%</span>
        </div>

        <div class="data-label flow-rate">
          <span class="label-value">{{ flowRate }} L/s</span>
        </div>

        <div class="data-label reactor-temp" :class="getAlarmClass('temp')">
          <span class="label-value">{{ reactorTemp }}°C</span>
        </div>

        <div class="data-label reactor-pressure" :class="getAlarmClass('pressure')">
          <span class="label-value">{{ reactorPressure }} atm</span>
        </div>

        <div class="data-label motor-speed" :class="{ active: isRunning }">
          <span class="label-value">{{ motorSpeed }} RPM</span>
        </div>

        <div class="data-label product-count">
          <span class="label-value">{{ productCount }}</span>
        </div>
      </div>

      <div class="equipment-animations">
        <div class="equip mixer" :class="{ running: isRunning }">
          <div class="blade blade1"></div>
          <div class="blade blade2"></div>
        </div>

        <div class="equip motor" :class="{ running: isRunning }">
          <div class="motor-rotor"></div>
        </div>
      </div>

      <div class="pipe-flows">
        <svg class="pipe-svg" viewBox="0 0 1200 700" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#00aaff;stop-opacity:0.3" />
              <stop offset="50%" style="stop-color:#00ffee;stop-opacity:0.8" />
              <stop offset="100%" style="stop-color:#00aaff;stop-opacity:0.3" />
            </linearGradient>
          </defs>

          <path
            class="pipe-path horizontal"
            :class="{ flowing: isRunning }"
            d="M 140 260 L 260 270"
          />
          <path
            class="pipe-path diagonal"
            :class="{ flowing: isRunning }"
            d="M 300 270 L 400 250"
          />
          <path
            class="pipe-path horizontal"
            :class="{ flowing: isRunning }"
            d="M 500 250 L 580 230"
          />
          <path
            class="pipe-path horizontal"
            :class="{ flowing: isRunning }"
            d="M 720 230 L 780 240"
          />
          <path
            class="pipe-path horizontal final"
            :class="{ flowing: isRunning }"
            d="M 880 240 L 960 260"
          />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import flowsheetSrc from '@/assets/flowsheet.svg'

const props = defineProps({
  isRunning: { type: Boolean, default: false },
  tankLevel: { type: Number, default: 50 },
  flowRate: { type: Number, default: 0 },
  reactorTemp: { type: Number, default: 25 },
  reactorPressure: { type: Number, default: 1.0 },
  motorSpeed: { type: Number, default: 0 },
  productCount: { type: Number, default: 0 },
  alarms: { type: Array, default: () => [] }
})

const containerRef = ref(null)

function getAlarmClass(type) {
  const alarm = props.alarms.find(a => {
    if (type === 'level') return a.id.includes('LEVEL')
    if (type === 'temp') return a.id.includes('TEMP')
    if (type === 'pressure') return a.id.includes('PRESSURE')
    return false
  })
  if (!alarm) return ''
  return alarm.level === 'critical' ? 'danger' : 'warning'
}
</script>

<style scoped>
.plant-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: rgba(10, 14, 23, 0.95);
  border-radius: 10px;
  overflow: hidden;
}

.plant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: rgba(26, 34, 53, 0.8);
  border-bottom: 1px solid rgba(0, 170, 255, 0.2);
}

.plant-title {
  color: #00aaff;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
  margin: 0;
}

.plant-legend {
  display: flex;
  gap: 15px;
}

.legend-item {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-item.running {
  background: rgba(54, 211, 153, 0.2);
  color: #36d399;
}

.legend-item.stopped {
  background: rgba(74, 85, 104, 0.2);
  color: #4a5568;
}

.legend-item.alarm {
  background: rgba(255, 71, 87, 0.2);
  color: #ff4757;
}

.plant-container {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background:
    radial-gradient(circle at 50% 50%, rgba(0, 170, 255, 0.03) 0%, transparent 50%),
    linear-gradient(rgba(26, 34, 53, 0.3) 1px, transparent 1px),
    linear-gradient(90deg, rgba(26, 34, 53, 0.3) 1px, transparent 1px);
  background-size: 100% 100%, 50px 50px, 50px 50px;
}

.flowsheet-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 0 30px rgba(0, 170, 255, 0.2));
  transition: filter 0.5s ease;
}

.flowsheet-image.running {
  filter: drop-shadow(0 0 50px rgba(0, 170, 255, 0.4));
}

.data-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.data-label {
  position: absolute;
  background: rgba(26, 34, 53, 0.95);
  border: 1px solid rgba(0, 170, 255, 0.5);
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  color: #36d399;
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.2);
  transition: all 0.3s ease;
}

.data-label.warning {
  border-color: rgba(255, 159, 67, 0.7);
  color: #ff9f43;
  animation: label-pulse-warning 1.5s ease-in-out infinite;
}

.data-label.danger {
  border-color: rgba(255, 71, 87, 0.7);
  color: #ff4757;
  animation: label-pulse-danger 0.8s ease-in-out infinite;
}

.data-label.active {
  border-color: rgba(54, 211, 153, 0.7);
  box-shadow: 0 0 20px rgba(54, 211, 153, 0.3);
}

@keyframes label-pulse-warning {
  0%, 100% { box-shadow: 0 0 10px rgba(255, 159, 67, 0.3); }
  50% { box-shadow: 0 0 25px rgba(255, 159, 67, 0.5); }
}

@keyframes label-pulse-danger {
  0%, 100% { box-shadow: 0 0 15px rgba(255, 71, 87, 0.4); }
  50% { box-shadow: 0 0 30px rgba(255, 71, 87, 0.7); }
}

.tank-level { top: 38%; left: 8%; }
.flow-rate { top: 50%; left: 24%; }
.reactor-temp { top: 28%; left: 52%; }
.reactor-pressure { top: 55%; left: 52%; }
.motor-speed { top: 10%; left: 55%; }
.product-count { top: 38%; left: 84%; }

.equipment-animations {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.equip {
  position: absolute;
}

.equip.mixer {
  top: 32%;
  left: 37%;
  width: 60px;
  height: 60px;
}

.blade {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 4px;
  background: linear-gradient(90deg, transparent, #00aaff, transparent);
  transform-origin: center;
  border-radius: 2px;
}

.blade1 {
  transform: translate(-50%, -50%) rotate(0deg);
}

.blade2 {
  transform: translate(-50%, -50%) rotate(90deg);
}

.equip.mixer.running .blade1 {
  animation: rotate-blade 2s linear infinite;
}

.equip.mixer.running .blade2 {
  animation: rotate-blade 2s linear infinite reverse;
}

@keyframes rotate-blade {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.equip.motor {
  top: 18%;
  left: 57%;
  width: 40px;
  height: 40px;
  border: 3px solid #00aaff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.motor-rotor {
  width: 20px;
  height: 20px;
  background: conic-gradient(#00aaff, #00ffee, #00aaff);
  border-radius: 50%;
  opacity: 0.6;
}

.equip.motor.running .motor-rotor {
  animation: spin-rotor 1s linear infinite;
}

@keyframes spin-rotor {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.pipe-flows {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.pipe-svg {
  width: 100%;
  height: 100%;
}

.pipe-path {
  fill: none;
  stroke: url(#flowGradient);
  stroke-width: 6;
  stroke-linecap: round;
  opacity: 0.3;
}

.pipe-path.flowing {
  opacity: 1;
  stroke-dasharray: 20, 10;
  animation: flow-dash 1s linear infinite;
}

@keyframes flow-dash {
  from { stroke-dashoffset: 30; }
  to { stroke-dashoffset: 0; }
}
</style>
