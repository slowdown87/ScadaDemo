<template>
  <nav class="side-nav">
    <div class="nav-header">
      <div class="logo">
        <span class="logo-icon">◆</span>
        <span class="logo-text">SCADA</span>
      </div>
    </div>

    <ul class="nav-menu">
      <li
        v-for="item in menuItems"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        @click="navigate(item.path)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
        <span class="nav-badge" v-if="item.badge">{{ item.badge }}</span>
      </li>
    </ul>

    <div class="nav-footer">
      <div class="connection-status">
        <span class="status-dot" :class="{ online: true }"></span>
        <span class="status-text">ONLINE</span>
      </div>
      <div class="version-info">v2.0.0</div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const currentPath = computed(() => route.path)

const menuItems = [
  { path: '/home', label: '工业组态', icon: '◆', desc: '方案A' },
  { path: '/twin', label: '数字孪生', icon: '◈', desc: '方案B' },
  { path: '/perf', label: '性能监控', icon: '◉', desc: '方案C' },
  { path: '/trend', label: '趋势分析', icon: '◇', desc: '数据分析' },
  { path: '/about', label: '关于', icon: '○', desc: '项目介绍' }
]

function navigate(path) {
  router.push(path)
}
</script>

<style scoped>
.side-nav {
  width: 200px;
  height: 100%;
  background: linear-gradient(180deg, rgba(0, 60, 120, 0.6) 0%, rgba(0, 30, 80, 0.8) 100%);
  border-right: 1px solid rgba(0, 170, 255, 0.3);
  display: flex;
  flex-direction: column;
  box-shadow: 5px 0 20px rgba(0, 0, 0, 0.3);
}

.nav-header {
  padding: 25px 20px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.2);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
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

.logo-text {
  font-size: 20px;
  font-weight: bold;
  color: var(--color-primary);
  letter-spacing: 3px;
  text-shadow: 0 0 10px rgba(0, 170, 255, 0.5);
}

.nav-menu {
  flex: 1;
  list-style: none;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 15px 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  position: relative;
}

.nav-item:hover {
  background: rgba(0, 170, 255, 0.1);
  border-left-color: rgba(0, 170, 255, 0.5);
}

.nav-item.active {
  background: rgba(0, 170, 255, 0.15);
  border-left-color: var(--color-accent);
}

.nav-icon {
  font-size: 18px;
  color: var(--color-text-dim);
  transition: all 0.3s ease;
}

.nav-item.active .nav-icon {
  color: var(--color-accent);
  text-shadow: 0 0 10px rgba(54, 211, 153, 0.5);
}

.nav-label {
  font-size: 13px;
  color: var(--color-text-dim);
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.nav-item.active .nav-label {
  color: var(--color-text);
  font-weight: 500;
}

.nav-badge {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 9px;
  color: var(--color-primary);
  opacity: 0.6;
  padding: 2px 6px;
  background: rgba(0, 170, 255, 0.1);
  border-radius: 8px;
}

.nav-item.active .nav-badge {
  color: var(--color-accent);
  opacity: 1;
}

.nav-footer {
  padding: 20px;
  border-top: 1px solid rgba(0, 170, 255, 0.2);
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #888;
}

.status-dot.online {
  background: var(--color-accent);
  box-shadow: 0 0 8px rgba(54, 211, 153, 0.6);
  animation: blink-dot 2s infinite;
}

@keyframes blink-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  color: var(--color-accent);
  letter-spacing: 1px;
}

.version-info {
  font-size: 11px;
  color: var(--color-text-dim);
  text-align: center;
}
</style>
