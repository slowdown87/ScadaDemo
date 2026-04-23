<template>
  <div class="scada-app">
    <header class="app-header">
      <div class="header-left">
        <span class="logo-icon">◆</span>
        <h1 class="app-title">SCADA INTELLIGENT CONTROL SYSTEM</h1>
      </div>
      <div class="header-right">
        <span class="version">v1.0.0</span>
        <span class="connection-status" :class="{ online: true }">
          ● {{ connectionStatus }}
        </span>
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer">
      <span class="footer-item">{{ systemTime }}</span>
      <span class="footer-item">|</span>
      <span class="footer-item">Refresh: 1s</span>
      <span class="footer-item">|</span>
      <span class="footer-item">1920×1080</span>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const connectionStatus = ref('ONLINE')
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

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --color-bg: #121826;
  --color-panel: rgba(10, 15, 26, 0.95);
  --color-primary: #00aaff;
  --color-accent: #36d399;
  --color-warning: #ff4444;
  --color-text: #ffffff;
  --color-text-dim: #8892a0;
  --border-radius: 8px;
  --box-shadow: 0 0 20px rgba(0, 170, 255, 0.15);
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

body {
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
  background-color: var(--color-bg);
  color: var(--color-text);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.scada-app {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #0a0f1a 0%, #121826 50%, #0a1020 100%);
}

.app-header {
  height: 60px;
  background: linear-gradient(90deg, rgba(0, 60, 120, 0.8) 0%, rgba(0, 40, 80, 0.9) 100%);
  border-bottom: 2px solid var(--color-primary);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30px;
  box-shadow: 0 0 15px rgba(0, 170, 255, 0.2);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.logo-icon {
  font-size: 28px;
  color: var(--color-primary);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 3px;
  color: var(--color-text);
  text-shadow: 0 0 10px rgba(0, 170, 255, 0.5);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.version {
  font-size: 12px;
  color: var(--color-text-dim);
}

.connection-status {
  font-size: 13px;
  padding: 4px 12px;
  border-radius: 4px;
  background: rgba(54, 211, 153, 0.2);
  color: var(--color-accent);
}

.connection-status.online {
  background: rgba(54, 211, 153, 0.2);
  color: var(--color-accent);
}

.app-main {
  flex: 1;
  overflow: auto;
}

.app-footer {
  height: 35px;
  background: rgba(0, 60, 120, 0.6);
  border-top: 1px solid rgba(0, 170, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  font-size: 12px;
  color: var(--color-text-dim);
  flex-shrink: 0;
}

.footer-item {
  letter-spacing: 1px;
}

@media (max-width: 1400px) {
  .app-title {
    font-size: 16px;
    letter-spacing: 2px;
  }
}

@media (max-width: 1024px) {
  .app-header {
    padding: 0 15px;
  }

  .app-title {
    font-size: 14px;
    letter-spacing: 1px;
  }

  .header-right {
    gap: 10px;
  }
}
</style>
