import React, { useEffect } from 'react';
import { Layout, Typography, Card, Row, Col, Statistic, Badge, Space, Tag, Progress } from 'antd';
import { AlertOutlined, ApiOutlined, UserOutlined, SettingOutlined } from '@ant-design/icons';
import { useCIPStore } from '@/store';
import type { ZoneStatus, CleanState } from '@/types';
import './MainDashboard.css';

const { Header, Content, Footer } = Layout;
const { Title, Text } = Typography;

// 状态颜色映射
const stateColors: Record<CleanState, string> = {
  IDLE: '#8c8c8c',
  READY: '#1890ff',
  STEP_EXEC: '#52c41a',
  PAUSE: '#faad14',
  FAULT: '#ff4d4f',
};

const stateText: Record<CleanState, string> = {
  IDLE: '待机',
  READY: '就绪',
  STEP_EXEC: '清洗中',
  PAUSE: '暂停',
  FAULT: '故障',
};

const mediaText: Record<string, string> = {
  PURE_WATER: '纯水',
  CAUSTIC: '碱液',
  ACID: '酸液',
  HOT_WATER: '热水',
  DISINFECTANT: '消毒液',
};

const MainDashboard: React.FC = () => {
  const { zones, alarms, systemStatus, wsConnected, selectedZones, toggleZone, initialize, cleanup } = useCIPStore();

  useEffect(() => {
    initialize();
    return () => cleanup();
  }, [initialize, cleanup]);

  const selectedZone = zones.find((z) => z.zone_id === selectedZones[0]);

  return (
    <Layout className="cip-dashboard">
      {/* 顶部导航 */}
      <Header className="dashboard-header">
        <div className="header-content">
          <Title level={4} style={{ color: '#fff', margin: 0 }}>CIP清洗系统控制</Title>
          <Space size="large">
            <Badge status={wsConnected ? 'success' : 'error'} text={<Text style={{ color: '#fff' }}>{wsConnected ? '已连接' : '未连接'}</Text>} />
            <Text style={{ color: '#fff' }}><UserOutlined /> 操作员</Text>
          </Space>
        </div>
      </Header>

      <Content className="dashboard-content">
        <Row gutter={16}>
          {/* 左侧：5区状态卡片 */}
          <Col span={16}>
            <Card title="清洗区域状态" className="zones-card">
              <Row gutter={16}>
                {zones.map((zone) => (
                  <Col span={4} key={zone.zone_id}>
                    <ZoneCard 
                      zone={zone} 
                      selected={selectedZones.includes(zone.zone_id)}
                      onClick={() => toggleZone(zone.zone_id)}
                    />
                  </Col>
                ))}
              </Row>
            </Card>

            {/* 选中区域详情 */}
            {selectedZone && (
              <Card title={`${selectedZone.zone_name} - 详细信息`} className="zone-detail-card" style={{ marginTop: 16 }}>
                <Row gutter={24}>
                  <Col span={6}>
                    <Statistic 
                      title="当前状态" 
                      value={stateText[selectedZone.state]} 
                      valueStyle={{ color: stateColors[selectedZone.state] }}
                    />
                  </Col>
                  <Col span={6}>
                    <Statistic title="当前步骤" value={`${selectedZone.current_step} / 5`} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="当前介质" value={mediaText[selectedZone.current_media] || selectedZone.current_media} />
                  </Col>
                  <Col span={6}>
                    <Statistic 
                      title="温度" 
                      value={selectedZone.temp_pv} 
                      suffix="℃" 
                      precision={1}
                      valueStyle={{ color: selectedZone.temp_reached ? '#52c41a' : '#faad14' }}
                      suffix={selectedZone.temp_reached ? ' ✓' : ''}
                    />
                  </Col>
                </Row>
                <Row gutter={24} style={{ marginTop: 16 }}>
                  <Col span={6}>
                    <Statistic title="温度设定" value={selectedZone.temp_sp} suffix="℃" precision={1} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="电导率" value={selectedZone.conductivity} suffix="μS/cm" precision={1} />
                  </Col>
                  <Col span={6}>
                    <Statistic title="流量" value={selectedZone.flow_pv} suffix="m³/h" precision={2} />
                  </Col>
                  <Col span={6}>
                    <Statistic 
                      title="泵运行" 
                      value={selectedZone.pump_running ? '运行中' : '停止'} 
                      valueStyle={{ color: selectedZone.pump_running ? '#52c41a' : '#8c8c8c' }}
                    />
                  </Col>
                </Row>
                <div style={{ marginTop: 16 }}>
                  <Text>清洗进度: </Text>
                  <Progress 
                    percent={Math.round((selectedZone.current_step / 5) * 100)} 
                    status={selectedZone.state === 'FAULT' ? 'exception' : 'active'}
                    strokeColor={stateColors[selectedZone.state]}
                  />
                  <Text style={{ marginLeft: 16 }}>剩余时间: {Math.floor(selectedZone.step_time_remaining / 60)}分{selectedZone.step_time_remaining % 60}秒</Text>
                </div>
              </Card>
            )}
          </Col>

          {/* 右侧：报警和系统状态 */}
          <Col span={8}>
            <Card title={<><AlertOutlined /> 活跃报警</>} className="alarms-card">
              {alarms.length === 0 ? (
                <Text type="secondary">暂无报警</Text>
              ) : (
                alarms.slice(0, 5).map((alarm) => (
                  <div key={alarm.alarm_id} className="alarm-item">
                    <Tag color={alarm.level === 'L1' ? 'red' : alarm.level === 'L2' ? 'orange' : 'yellow'}>
                      {alarm.level}
                    </Tag>
                    <Text>{alarm.alarm_text}</Text>
                  </div>
                ))
              )}
            </Card>

            <Card title="系统概览" className="system-card" style={{ marginTop: 16 }}>
              <Statistic 
                title="运行状态" 
                value={systemStatus?.running ? '运行中' : '待机'} 
                valueStyle={{ color: systemStatus?.running ? '#52c41a' : '#8c8c8c' }}
              />
              <Row gutter={16} style={{ marginTop: 16 }}>
                <Col span={12}>
                  <Statistic title="活跃区域" value={systemStatus?.active_zones || 0} />
                </Col>
                <Col span={12}>
                  <Statistic title="报警数量" value={systemStatus?.alarm_count || 0} />
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      </Content>

      <Footer className="dashboard-footer">
        <Space>
          <Badge status={wsConnected ? 'success' : 'error'} />
          <Text>PLC连接: {wsConnected ? '正常' : '断开'}</Text>
          <Text>|</Text>
          <Text>1区泵: {zones[0]?.pump_running ? '运行' : '停止'}</Text>
          <Text>|</Text>
          <Text>当前用户: 操作员</Text>
          <Text>|</Text>
          <Text>{new Date().toLocaleTimeString()}</Text>
        </Space>
      </Footer>
    </Layout>
  );
};

// Zone卡片组件
interface ZoneCardProps {
  zone: ZoneStatus;
  selected: boolean;
  onClick: () => void;
}

const ZoneCard: React.FC<ZoneCardProps> = ({ zone, selected, onClick }) => {
  return (
    <Card 
      className={`zone-card ${selected ? 'selected' : ''}`}
      onClick={onClick}
      style={{ 
        borderColor: selected ? '#1890ff' : undefined,
        borderWidth: selected ? 2 : 1,
      }}
    >
      <div className="zone-header">
        <Text strong>{zone.zone_name}</Text>
        <Tag color={stateColors[zone.state]}>{stateText[zone.state]}</Tag>
      </div>
      <div className="zone-progress">
        <Progress 
          percent={Math.round((zone.current_step / 5) * 100)} 
          size="small"
          strokeColor={stateColors[zone.state]}
          showInfo={false}
        />
        <Text type="secondary" style={{ fontSize: 12 }}>
          {zone.current_step}/5步
        </Text>
      </div>
      <div className="zone-info">
        <Text style={{ fontSize: 12 }}>温度: {zone.temp_pv.toFixed(1)}℃</Text>
        <Text style={{ fontSize: 12 }}>电导: {zone.conductivity.toFixed(1)}</Text>
      </div>
    </Card>
  );
};

export default MainDashboard;
