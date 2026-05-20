import React, { useState, useCallback, useEffect } from 'react';
import { Layout, Card, Button, Badge, Space, Typography, Select, Modal, Descriptions, Tag, Divider } from 'antd';
import {
  FullscreenOutlined,
  FullscreenExitOutlined,
  CameraOutlined,
  ReloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useCIPStore } from '@/store';
import { DigitalTwinScene } from '@/components/DigitalTwin';
import type { CleanState } from '@/types';
import './DigitalTwinPage.css';

const { Header, Content } = Layout;
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

// 设备类型
type DeviceType = 'tank' | 'pump' | 'valve' | 'sensor' | null;

interface DeviceInfo {
  id: string;
  type: DeviceType;
  name: string;
  details: Record<string, any>;
}

// 数字孪生页面组件
const DigitalTwinPage: React.FC = () => {
  const { zones, alarms, wsConnected, initialize, cleanup } = useCIPStore();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState<string | undefined>();
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [cameraPreset, setCameraPreset] = useState<string>('overview');

  // 初始化
  useEffect(() => {
    initialize();
    return () => cleanup();
  }, [initialize, cleanup]);

  // 处理设备选择
  const handleDeviceSelect = useCallback((deviceId: string, deviceType: string) => {
    setSelectedDevice(deviceId);
    
    // 模拟设备详细信息（实际应从store或API获取）
    const info: DeviceInfo = {
      id: deviceId,
      type: deviceType as DeviceType,
      name: `设备 ${deviceId}`,
      details: {
        设备ID: deviceId,
        设备类型: deviceType === 'tank' ? '储罐' : 
                  deviceType === 'pump' ? '泵' : 
                  deviceType === 'valve' ? '阀门' : '传感器',
        状态: zones[0]?.state || 'IDLE',
        温度: `${zones[0]?.temp_pv || 0}°C`,
        压力: '3.2 bar',
        流量: `${zones[0]?.flow_pv || 0} m³/h`,
        电导率: `${zones[0]?.conductivity || 0} μS/cm`,
        最后更新: new Date().toLocaleTimeString(),
      },
    };

    setDeviceInfo(info);
    setDetailModalVisible(true);
  }, [zones]);

  // 全屏切换
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  }, []);

  // 重置视角
  const resetCamera = useCallback(() => {
    setCameraPreset('overview');
    // 实际重置由DigitalTwinScene内部控制
  }, []);

  // 相机预设
  const cameraPresets = [
    { value: 'overview', label: '总览' },
    { value: 'raw', label: '原料区' },
    { value: 'process', label: '工艺区' },
    { value: 'clean', label: '清水区' },
  ];

  return (
    <Layout className="digital-twin-page">
      {/* 顶部工具栏 */}
      <Header className="digital-twin-header">
        <div className="header-left">
          <Title level={4} style={{ color: '#fff', margin: 0 }}>
            CIP数字孪生
          </Title>
          <Badge
            status={wsConnected ? 'success' : 'error'}
            text={<Text style={{ color: '#fff' }}>{wsConnected ? '实时同步' : '未连接'}</Text>}
          />
        </div>

        <div className="header-center">
          <Space size="middle">
            <Select
              value={cameraPreset}
              onChange={setCameraPreset}
              options={cameraPresets}
              style={{ width: 120 }}
              dropdownStyle={{ background: '#001529' }}
            />
          </Space>
        </div>

        <div className="header-right">
          <Space size="middle">
            <Button
              type="text"
              icon={<FullscreenOutlined />}
              onClick={toggleFullscreen}
              style={{ color: '#fff' }}
            >
              {isFullscreen ? '退出全屏' : '全屏'}
            </Button>
            <Button
              type="text"
              icon={<CameraOutlined />}
              style={{ color: '#fff' }}
            >
              截图
            </Button>
            <Button
              type="text"
              icon={<ReloadOutlined />}
              onClick={resetCamera}
              style={{ color: '#fff' }}
            >
              重置视角
            </Button>
            <Button
              type="text"
              icon={<SettingOutlined />}
              style={{ color: '#fff' }}
            >
              设置
            </Button>
          </Space>
        </div>
      </Header>

      {/* 3D场景内容 */}
      <Content className="digital-twin-content">
        <div className="digital-twin-container">
          {/* 3D场景 */}
          <div className="scene-container">
            <DigitalTwinScene
              onDeviceSelect={handleDeviceSelect}
              selectedDevice={selectedDevice}
            />
          </div>

          {/* 右侧信息面板 */}
          <div className="info-panel">
            {/* 实时数据卡片 */}
            <Card
              title="实时数据"
              size="small"
              className="info-card"
            >
              <div className="data-grid">
                <div className="data-item">
                  <Text type="secondary">活跃区域</Text>
                  <Text strong>{zones.filter(z => z.state === 'STEP_EXEC').length}</Text>
                </div>
                <div className="data-item">
                  <Text type="secondary">总流量</Text>
                  <Text strong>{zones.reduce((sum, z) => sum + z.flow_pv, 0).toFixed(1)} m³/h</Text>
                </div>
                <div className="data-item">
                  <Text type="secondary">平均温度</Text>
                  <Text strong>{zones.length > 0 ? (zones.reduce((sum, z) => sum + z.temp_pv, 0) / zones.length).toFixed(1) : 0}°C</Text>
                </div>
                <div className="data-item">
                  <Text type="secondary">报警数</Text>
                  <Text strong type={alarms.length > 0 ? 'danger' : undefined}>
                    {alarms.length}
                  </Text>
                </div>
              </div>
            </Card>

            {/* 区域状态 */}
            <Card
              title="区域状态"
              size="small"
              className="info-card"
            >
              <div className="zone-list">
                {zones.map((zone) => (
                  <div key={zone.zone_id} className="zone-item">
                    <Tag color={stateColors[zone.state]}>{zone.zone_name}</Tag>
                    <Text type="secondary">{stateText[zone.state]}</Text>
                    <Text type="secondary">{zone.temp_pv.toFixed(1)}°C</Text>
                  </div>
                ))}
              </div>
            </Card>

            {/* 活跃报警 */}
            <Card
              title="活跃报警"
              size="small"
              className="info-card"
            >
              {alarms.length === 0 ? (
                <Text type="secondary">暂无报警</Text>
              ) : (
                <div className="alarm-list">
                  {alarms.slice(0, 5).map((alarm) => (
                    <div key={alarm.alarm_id} className="alarm-item">
                      <Tag color={alarm.level === 'L1' ? 'red' : alarm.level === 'L2' ? 'orange' : 'yellow'}>
                        {alarm.level}
                      </Tag>
                      <Text style={{ fontSize: '12px' }}>{alarm.alarm_text}</Text>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* 性能指标 */}
            <Card
              title="系统性能"
              size="small"
              className="info-card"
            >
              <div className="performance-grid">
                <div className="perf-item">
                  <Text type="secondary">帧率</Text>
                  <Text strong>60 FPS</Text>
                </div>
                <div className="perf-item">
                  <Text type="secondary">渲染时间</Text>
                  <Text strong>16 ms</Text>
                </div>
                <div className="perf-item">
                  <Text type="secondary">模型数量</Text>
                  <Text strong>26</Text>
                </div>
                <div className="perf-item">
                  <Text type="secondary">多边形</Text>
                  <Text strong>~50K</Text>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </Content>

      {/* 设备详情弹窗 */}
      <Modal
        title={deviceInfo?.name || '设备详情'}
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
          <Button key="control" type="primary">
            设备控制
          </Button>,
        ]}
        width={600}
      >
        {deviceInfo && (
          <div>
            <Descriptions column={2} bordered size="small">
              {Object.entries(deviceInfo.details).map(([key, value]) => (
                <Descriptions.Item key={key} label={key}>
                  {value}
                </Descriptions.Item>
              ))}
            </Descriptions>
            
            <Divider>历史趋势</Divider>
            <div style={{ height: 200, background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Text type="secondary">趋势图表区域</Text>
            </div>
          </div>
        )}
      </Modal>
    </Layout>
  );
};

export default DigitalTwinPage;
