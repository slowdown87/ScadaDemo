<template>
  <div class="about-container">
    <SideNav />
    <main class="main-content">
      <header class="top-bar">
        <div class="header-left">
          <h1 class="page-title">◆ 关于系统</h1>
          <span class="page-subtitle">项目介绍</span>
        </div>
      </header>

      <div class="about-content">
        <div class="info-card">
          <h3>项目信息</h3>
          <div class="info-row">
            <span class="info-label">项目名称:</span>
            <span class="info-value">SCADA智能控制系统</span>
          </div>
          <div class="info-row">
            <span class="info-label">版本号:</span>
            <span class="info-value">v1.0.0</span>
          </div>
          <div class="info-row">
            <span class="info-label">技术栈:</span>
            <span class="info-value">Vue3 + Vite + Element Plus + ECharts + Pinia</span>
          </div>
          <div class="info-row">
            <span class="info-label">部署平台:</span>
            <span class="info-value">GitHub Pages</span>
          </div>
        </div>

        <div class="info-card">
          <h3>功能特性</h3>
          <ul class="feature-list">
            <li>⚡ 电机启停控制</li>
            <li>🌡️ 实时温度监控</li>
            <li>📊 产量自动计数</li>
            <li>📈 温度历史趋势图</li>
            <li>⚠️ 高温报警系统</li>
          </ul>
        </div>

        <div class="info-card">
          <h3>配色方案</h3>
          <div class="color-scheme">
            <div class="color-item">
              <div class="color-box primary"></div>
              <span>科技蓝 #00aaff</span>
            </div>
            <div class="color-item">
              <div class="color-box dark"></div>
              <span>深灰 #121826</span>
            </div>
            <div class="color-item">
              <div class="color-box accent"></div>
              <span>荧光绿 #36d399</span>
            </div>
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
.about-container {
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

.about-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
  flex: 1;
}

.info-card {
  background: var(--color-panel);
  border: 1px solid var(--color-primary);
  border-radius: var(--border-radius);
  padding: 25px;
  box-shadow: var(--box-shadow);
  transition: all 0.3s ease;
}

.info-card:hover {
  box-shadow: 0 0 30px rgba(0, 170, 255, 0.2);
}

.info-card h3 {
  color: var(--color-primary);
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.3);
  letter-spacing: 1px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--color-text-dim);
  font-size: 14px;
}

.info-value {
  color: var(--color-accent);
  font-size: 14px;
  font-weight: 500;
}

.feature-list {
  list-style: none;
}

.feature-list li {
  padding: 10px 0;
  color: var(--color-text);
  font-size: 14px;
  border-bottom: 1px solid rgba(0, 170, 255, 0.1);
}

.feature-list li:last-child {
  border-bottom: none;
}

.color-scheme {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.color-box {
  width: 60px;
  height: 30px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.color-box.primary {
  background: #00aaff;
  box-shadow: 0 0 10px rgba(0, 170, 255, 0.3);
}

.color-box.dark {
  background: #121826;
  border: 1px solid rgba(0, 170, 255, 0.3);
}

.color-box.accent {
  background: #36d399;
  box-shadow: 0 0 10px rgba(54, 211, 153, 0.3);
}

.color-item span {
  color: var(--color-text-dim);
  font-size: 13px;
  letter-spacing: 1px;
}
</style>
