<template>
  <div class="perf-container">
    <SideNav />
    <main class="main-content">
      <header class="top-bar">
        <div class="header-left">
          <h1 class="page-title">◆ 性能监控系统</h1>
          <span class="page-subtitle">方案C - 高频数据实时监控</span>
        </div>
      </header>

      <div class="perf-placeholder">
        <div class="placeholder-content">
          <div class="placeholder-icon">◉</div>
          <h2>高频性能监控模块</h2>
          <p>正在开发中...</p>
          <p class="desc">基于WebSocket的实时性能监控展示系统</p>
          <div class="feature-list">
            <span>✓ 毫秒级数据更新</span>
            <span>✓ FPS实时显示</span>
            <span>✓ 内存监控</span>
            <span>✓ 数据吞吐量统计</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import SideNav from '@/components/SideNav.vue'
</script>

<style scoped>
.perf-container {
  display: flex;
  width: 100%;
  height: 100%;
  background: var(--color-bg);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow: auto;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.perf-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(26, 34, 53, 0.5);
  border-radius: 15px;
  border: 2px dashed rgba(0, 170, 255, 0.3);
}

.placeholder-content {
  text-align: center;
  padding: 60px;
}

.placeholder-icon {
  font-size: 80px;
  color: var(--color-primary);
  margin-bottom: 20px;
  animation: blink 1s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.placeholder-content h2 {
  color: var(--color-text);
  font-size: 28px;
  margin-bottom: 15px;
  letter-spacing: 3px;
}

.placeholder-content p {
  color: var(--color-text-dim);
  font-size: 16px;
  margin-bottom: 10px;
}

.placeholder-content .desc {
  font-size: 13px;
  color: #f39c12;
  margin-bottom: 30px;
}

.feature-list {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
}

.feature-list span {
  background: rgba(243, 156, 18, 0.1);
  border: 1px solid rgba(243, 156, 18, 0.3);
  padding: 8px 20px;
  border-radius: 20px;
  color: #f39c12;
  font-size: 13px;
}
</style>
