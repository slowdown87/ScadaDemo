import React from 'react';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { MainDashboard } from '@/pages';
import './App.css';

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <MainDashboard />
    </ConfigProvider>
  );
};

export default App;
