import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainLayout } from '@/pages';
import { MainDashboard } from '@/pages';
import NotFoundPage from './pages/NotFoundPage';
import { Spin } from 'antd';

const RecipePage = lazy(() => import('@/pages/RecipePage'));
const ChemicalsPage = lazy(() => import('@/pages/ChemicalsPage'));
const QueuePage = lazy(() => import('@/pages/QueuePage'));
const HistoryPage = lazy(() => import('@/pages/HistoryPage'));
const AlarmPage = lazy(() => import('@/pages/AlarmPage'));

const LoadingFallback: React.FC = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '400px',
    flexDirection: 'column',
    gap: '16px'
  }}>
    <Spin size="large" />
    <div style={{ color: '#666', fontSize: '14px' }}>页面加载中...</div>
  </div>
);

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Suspense fallback={<LoadingFallback />}>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<MainDashboard />} />
            <Route path="recipes" element={<RecipePage />} />
            <Route path="chemicals" element={<ChemicalsPage />} />
            <Route path="queue" element={<QueuePage />} />
            <Route path="history" element={<HistoryPage />} />
            <Route path="alarms" element={<AlarmPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};

export default App;
