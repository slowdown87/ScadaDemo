<template>
  <nav class="side-nav" :class="{ collapsed: isCollapsed }">
    <div class="nav-header">
      <div class="logo">
        <div class="logo-icon-wrapper">
          <svg viewBox="0 0 24 24" width="28" height="28" class="logo-icon">
            <path fill="currentColor" d="M12,2L2,7L12,12L22,7L12,2M2,17L12,22L22,17L12,12L2,17Z"/>
          </svg>
        </div>
        <transition name="fade">
          <span v-if="!isCollapsed" class="logo-text">SCADA</span>
        </transition>
      </div>
      <button class="collapse-btn" @click="toggleCollapse">
        <svg viewBox="0 0 24 24" width="18" height="18" :class="{ rotated: isCollapsed }">
          <path fill="currentColor" d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"/>
        </svg>
      </button>
    </div>

    <ul class="nav-menu">
      <li
        v-for="item in menuItems"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        :title="isCollapsed ? item.label : ''"
      >
        <router-link
          :to="item.path"
          class="nav-link"
        >
          <div class="nav-icon-wrapper">
            <component :is="item.iconComponent" class="nav-icon" />
          </div>
          <transition name="fade">
            <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
          </transition>
          <transition name="fade">
            <span v-if="!isCollapsed && item.badge" class="nav-badge">{{ item.badge }}</span>
          </transition>
        </router-link>
        <div v-if="currentPath === item.path" class="active-indicator"></div>
      </li>
    </ul>

    <div class="nav-footer">
      <div class="system-meta" v-if="!isCollapsed">
        <span class="meta-item">方案A</span>
        <span class="meta-divider">·</span>
        <span class="meta-item">工业组态</span>
      </div>
      <div class="system-status" :class="{ online: isOnline }">
        <span class="status-dot"></span>
        <transition name="fade">
          <span v-if="!isCollapsed" class="status-text">{{ isOnline ? '在线' : '离线' }}</span>
        </transition>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref, h } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const isCollapsed = ref(false)

const currentPath = computed(() => route.path)
const isOnline = computed(() => true)

const HomeIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', width: 20, height: 20 }, [
      h('path', { fill: 'currentColor', d: 'M12,2L2,7L12,12L22,7L12,2M2,17L12,22L22,17L12,12L2,17Z' })
    ])
  }
}

const TwinIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', width: 20, height: 20 }, [
      h('path', { fill: 'currentColor', d: 'M4,4H20C21.1,4 22,4.9 22,6V18C22,19.1 21.1,20 20,20H4C2.9,20 2,19.1 2,18V6C2,4.9 2.9,4 4,4M4,6V18H20V6H4M6,8H8V10H10V8H14V10H16V8H18V12H6V8M9,14H15V16H9V14Z' })
    ])
  }
}

const SimulationIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', width: 20, height: 20 }, [
      h('path', { fill: 'currentColor', d: 'M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6M12,8A4,4 0 0,1 16,12A4,4 0 0,1 12,16A4,4 0 0,1 8,12A4,4 0 0,1 12,8M12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12A2,2 0 0,0 12,10Z' })
    ])
  }
}

const PerfIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', width: 20, height: 20 }, [
      h('path', { fill: 'currentColor', d: 'M3,14L3.5,14.07L8.07,9.5C7.89,8.85 8.06,8.11 8.59,7.59C9.37,6.8 10.63,6.8 11.41,7.59C11.94,8.11 12.11,8.85 11.93,9.5L14.5,12L11.93,14.5C12.11,15.15 11.94,15.89 11.41,16.41C10.63,17.2 9.37,17.2 8.59,16.41C8.06,15.89 7.89,15.15 8.07,14.5L3.5,9.93L3,10L3,14M10,14.5L14,10.5L10.5,7L6.5,11L10,14.5M16.5,6.5L18.5,8.5L10,17L8,15L16.5,6.5Z' })
    ])
  }
}

const TrendIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', width: 20, height: 20 }, [
      h('path', { fill: 'currentColor', d: 'M16,11.78L20.24,4.45L21.97,5.45L16.74,14.5L10.23,10.75L5.46,19H22V21H2V3H4V17.54L9.5,8L16,11.78Z' })
    ])
  }
}

const AboutIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', width: 20, height: 20 }, [
      h('path', { fill: 'currentColor', d: 'M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z' })
    ])
  }
}

const menuItems = [
  { path: '/home', label: '工业组态', iconComponent: HomeIcon, desc: '方案A' },
  { path: '/twin', label: '数字孪生', iconComponent: TwinIcon, desc: '方案B' },
  { path: '/simulation', label: '仿真培训', iconComponent: SimulationIcon, desc: '方案D' },
  { path: '/perf', label: '性能监控', iconComponent: PerfIcon, desc: '方案C' },
  { path: '/trend', label: '趋势分析', iconComponent: TrendIcon, desc: '数据分析' },
  { path: '/about', label: '关于', iconComponent: AboutIcon, desc: '项目介绍' }
]

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style scoped>
.side-nav {
  width: 220px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(
    180deg,
    rgba(26, 34, 53, 0.95) 0%,
    rgba(18, 24, 38, 0.98) 100%
  );
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid var(--color-border-light);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.side-nav.collapsed {
  width: 72px;
}

.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px;
  border-bottom: 1px solid var(--color-border-light);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  overflow: hidden;
}

.logo-icon-wrapper {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-600));
  border-radius: 10px;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 170, 255, 0.3);
}

.logo-icon {
  color: white;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: 3px;
  text-shadow: 0 0 20px rgba(0, 170, 255, 0.5);
  white-space: nowrap;
}

.collapse-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.collapse-btn:hover {
  background: rgba(0, 170, 255, 0.1);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.collapse-btn svg {
  transition: transform 0.3s ease;
}

.collapse-btn svg.rotated {
  transform: rotate(180deg);
}

.nav-menu {
  flex: 1;
  list-style: none;
  padding: 12px 8px;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-item {
  position: relative;
  margin-bottom: 4px;
  border-radius: 12px;
  transition: all var(--transition-normal);
}

.nav-item::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-600));
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.nav-item:hover::before {
  opacity: 0.08;
}

.nav-item.active::before {
  opacity: 0.15;
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600));
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  text-decoration: none;
  color: inherit;
  position: relative;
  z-index: 1;
}

.nav-icon-wrapper {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  flex-shrink: 0;
  transition: all var(--transition-normal);
}

.nav-icon {
  color: var(--color-text-secondary);
  transition: all var(--transition-normal);
}

.nav-item:hover .nav-icon-wrapper {
  background: rgba(0, 170, 255, 0.15);
}

.nav-item:hover .nav-icon {
  color: var(--color-primary);
  transform: scale(1.1);
}

.nav-item.active .nav-icon-wrapper {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-600));
  box-shadow: 0 4px 12px rgba(0, 170, 255, 0.3);
}

.nav-item.active .nav-icon {
  color: white;
}

.nav-label {
  font-size: 13px;
  color: var(--color-text-secondary);
  letter-spacing: 0.5px;
  white-space: nowrap;
  transition: all var(--transition-normal);
}

.nav-item:hover .nav-label {
  color: var(--color-text-primary);
}

.nav-item.active .nav-label {
  color: var(--color-text-primary);
  font-weight: 600;
}

.nav-badge {
  margin-left: auto;
  padding: 2px 8px;
  font-size: 10px;
  color: var(--color-primary);
  background: rgba(0, 170, 255, 0.15);
  border-radius: 10px;
  white-space: nowrap;
}

.nav-item.active .nav-badge {
  background: rgba(54, 211, 153, 0.2);
  color: var(--color-accent);
}

.active-indicator {
  position: absolute;
  right: -8px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: var(--color-accent);
  border-radius: 2px;
  box-shadow: 0 0 12px var(--color-accent);
}

.nav-footer {
  padding: 16px;
  border-top: 1px solid var(--color-border-light);
}

.system-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-bottom: 12px;
}

.meta-item {
  font-size: 11px;
  color: var(--color-text-tertiary);
  letter-spacing: 0.5px;
}

.meta-divider {
  font-size: 10px;
  color: var(--color-border-light);
}

.system-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(255, 71, 87, 0.1);
  border: 1px solid rgba(255, 71, 87, 0.2);
  border-radius: 8px;
  transition: all var(--transition-normal);
}

.system-status.online {
  background: rgba(54, 211, 153, 0.1);
  border-color: rgba(54, 211, 153, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-danger);
  animation: statusBreathe 2s ease-in-out infinite;
}

.system-status.online .status-dot {
  background: var(--color-accent);
  box-shadow: 0 0 8px var(--color-accent);
}

.status-text {
  font-size: 11px;
  color: var(--color-danger);
  letter-spacing: 0.5px;
}

.system-status.online .status-text {
  color: var(--color-accent);
}

@keyframes statusBreathe {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .side-nav {
    width: 72px;
  }

  .nav-label,
  .nav-badge,
  .logo-text,
  .system-meta,
  .status-text {
    display: none;
  }

  .collapse-btn {
    display: none;
  }
}
</style>
