<template>
  <div class="about-container">
    <header class="top-bar">
      <div class="header-left">
        <h1 class="page-title">关于系统</h1>
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
          <span class="info-value">v2.0.0</span>
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
  </div>
</template>

<style scoped>
.about-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: transparent;
  padding: 0;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border-light);
  position: relative;
}

.top-bar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 120px;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), transparent);
  border-radius: 1px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text-primary);
  letter-spacing: 2px;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-title::before {
  content: '◆';
  color: var(--color-primary);
  font-size: 18px;
}

.page-subtitle {
  font-size: 12px;
  color: var(--color-text-tertiary);
  letter-spacing: 1px;
  margin-left: 28px;
}

.about-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
  flex: 1;
  overflow-y: auto;
}

.info-card {
  background: var(--color-bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--color-border-light);
  border-radius: 16px;
  padding: 24px;
  box-shadow: var(--shadow-lg);
  transition: all var(--transition-normal);
  overflow: hidden;
}

.info-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.info-card {
  position: relative;
}

.info-card:hover {
  border-color: var(--color-border-hover);
  transform: translateY(-4px);
  box-shadow: var(--shadow-xl);
}

.info-card:hover::before {
  opacity: 1;
}

.info-card h3 {
  color: var(--color-primary);
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 20px 0;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--color-border-light);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.info-card h3::before {
  content: '◆';
  color: var(--color-primary);
  font-size: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  transition: background var(--transition-fast);
}

.info-row:last-child {
  border-bottom: none;
}

.info-row:hover {
  background: rgba(0, 170, 255, 0.03);
  margin: 0 -12px;
  padding-left: 12px;
  padding-right: 12px;
  border-radius: 6px;
}

.info-label {
  color: var(--color-text-tertiary);
  font-size: 13px;
}

.info-value {
  color: var(--color-text-primary);
  font-size: 13px;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-list li {
  padding: 12px 0;
  color: var(--color-text-primary);
  font-size: 13px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all var(--transition-fast);
}

.feature-list li:last-child {
  border-bottom: none;
}

.feature-list li:hover {
  background: rgba(0, 170, 255, 0.03);
  margin: 0 -12px;
  padding-left: 12px;
  padding-right: 12px;
  border-radius: 6px;
}

.feature-list li::before {
  content: '▸';
  color: var(--color-primary);
  font-size: 10px;
}

.feature-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(0, 170, 255, 0.15), rgba(0, 170, 255, 0.05));
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon svg {
  width: 16px;
  height: 16px;
  color: var(--color-primary);
}

.color-scheme {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.color-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.color-box {
  width: 56px;
  height: 32px;
  border-radius: 8px;
  border: 1px solid var(--color-border-light);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.color-item:hover .color-box {
  transform: scale(1.05);
  box-shadow: var(--shadow-lg);
}

.color-box.primary {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-600));
}

.color-box.dark {
  background: var(--color-bg-secondary);
  border-color: var(--color-border-hover);
}

.color-box.accent {
  background: linear-gradient(135deg, var(--color-accent), var(--color-accent-600));
}

.color-item span {
  color: var(--color-text-secondary);
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

@media (max-width: 1024px) {
  .top-bar {
    flex-direction: column;
    gap: 12px;
  }

  .page-title {
    font-size: 18px;
  }

  .about-content {
    grid-template-columns: 1fr;
  }
}
</style>
