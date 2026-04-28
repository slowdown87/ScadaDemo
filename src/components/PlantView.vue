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

        <div class="data-label tank-b-level">
          <span class="label-value">{{ tankBLevel }}%</span>
        </div>

        <div class="data-label flow-rate">
          <span class="label-value">{{ flowRate }} L/s</span>
        </div>

        <div class="data-label flow-rate-b">
          <span class="label-value">{{ flowRateB }} L/s</span>
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

        <div class="data-label sep-level">
          <span class="label-value">{{ sepLevel }}%</span>
        </div>

        <div class="data-label product-count">
          <span class="label-value">{{ productCount }}</span>
        </div>

        <div class="data-label storage-level">
          <span class="label-value">{{ storageLevel }}%</span>
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

        <div class="equip pump" :class="{ running: isRunning }">
          <div class="pump-blade"></div>
        </div>
      </div>

      <div class="pipe-flows">
        <svg class="pipe-svg" viewBox="0 0 1400 750" preserveAspectRatio="xMidYMid meet">
          <defs>
            <linearGradient id="flowGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#00aaff;stop-opacity:0.3" />
              <stop offset="50%" style="stop-color:#00ddff;stop-opacity:0.8" />
              <stop offset="100%" style="stop-color:#00aaff;stop-opacity:0.3" />
            </linearGradient>
          </defs>

          <path
            class="pipe-path horizontal"
            :class="{ flowing: isRunning }"
            d="M 150 220 L 280 225"
          />
          <path
            class="pipe-path horizontal"
            :class="{ flowing: isRunning }"
            d="M 150 450 L 280 455"
          />
          <path
            class="pipe-path diagonal"
            :class="{ flowing: isRunning }"
            d="M 330 225 L 420 340"
          />
          <path
            class="pipe-path diagonal"
            :class="{ flowing: isRunning }"
            d="M 330 455 L 420 340"
          />
          <path
            class="pipe-path horizontal"
            :class="{ flowing: isRunning }"
            d="M 540 340 L 620 250"
          />
          <path
            class="pipe-path horizontal"
            :class="{ flowing: isRunning }"
            d="M 760 280 L 850 270"
          />
          <path
            class="pipe-path horizontal final"
            :class="{ flowing: isRunning }"
            d="M 950 270 L 1040 250"
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
  tankLevel: { type: Number, default: 75 },
  flowRate: { type: Number, default: 10 },
  flowRateB: { type: Number, default: 8 },
  tankBLevel: { type: Number, default: 60 },
  reactorTemp: { type: Number, default: 25 },
  reactorPressure: { type: Number, default: 1.0 },
  motorSpeed: { type: Number, default: 0 },
  productCount: { type: Number, default: 0 },
  sepLevel: { type: Number, default: 50 },
  storageLevel: { type: Number, default: 100 },
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
  background: var(--color-bg-primary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.plant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: var(--color-bg-glass);
  border-bottom: 1px solid var(--color-border-light);
}

.plant-title {
  color: var(--color-primary);
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
  color: var(--color-accent);
}

.legend-item.stopped {
  background: rgba(74, 85, 104, 0.2);
  color: var(--color-text-disabled);
}

.legend-item.alarm {
  background: rgba(255, 71, 87, 0.2);
  color: var(--color-danger);
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
  overflow: hidden;
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
  background: var(--color-bg-glass);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Courier New', monospace;
  color: var(--color-accent);
  box-shadow: var(--shadow-glow);
  transition: all var(--transition-normal);
}

.data-label.warning {
  border-color: var(--color-warning);
  color: var(--color-warning);
  animation: label-pulse-warning 1.5s ease-in-out infinite;
}

.data-label.danger {
  border-color: var(--color-danger);
  color: var(--color-danger);
  animation: label-pulse-danger 0.8s ease-in-out infinite;
}

.data-label.active {
  border-color: var(--color-accent);
  box-shadow: var(--shadow-glow-accent);
}

@keyframes label-pulse-warning {
  0%, 100% { box-shadow: 0 0 10px rgba(255, 159, 67, 0.3); }
  50% { box-shadow: 0 0 25px rgba(255, 159, 67, 0.5); }
}

@keyframes label-pulse-danger {
  0%, 100% { box-shadow: 0 0 15px rgba(255, 71, 87, 0.4); }
  50% { box-shadow: 0 0 30px rgba(255, 71, 87, 0.7); }
}

.tank-level { top: 22%; left: 8%; }
.tank-b-level { top: 54%; left: 8%; }
.flow-rate { top: 28%; left: 22%; }
.flow-rate-b { top: 56%; left: 22%; }
.reactor-temp { top: 26%; left: 48%; }
.reactor-pressure { top: 48%; left: 48%; }
.motor-speed { top: 18%; left: 47%; }
.sep-level { top: 38%; left: 63%; }
.product-count { top: 30%; left: 78%; }
.storage-level { top: 60%; left: 78%; }

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
  top: 42%;
  left: 33%;
  width: 60px;
  height: 60px;
}

.blade {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 4px;
  background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
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
  left: 46%;
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-primary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.motor-rotor {
  width: 20px;
  height: 20px;
  background: conic-gradient(var(--color-primary), var(--color-accent), var(--color-primary));
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

.equip.pump {
  top: 55%;
  left: 62%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pump-blade {
  width: 30px;
  height: 30px;
  border: 3px solid var(--color-primary);
  border-radius: 50%;
  position: relative;
}

.pump-blade::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 4px;
  background: var(--color-primary);
  transform: translate(-50%, -50%) rotate(0deg);
  transform-origin: center;
}

.equip.pump.running .pump-blade::before {
  animation: spin-rotor 0.5s linear infinite;
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