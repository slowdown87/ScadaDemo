import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Layout, Menu, Badge, Typography } from 'antd';
import {
  DashboardOutlined,
  AppstoreOutlined,
  ExperimentOutlined,
  UnorderedListOutlined,
  HistoryOutlined,
  AlertOutlined,
  CloudOutlined,
} from '@ant-design/icons';
import { useCIPStore } from '@/store';
import './MainLayout.css';

const { Header, Sider, Content } = Layout;
const { Title } = Typography;

const MainLayout: React.FC = () => {
  const location = useLocation();
  const { wsConnected, alarms, systemStatus } = useCIPStore();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: <Link to="/">主监控</Link>,
    },
    {
      key: '/digital-twin',
      icon: <CloudOutlined />,
      label: <Link to="/digital-twin">数字孪生</Link>,
    },
    {
      key: '/recipes',
      icon: <AppstoreOutlined />,
      label: <Link to="/recipes">配方管理</Link>,
    },
    {
      key: '/chemicals',
      icon: <ExperimentOutlined />,
      label: <Link to="/chemicals">清洗剂配置</Link>,
    },
    {
      key: '/queue',
      icon: <UnorderedListOutlined />,
      label: <Link to="/queue">清洗队列</Link>,
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: <Link to="/history">历史记录</Link>,
    },
    {
      key: '/alarms',
      icon: <AlertOutlined />,
      label: (
        <Link to="/alarms">
          报警列表
          {alarms.length > 0 && (
            <Badge count={alarms.length} size="small" offset={[8, 0]} />
          )}
        </Link>
      ),
    },
  ];

  return (
    <Layout className="cip-layout">
      <Sider width={220} className="layout-sider">
        <div className="logo">
          <Title level={4} style={{ color: '#fff', margin: 0 }}>
            CIP SCADA
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          className="layout-menu"
        />
      </Sider>

      <Layout>
        <Header className="layout-header">
          <div className="header-left">
            <Title level={4} style={{ color: '#fff', margin: 0 }}>
              茶饮料生产线 - CIP清洗系统
            </Title>
          </div>
          <div className="header-right">
            <Badge status={wsConnected ? 'success' : 'error'} text={
              <span style={{ color: '#fff' }}>
                {wsConnected ? '已连接' : '未连接'}
              </span>
            } />
            {systemStatus && (
              <>
                <Badge
                  status={systemStatus.running ? 'processing' : 'default'}
                  text={
                    <span style={{ color: '#fff' }}>
                      {systemStatus.running ? '运行中' : '待机'}
                    </span>
                  }
                />
              </>
            )}
          </div>
        </Header>

        <Content className="layout-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
