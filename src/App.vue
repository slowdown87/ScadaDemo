<template>
  <div class="scada-app">
    <header class="app-header">
      <div class="header-left">
        <div class="logo-wrapper">
          <svg viewBox="0 0 24 24" width="24" height="24" class="logo-icon">
            <path fill="currentColor" d="M12,2L2,7L12,12L22,7L12,2M2,17L12,22L22,17L12,12L2,17Z"/>
          </svg>
        </div>
        <h1 class="app-title">SCADA INTELLIGENT CONTROL SYSTEM</h1>
      </div>
      <div class="header-right">
        <span class="version">v2.0.0</span>
        <div class="connection-status" :class="{ online: isOnline }">
          <span class="status-dot"></span>
          <span class="status-text">{{ isOnline ? 'ONLINE' : 'OFFLINE' }}</span>
        </div>
      </div>
    </header>

    <div class="app-body">
      <SideNav />
      <main class="app-main">
        <router-view />
      </main>
    </div>

    <footer class="app-footer">
      <span class="footer-item time">{{ systemTime }}</span>
      <span class="footer-divider">|</span>
      <span class="footer-item">Refresh: 1s</span>
      <span class="footer-divider">|</span>
      <span class="footer-item resolution">1920×1080</span>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { usePlantStore } from '@/stores/plantStore'
import SideNav from '@/components/SideNav.vue'

const plantStore = usePlantStore()

const isOnline = computed(() => plantStore.connectionStatus === 'ONLINE')
const systemTime = ref('')

let timeInterval = null

function updateTime() {
  const now = new Date()
  systemTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.scada-app {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
}

.app-header {
  height: 60px;
  background: linear-gradient(
    90deg,
    rgba(0, 40, 80, 0.95) 0%,
    rgba(0, 60, 120, 0.9) 50%,
    rgba(0, 40, 80, 0.95) 100%
  );
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow:
    0 4px 20px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(0, 170, 255, 0.1);
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.app-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    var(--color-primary) 20%,
    var(--color-primary) 80%,
    transparent 100%
  );
  opacity: 0.5;
}

.app-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-600));
  border-radius: 10px;
  box-shadow:
    0 4px 12px rgba(0, 170, 255, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  animation: logoGlow 3s ease-in-out infinite;
}

@keyframes logoGlow {
  0%, 100% {
    box-shadow:
      0 4px 12px rgba(0, 170, 255, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
  50% {
    box-shadow:
      0 4px 20px rgba(0, 170, 255, 0.5),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }
}

.logo-icon {
  color: white;
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 3px;
  color: var(--color-text-primary);
  text-shadow: 0 2px 10px rgba(0, 170, 255, 0.3);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.version {
  font-size: 12px;
  color: var(--color-text-tertiary);
  letter-spacing: 1px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.2);
  border-radius: 20px;
  transition: all var(--transition-normal);
}

.connection-status.online {
  background: rgba(54, 211, 153, 0.1);
  border-color: rgba(54, 211, 153, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-danger);
  animation: statusPulse 2s ease-in-out infinite;
}

.connection-status.online .status-dot {
  background: var(--color-accent);
  box-shadow: 0 0 8px var(--color-accent);
}

@keyframes statusPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 1px;
  color: var(--color-danger);
}

.connection-status.online .status-text {
  color: var(--color-accent);
}

.app-main {
  flex: 1;
  overflow: auto;
  min-height: 0;
  padding: 20px;
  background: linear-gradient(
    180deg,
    rgba(10, 15, 26, 1) 0%,
    rgba(18, 24, 38, 1) 100%
  );
}

.app-footer {
  height: 36px;
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  font-size: 12px;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  padding: 0 20px;
}

.footer-item {
  letter-spacing: 0.5px;
}

.footer-item.time {
  font-variant-numeric: tabular-nums;
  color: var(--color-text-secondary);
}

.footer-divider {
  color: var(--color-border-light);
  opacity: 0.5;
}

.footer-item.resolution {
  font-variant-numeric: tabular-nums;
}

@media (max-width: 1400px) {
  .app-title {
    font-size: 16px;
    letter-spacing: 2px;
  }

  .version {
    display: none;
  }
}

@media (max-width: 1024px) {
  .app-header {
    padding: 0 16px;
  }

  .app-title {
    font-size: 14px;
    letter-spacing: 1px;
  }

  .header-right {
    gap: 12px;
  }

  .connection-status {
    padding: 4px 10px;
  }

  .status-text {
    display: none;
  }
}
</style>
