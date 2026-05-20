/**
 * CIP清洗系统 P&ID流程图
 * 
 * 遵循标准：ISO 14617 / ISA S5.1
 * 布局：从左到右，从上到下，清晰的工艺流程
 */

import React, { useState } from 'react';
import { Modal, Descriptions, Tag, Space, Card, Tooltip } from 'antd';
import { useCIPStore } from '@/store';
import './FlowDiagram.css';

interface DeviceDetail {
  type: 'tank' | 'pump' | 'meteringPump' | 'valve' | 'zoneValve' | 'heatExchanger' | 'zone';
  id: string;
  name: string;
  tag?: string;
  data: {
    level?: number;
    temp?: number;
    pressure?: number;
    flow?: number;
    conductivity?: number;
    running?: boolean;
    frequency?: number;
    open?: boolean;
    state?: string;
    currentStep?: number;
    valveType?: 'inlet' | 'return' | 'drain' | 'circulation';
    [key: string]: number | boolean | string | undefined;
  };
}

const FlowDiagram: React.FC = () => {
  const { zones, wsConnected } = useCIPStore();
  const [selectedDevice, setSelectedDevice] = useState<DeviceDetail | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const svgRef = React.useRef<SVGSVGElement>(null);
  const svgWrapperRef = React.useRef<HTMLDivElement>(null);

  const handleZoom = (delta: number) => {
    setZoom(prev => Math.min(Math.max(prev + delta, 0.5), 3));
  };

  const handleReset = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  };

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.05 : 0.05;
    setZoom(prev => Math.min(Math.max(prev + delta, 0.5), 3));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setStartPos({ x: e.clientX - panX, y: e.clientY - panY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPanX(e.clientX - startPos.x);
      setPanY(e.clientY - startPos.y);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleDeviceClick = (device: DeviceDetail) => {
    setSelectedDevice(device);
    setModalVisible(true);
  };

  const renderDeviceDetail = () => {
    if (!selectedDevice) return null;

    const details = [
      { label: '设备编号', value: selectedDevice.id },
      { label: '设备名称', value: selectedDevice.name },
      { label: '位号', value: selectedDevice.tag || 'N/A' },
    ];

    if (selectedDevice.type === 'tank') {
      details.push(
        { label: '设备类型', value: '储罐 (TK)' },
        { label: '液位', value: `${selectedDevice.data.level}%` },
        { label: '温度', value: `${selectedDevice.data.temp}℃` },
        { label: '电导率', value: `${selectedDevice.data.conductivity} μS/cm` }
      );
    } else if (selectedDevice.type === 'pump') {
      details.push(
        { label: '设备类型', value: '离心泵 (P)' },
        { label: '运行状态', value: selectedDevice.data.running ? '运行' : '停止' },
        { label: '频率', value: `${selectedDevice.data.frequency} Hz` },
        { label: '流量', value: `${selectedDevice.data.flow} m³/h` }
      );
    } else if (selectedDevice.type === 'meteringPump') {
      details.push(
        { label: '设备类型', value: '计量泵 (MP)' },
        { label: '运行状态', value: selectedDevice.data.running ? '运行' : '停止' },
        { label: '频率', value: `${selectedDevice.data.frequency || 0} Hz` },
        { label: '流量', value: `${selectedDevice.data.flow || 0} L/h` }
      );
    } else if (selectedDevice.type === 'valve') {
      details.push(
        { label: '阀门状态', value: selectedDevice.data.open ? '开启' : '关闭' }
      );
    } else if (selectedDevice.type === 'zoneValve') {
      const valveTypeMap = {
        'inlet': '进液阀',
        'return': '回流阀',
        'drain': '排放阀',
        'circulation': '循环阀'
      };
      details.push(
        { label: '阀门类型', value: valveTypeMap[selectedDevice.data.valveType as keyof typeof valveTypeMap] || '未知' },
        { label: '阀门状态', value: selectedDevice.data.open ? '开启' : '关闭' }
      );
    } else if (selectedDevice.type === 'heatExchanger') {
      details.push(
        { label: '设备类型', value: '板式换热器 (E)' },
        { label: '温度', value: `${selectedDevice.data.temp}℃` }
      );
    } else if (selectedDevice.type === 'zone') {
      details.push(
        { label: '清洗区域', value: selectedDevice.id },
        { label: '状态', value: selectedDevice.data.state || 'IDLE' },
        { label: '当前步骤', value: `${selectedDevice.data.currentStep || 1}/5` },
        { label: '温度', value: `${selectedDevice.data.temp}℃` },
        { label: '电导率', value: `${selectedDevice.data.conductivity} μS/cm` },
        { label: '流量', value: `${selectedDevice.data.flow} m³/h` }
      );
    }

    return (
      <Descriptions column={2} bordered size="small">
        {details.map((item, index) => (
          <Descriptions.Item key={index} label={item.label}>{item.value}</Descriptions.Item>
        ))}
      </Descriptions>
    );
  };

  return (
    <div className="flow-diagram-container">
      <div className="flow-diagram-header">
        <h3>🍵 CIP清洗系统 P&ID工艺流程图</h3>
        <Space>
          <Tag color={wsConnected ? 'green' : 'red'}>
            {wsConnected ? '🟢 已连接' : '🔴 未连接'}
          </Tag>
          <Tag color="blue">完整工艺流程</Tag>
        </Space>
      </div>

      <Card className="flow-diagram-card">
        <div className="svg-container">
          <div className="svg-controls">
            <button className="zoom-btn" onClick={() => handleZoom(0.1)} title="放大">+</button>
            <span className="zoom-level">{Math.round(zoom * 100)}%</span>
            <button className="zoom-btn" onClick={() => handleZoom(-0.1)} title="缩小">-</button>
            <button className="zoom-btn reset" onClick={() => handleReset()} title="重置">⟲</button>
          </div>
          <div className="svg-wrapper" ref={svgWrapperRef}>
            <svg 
              width="100%" 
              height="950" 
              viewBox="0 0 1400 950" 
              className="pid-diagram"
              ref={svgRef}
              style={{ 
                transform: `scale(${zoom}) translate(${panX}px, ${panY}px)`,
                cursor: isDragging ? 'grabbing' : 'grab'
              }}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              onWheel={handleWheel}
            >
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
            </marker>
            <filter id="deviceShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="2" dy="2" stdDeviation="2" floodOpacity="0.2" />
            </filter>
            <linearGradient id="alkaliTankGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ff9c43" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#ff6b00" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="acidTankGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#a55eea" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#8854d0" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="hotWaterTankGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ff4757" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#c0392b" stopOpacity="0.8" />
            </linearGradient>
            <linearGradient id="pureWaterTankGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#70a1ff" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#1e90ff" stopOpacity="0.8" />
            </linearGradient>
            <style>
              {`
                @keyframes flowAnimation {
                  0% { stroke-dashoffset: 30; }
                  100% { stroke-dashoffset: 0; }
                }
                .pipe-line {
                  animation: flowAnimation 2s linear infinite;
                }
              `}
            </style>
          </defs>

          {/* 背景 */}
          <rect width="100%" height="100%" fill="#fff" />

          {/* ===== 标题 ===== */}
          <text x="700" y="30" textAnchor="middle" fontSize="16" fontWeight="bold" fill="#333">
            CIP清洗系统工艺流程图 (P&ID)
          </text>
          <text x="700" y="50" textAnchor="middle" fontSize="10" fill="#666">
            遵循ISO 14617 / ISA S5.1标准 | 工艺流程：储罐→阀门→泵→换热器→清洗区→排放
          </text>
          <line x1="50" y1="60" x2="1350" y2="60" stroke="#333" strokeWidth="2" />

          {/* ===== 第一行：介质制备系统 ===== */}
          <g transform="translate(50, 75)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">1. 介质制备系统</text>
            <text x="0" y="12" fontSize="8" fill="#666">【起点】</text>

            {/* TK-101 */}
            <g transform="translate(20, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-101', name: '碱液储罐', tag: 'TK-101', data: { level: 85, temp: 85, conductivity: 32 } })} style={{ cursor: 'pointer' }}>
              <Tooltip
                title={
                  <div>
                    <div><strong>传感器配置：</strong></div>
                    <div>TT01 - 温度传感器</div>
                    <div>LT01 - 液位传感器</div>
                    <div>CD01 - 电导率传感器</div>
                  </div>
                }
              >
                <g>
                  <rect x="0" y="0" width="60" height="100" fill="url(#alkaliTankGradient)" stroke="#ff6b00" strokeWidth="2" filter="url(#deviceShadow)" />
                  <ellipse cx="30" cy="0" rx="30" ry="6" fill="#ff6b00" />
                  <ellipse cx="30" cy="100" rx="30" ry="6" fill="#ff6b00" />
                  <rect x="25" y="15" width="10" height="70" fill="rgba(255, 107, 0, 0.4)" />
                  <text x="30" y="115" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-101</text>
                  <text x="30" y="127" textAnchor="middle" fontSize="7" fill="#666">碱液罐</text>
                  <text x="30" y="40" textAnchor="middle" fontSize="11" fill="#fff" fontWeight="bold">85%</text>
                  <text x="30" y="60" textAnchor="middle" fontSize="9" fill="#fff">85℃</text>
                </g>
              </Tooltip>
            </g>

            {/* TK-102 */}
            <g transform="translate(130, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-102', name: '酸液储罐', tag: 'TK-102', data: { level: 72, temp: 60, conductivity: 28 } })} style={{ cursor: 'pointer' }}>
              <Tooltip
                title={
                  <div>
                    <div><strong>传感器配置：</strong></div>
                    <div>TT02 - 温度传感器</div>
                    <div>LT02 - 液位传感器</div>
                    <div>CD02 - 电导率传感器</div>
                  </div>
                }
              >
                <g>
                  <rect x="0" y="0" width="60" height="100" fill="url(#acidTankGradient)" stroke="#8854d0" strokeWidth="2" filter="url(#deviceShadow)" />
                  <ellipse cx="30" cy="0" rx="30" ry="6" fill="#8854d0" />
                  <ellipse cx="30" cy="100" rx="30" ry="6" fill="#8854d0" />
                  <rect x="25" y="28" width="10" height="56" fill="rgba(136, 84, 208, 0.4)" />
                  <text x="30" y="115" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-102</text>
                  <text x="30" y="127" textAnchor="middle" fontSize="7" fill="#666">酸液罐</text>
                  <text x="30" y="40" textAnchor="middle" fontSize="11" fill="#fff" fontWeight="bold">72%</text>
                  <text x="30" y="60" textAnchor="middle" fontSize="9" fill="#fff">60℃</text>
                </g>
              </Tooltip>
            </g>

            {/* TK-103 */}
            <g transform="translate(240, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-103', name: '热水储罐', tag: 'TK-103', data: { level: 95, temp: 85 } })} style={{ cursor: 'pointer' }}>
              <Tooltip
                title={
                  <div>
                    <div><strong>传感器配置：</strong></div>
                    <div>TT03 - 温度传感器</div>
                    <div>LT03 - 液位传感器</div>
                  </div>
                }
              >
                <g>
                  <rect x="0" y="0" width="60" height="100" fill="url(#hotWaterTankGradient)" stroke="#c0392b" strokeWidth="2" filter="url(#deviceShadow)" />
                  <ellipse cx="30" cy="0" rx="30" ry="6" fill="#c0392b" />
                  <ellipse cx="30" cy="100" rx="30" ry="6" fill="#c0392b" />
                  <rect x="25" y="5" width="10" height="80" fill="rgba(192, 57, 43, 0.4)" />
                  <text x="30" y="115" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-103</text>
                  <text x="30" y="127" textAnchor="middle" fontSize="7" fill="#666">热水罐</text>
                  <text x="30" y="40" textAnchor="middle" fontSize="11" fill="#fff" fontWeight="bold">95%</text>
                  <text x="30" y="60" textAnchor="middle" fontSize="9" fill="#fff">85℃</text>
                </g>
              </Tooltip>
            </g>

            {/* TK-104 */}
            <g transform="translate(350, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-104', name: '纯水储罐', tag: 'TK-104', data: { level: 88, temp: 25 } })} style={{ cursor: 'pointer' }}>
              <Tooltip
                title={
                  <div>
                    <div><strong>传感器配置：</strong></div>
                    <div>TT04 - 温度传感器</div>
                    <div>LT04 - 液位传感器</div>
                  </div>
                }
              >
                <g>
                  <rect x="0" y="0" width="60" height="100" fill="url(#pureWaterTankGradient)" stroke="#1e90ff" strokeWidth="2" filter="url(#deviceShadow)" />
                  <ellipse cx="30" cy="0" rx="30" ry="6" fill="#1e90ff" />
                  <ellipse cx="30" cy="100" rx="30" ry="6" fill="#1e90ff" />
                  <rect x="25" y="12" width="10" height="72" fill="rgba(30, 144, 255, 0.4)" />
                  <text x="30" y="115" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-104</text>
                  <text x="30" y="127" textAnchor="middle" fontSize="7" fill="#666">纯水罐</text>
                  <text x="30" y="40" textAnchor="middle" fontSize="11" fill="#fff" fontWeight="bold">88%</text>
                  <text x="30" y="60" textAnchor="middle" fontSize="9" fill="#fff">25℃</text>
                </g>
              </Tooltip>
            </g>
          </g>

          {/* 管道：储罐→计量泵 */}
          <path d="M 110 230 L 110 250 L 130 250 L 130 270" fill="none" stroke="#ff6b00" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          <path d="M 220 230 L 220 250 L 220 270" fill="none" stroke="#8854d0" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />

          {/* ===== 计量泵组 ===== */}
          <g transform="translate(50, 270)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">计量泵组</text>

            {/* P-CP06 碱液添加泵 */}
            <g transform="translate(20, 20)" onClick={() => handleDeviceClick({ type: 'meteringPump', id: 'P-CP06', name: '碱液添加泵', tag: 'P-CP06', data: { running: zones.some(z => z?.current_media === 'CAUSTIC' && z?.pump_running), frequency: 50, flow: 50 } })} style={{ cursor: 'pointer' }}>
              <ellipse cx="25" cy="30" rx="22" ry="15" fill={zones.some(z => z?.current_media === 'CAUSTIC' && z?.pump_running) ? '#ff6b00' : '#fff'} stroke="#ff6b00" strokeWidth="2" filter="url(#deviceShadow)" />
              <text x="25" y="35" textAnchor="middle" fontSize="12" fontWeight="bold" fill={zones.some(z => z?.current_media === 'CAUSTIC' && z?.pump_running) ? '#fff' : '#ff6b00'}>MP</text>
              <text x="25" y="60" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">P-CP06</text>
              <text x="25" y="72" textAnchor="middle" fontSize="7" fill="#666">碱液添加</text>
              <text x="25" y="84" textAnchor="middle" fontSize="8" fill={zones.some(z => z?.current_media === 'CAUSTIC' && z?.pump_running) ? '#52c41a' : '#999'}>
                {zones.some(z => z?.current_media === 'CAUSTIC' && z?.pump_running) ? '▶ 运行' : '■ 待机'}
              </text>
            </g>

            {/* P-CP07 酸液添加泵 */}
            <g transform="translate(150, 20)" onClick={() => handleDeviceClick({ type: 'meteringPump', id: 'P-CP07', name: '酸液添加泵', tag: 'P-CP07', data: { running: zones.some(z => z?.current_media === 'ACID' && z?.pump_running), frequency: 50, flow: 50 } })} style={{ cursor: 'pointer' }}>
              <ellipse cx="25" cy="30" rx="22" ry="15" fill={zones.some(z => z?.current_media === 'ACID' && z?.pump_running) ? '#8854d0' : '#fff'} stroke="#8854d0" strokeWidth="2" filter="url(#deviceShadow)" />
              <text x="25" y="35" textAnchor="middle" fontSize="12" fontWeight="bold" fill={zones.some(z => z?.current_media === 'ACID' && z?.pump_running) ? '#fff' : '#8854d0'}>MP</text>
              <text x="25" y="60" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">P-CP07</text>
              <text x="25" y="72" textAnchor="middle" fontSize="7" fill="#666">酸液添加</text>
              <text x="25" y="84" textAnchor="middle" fontSize="8" fill={zones.some(z => z?.current_media === 'ACID' && z?.pump_running) ? '#52c41a' : '#999'}>
                {zones.some(z => z?.current_media === 'ACID' && z?.pump_running) ? '▶ 运行' : '■ 待机'}
              </text>
            </g>
          </g>

          {/* 管道：计量泵→阀门 */}
          <path d="M 95 375 L 95 395 L 110 395 L 110 415" fill="none" stroke="#ff6b00" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          <path d="M 195 375 L 195 395 L 220 395 L 220 415" fill="none" stroke="#8854d0" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          <path d="M 330 230 L 330 415" fill="none" stroke="#c0392b" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          <path d="M 440 230 L 440 415" fill="none" stroke="#1e90ff" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />

          {/* ===== 公用介质阀组 ===== */}
          <g transform="translate(50, 415)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">2. 公用介质阀组</text>

            {/* M-V-01 */}
            <g transform="translate(20, 20)" onClick={() => handleDeviceClick({ type: 'valve', id: 'M-V-01', name: '碱液进水阀', tag: 'M-V-01', data: { open: zones[0]?.current_media === 'CAUSTIC' } })} style={{ cursor: 'pointer' }}>
              <circle cx="20" cy="20" r="15" fill={zones[0]?.current_media === 'CAUSTIC' ? '#ff6b00' : '#fff'} stroke="#ff6b00" strokeWidth="2" />
              <polygon points="20,7 28,20 20,33" fill={zones[0]?.current_media === 'CAUSTIC' ? '#fff' : '#ff6b00'} />
              <text x="20" y="50" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">M-V-01</text>
              <text x="20" y="62" textAnchor="middle" fontSize="7" fill="#666">碱液</text>
            </g>

            {/* M-V-02 */}
            <g transform="translate(130, 20)" onClick={() => handleDeviceClick({ type: 'valve', id: 'M-V-02', name: '酸液进水阀', tag: 'M-V-02', data: { open: zones[0]?.current_media === 'ACID' } })} style={{ cursor: 'pointer' }}>
              <circle cx="20" cy="20" r="15" fill={zones[0]?.current_media === 'ACID' ? '#8854d0' : '#fff'} stroke="#8854d0" strokeWidth="2" />
              <polygon points="20,7 28,20 20,33" fill={zones[0]?.current_media === 'ACID' ? '#fff' : '#8854d0'} />
              <text x="20" y="50" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">M-V-02</text>
              <text x="20" y="62" textAnchor="middle" fontSize="7" fill="#666">酸液</text>
            </g>

            {/* M-V-03 */}
            <g transform="translate(240, 20)" onClick={() => handleDeviceClick({ type: 'valve', id: 'M-V-03', name: '热水进水阀', tag: 'M-V-03', data: { open: zones[0]?.current_media === 'HOT_WATER' } })} style={{ cursor: 'pointer' }}>
              <circle cx="20" cy="20" r="15" fill={zones[0]?.current_media === 'HOT_WATER' ? '#c0392b' : '#fff'} stroke="#c0392b" strokeWidth="2" />
              <polygon points="20,7 28,20 20,33" fill={zones[0]?.current_media === 'HOT_WATER' ? '#fff' : '#c0392b'} />
              <text x="20" y="50" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">M-V-03</text>
              <text x="20" y="62" textAnchor="middle" fontSize="7" fill="#666">热水</text>
            </g>

            {/* M-V-04 */}
            <g transform="translate(350, 20)" onClick={() => handleDeviceClick({ type: 'valve', id: 'M-V-04', name: '纯水进水阀', tag: 'M-V-04', data: { open: zones[0]?.current_media === 'PURE_WATER' } })} style={{ cursor: 'pointer' }}>
              <circle cx="20" cy="20" r="15" fill={zones[0]?.current_media === 'PURE_WATER' ? '#1e90ff' : '#fff'} stroke="#1e90ff" strokeWidth="2" />
              <polygon points="20,7 28,20 20,33" fill={zones[0]?.current_media === 'PURE_WATER' ? '#fff' : '#1e90ff'} />
              <text x="20" y="50" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">M-V-04</text>
              <text x="20" y="62" textAnchor="middle" fontSize="7" fill="#666">纯水</text>
            </g>

            {/* M-V-05 循环阀 */}
            <g transform="translate(460, 20)" onClick={() => handleDeviceClick({ type: 'valve', id: 'M-V-05', name: '循环阀', tag: 'M-V-05', data: { open: false } })} style={{ cursor: 'pointer' }}>
              <circle cx="20" cy="20" r="15" fill="#fff" stroke="#2ecc71" strokeWidth="2" />
              <polygon points="20,7 28,20 20,33" fill="#2ecc71" />
              <text x="20" y="50" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">M-V-05</text>
              <text x="20" y="62" textAnchor="middle" fontSize="7" fill="#666">循环</text>
            </g>

            {/* M-V-06 排放总阀 */}
            <g transform="translate(570, 20)" onClick={() => handleDeviceClick({ type: 'valve', id: 'M-V-06', name: '排放总阀', tag: 'M-V-06', data: { open: false } })} style={{ cursor: 'pointer' }}>
              <circle cx="20" cy="20" r="15" fill="#fff" stroke="#e91e63" strokeWidth="2" />
              <polygon points="20,7 28,20 20,33" fill="#e91e63" />
              <text x="20" y="50" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">M-V-06</text>
              <text x="20" y="62" textAnchor="middle" fontSize="7" fill="#666">排放总</text>
            </g>
          </g>

          {/* 管道：阀门→泵 */}
          <path d="M 110 535 L 110 555" fill="none" stroke="#ff6b00" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          <path d="M 220 535 L 220 555" fill="none" stroke="#8854d0" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          <path d="M 330 535 L 330 555" fill="none" stroke="#c0392b" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          <path d="M 440 535 L 440 555" fill="none" stroke="#1e90ff" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />

          {/* ===== 清洗泵组 ===== */}
          <g transform="translate(50, 555)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">3. 清洗泵组</text>

            {[0, 1, 2, 3, 4].map((index) => (
              <g key={index} transform={`translate(${20 + index * 85}, 20)}`} onClick={() => handleDeviceClick({ type: 'pump', id: `P-CP0${index + 1}`, name: `${index + 1}区清洗泵`, tag: `P-CP0${index + 1}`, data: { running: zones[index]?.pump_running || false, frequency: 50, flow: zones[index]?.flow_pv || 0 } })} style={{ cursor: 'pointer' }}>
                <circle cx="25" cy="30" r="22" fill="#fff" stroke="#52c41a" strokeWidth="2" filter="url(#deviceShadow)" />
                <circle cx="25" cy="30" r="13" fill="#fff" stroke="#52c41a" strokeWidth="1" />
                <text x="25" y="35" textAnchor="middle" fontSize="14" fontWeight="bold" fill="#52c41a">P</text>
                <text x="25" y="68" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">P-CP0{index + 1}</text>
                <text x="25" y="80" textAnchor="middle" fontSize="8" fill="#666">Zone-{index + 1}</text>
                <text x="25" y="98" textAnchor="middle" fontSize="9" fill={zones[index]?.pump_running ? '#52c41a' : '#999'}>
                  {zones[index]?.pump_running ? '▶ 运行' : '■ 待机'}
                </text>
              </g>
            ))}
          </g>

          {/* 管道：泵→每区阀门 */}
          {[0, 1, 2, 3, 4].map((index) => (
            <path key={index} d={`M ${110 + index * 85} 715 L ${110 + index * 85} 735}`} fill="none" stroke="#52c41a" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />
          ))}

          {/* ===== 每区阀门组 ===== */}
          <g transform="translate(50, 735)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">4. 每区阀门组</text>
            <text x="0" y="12" fontSize="8" fill="#666">（进液/回流/排放/循环）</text>

            {['#4caf50', '#ff9800', '#2196f3', '#e91e63', '#9c27b0'].map((color, zoneIndex) => (
              <g key={`zone-valves-${zoneIndex}`} transform={`translate(${20 + zoneIndex * 160}, 25)}`}>
                <text x="50" y="0" textAnchor="middle" fontSize="10" fontWeight="bold" fill={color}>
                  Zone-{zoneIndex + 1}
                </text>

                {[
                  { id: `Z${zoneIndex+1}-V-01`, name: '进液', valveColor: '#52c41a', type: 'inlet' as const, isOpen: zones[zoneIndex]?.pump_running },
                  { id: `Z${zoneIndex+1}-V-02`, name: '回流', valveColor: '#ff9800', type: 'return' as const, isOpen: zones[zoneIndex]?.pump_running },
                  { id: `Z${zoneIndex+1}-V-03`, name: '排放', valveColor: '#e91e63', type: 'drain' as const, isOpen: false },
                  { id: `Z${zoneIndex+1}-V-04`, name: '循环', valveColor: '#2ecc71', type: 'circulation' as const, isOpen: false }
                ].map((valve, valveIndex) => (
                  <g key={valve.id} transform={`translate(0, ${valveIndex * 25})`} onClick={() => handleDeviceClick({ type: 'zoneValve', id: valve.id, name: `${zoneIndex + 1}区${valve.name}阀`, tag: valve.id, data: { open: valve.isOpen, valveType: valve.type } })} style={{ cursor: 'pointer' }}>
                    <rect x="0" y="0" width="100" height="20" fill={valve.isOpen ? valve.valveColor : '#fff'} stroke={valve.valveColor} strokeWidth="1.5" rx="3" />
                    <text x="8" y="14" fontSize="8" fontWeight="bold" fill={valve.isOpen ? '#fff' : valve.valveColor}>{valve.id}</text>
                    <text x="60" y="14" fontSize="7" fill={valve.isOpen ? '#fff' : '#666'}>{valve.name}</text>
                    <circle cx="90" cy="10" r="4" fill={valve.valveColor} opacity={valve.isOpen ? 1 : 0.5} />
                  </g>
                ))}
              </g>
            ))}
          </g>

          {/* 管道：每区阀门→换热器 */}
          <path d="M 240 830 L 240 850 L 650 850 L 650 870" fill="none" stroke="#52c41a" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />

          {/* ===== 换热器 ===== */}
          <g transform="translate(580, 870)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">5. 板式换热器</text>

            <g transform="translate(0, 20)" onClick={() => handleDeviceClick({ type: 'heatExchanger', id: 'E-101', name: '板式换热器', tag: 'E-101', data: { temp: 85 } })} style={{ cursor: 'pointer' }}>
              <rect x="0" y="0" width="80" height="70" fill="#fff" stroke="#333" strokeWidth="2" filter="url(#deviceShadow)" />
              <line x1="0" y1="17" x2="80" y2="17" stroke="#333" strokeWidth="1" />
              <line x1="0" y1="35" x2="80" y2="35" stroke="#333" strokeWidth="1" />
              <line x1="0" y1="52" x2="80" y2="52" stroke="#333" strokeWidth="1" />
              <circle cx="-6" cy="8" r="4" fill="#333" />
              <circle cx="86" cy="8" r="4" fill="#333" />
              <circle cx="-6" cy="61" r="4" fill="#333" />
              <circle cx="86" cy="61" r="4" fill="#333" />
              <text x="40" y="85" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">E-101</text>
              <text x="40" y="97" textAnchor="middle" fontSize="8" fill="#666">板式换热器</text>
            </g>
          </g>

          {/* 管道：换热器→清洗区 */}
          <path d="M 740 915 L 740 935" fill="none" stroke="#52c41a" strokeWidth="3" className="pipe-line" markerEnd="url(#arrowhead)" />

          {/* ===== 清洗对象 ===== */}
          <g transform="translate(50, 935)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#333">6. 清洗对象</text>
            <text x="0" y="12" fontSize="8" fill="#666">【终点】</text>

            {['e8f5e9', 'fff3e0', 'e3f2fd', 'fce4ec', 'f3e5f5'].map((color, index) => {
              const zoneColors = ['#4caf50', '#ff9800', '#2196f3', '#e91e63', '#9c27b0'];
              const zoneEquipment = ['WT-101~201', 'TH/EX-101~106', 'BL-101~106', 'UH-101~106', 'PF-101~106'];
              const zoneNames = ['水处理系统', '茶叶萃取系统', '调配系统', 'UHT杀菌系统', '灌装设备'];

              return (
                <g key={index} transform={`translate(${20 + index * 160}, 25)}`} onClick={() => handleDeviceClick({ type: 'zone', id: `Zone-${index + 1}`, name: zoneNames[index], tag: `CIP-Z${index + 1}`, data: { state: zones[index]?.state || 'IDLE', currentStep: zones[index]?.current_step || 1, temp: zones[index]?.temp_pv || 0, conductivity: zones[index]?.conductivity || 0, flow: zones[index]?.flow_pv || 0 } })} style={{ cursor: 'pointer' }}>
                  <Tooltip
                    title={
                      <div>
                        <div><strong>传感器配置：</strong></div>
                        <div>TT-{index+1}-01 - 进液温度</div>
                        <div>TT-{index+1}-02 - 回液温度</div>
                        <div>PT-{index+1}-01 - 压力传感器</div>
                        <div>FT-{index+1}-01 - 流量传感器</div>
                        <div>CD-{index+1}-01 - 电导率传感器</div>
                      </div>
                    }
                  >
                    <g>
                      <rect x="0" y="0" width="140" height="140" fill={`#${color}`} stroke={zoneColors[index]} strokeWidth="2" rx="5" filter="url(#deviceShadow)" />
                      <text x="70" y="20" textAnchor="middle" fontSize="11" fontWeight="bold" fill="#333">Zone-{index + 1}</text>
                      <text x="70" y="35" textAnchor="middle" fontSize="8" fill="#666">{zoneNames[index]}</text>
                      <line x1="10" y1="45" x2="130" y2="45" stroke="#ddd" strokeWidth="1" />
                      <text x="70" y="62" textAnchor="middle" fontSize="10" fill={zoneColors[index]} fontWeight="bold">{zoneEquipment[index]}</text>
                      <line x1="10" y1="72" x2="130" y2="72" stroke="#ddd" strokeWidth="1" />

                      <text x="15" y="90" fontSize="8" fill="#333">温度:</text>
                      <text x="125" y="90" textAnchor="end" fontSize="9" fontWeight="bold" fill="#ff6b00">
                        {zones[index]?.temp_pv?.toFixed(1) || '0.0'}℃
                      </text>

                      <text x="15" y="108" fontSize="8" fill="#333">电导:</text>
                      <text x="125" y="108" textAnchor="end" fontSize="9" fontWeight="bold" fill="#8854d0">
                        {zones[index]?.conductivity?.toFixed(1) || '0.0'}
                      </text>

                      <text x="15" y="126" fontSize="8" fill="#333">流量:</text>
                      <text x="125" y="126" textAnchor="end" fontSize="9" fontWeight="bold" fill="#1e90ff">
                        {zones[index]?.flow_pv?.toFixed(2) || '0.00'}
                      </text>
                    </g>
                  </Tooltip>
                </g>
              );
            })}
          </g>

          {/* 管道：清洗区→排放 */}
          {[0, 1, 2, 3, 4].map((index) => (
            <path key={index} d={`M ${210 + index * 160} 1100 L ${210 + index * 160} 1115}`} fill="none" stroke="#e91e63" strokeWidth="2" className="pipe-line" markerEnd="url(#arrowhead)" />
          ))}

          {/* 排放系统 */}
          <g transform="translate(1050, 935)">
            <text x="0" y="0" fontSize="12" fontWeight="bold" fill="#e91e63">7. 排放系统</text>
            <rect x="20" y="20" width="80" height="160" fill="#fff" stroke="#e91e63" strokeWidth="2" rx="5" />
            <text x="60" y="50" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#e91e63">排放</text>
            <text x="60" y="65" textAnchor="middle" fontSize="8" fill="#666">系统</text>
            <line x1="60" y1="80" x2="60" y2="160" stroke="#e91e63" strokeWidth="4" className="pipe-line" markerEnd="url(#arrowhead)" />
            <text x="60" y="180" textAnchor="middle" fontSize="8" fill="#666">DN100</text>
          </g>

          {/* ===== 图例 ===== */}
          <g transform="translate(50, 1130)">
            <rect x="0" y="0" width="1200" height="40" fill="#fff" stroke="#ddd" strokeWidth="1" rx="3" />
            <text x="10" y="15" fontSize="9" fontWeight="bold" fill="#333">图例</text>

            {/* 储罐 */}
            <rect x="50" y="8" width="18" height="14" fill="url(#alkaliTankGradient)" stroke="#ff6b00" strokeWidth="1" />
            <text x="75" y="19" fontSize="8" fill="#333">储罐</text>

            {/* 泵 */}
            <circle cx="130" cy="15" r="7" fill="#fff" stroke="#52c41a" strokeWidth="1.5" />
            <text x="130" y="18" textAnchor="middle" fontSize="6" fontWeight="bold" fill="#52c41a">P</text>
            <text x="145" y="19" fontSize="8" fill="#333">离心泵</text>

            {/* 计量泵 */}
            <ellipse cx="220" cy="15" rx="10" ry="6" fill="#fff" stroke="#ff6b00" strokeWidth="1.5" />
            <text x="220" y="18" textAnchor="middle" fontSize="5" fontWeight="bold" fill="#ff6b00">MP</text>
            <text x="240" y="19" fontSize="8" fill="#333">计量泵</text>

            {/* 阀门 */}
            <circle cx="320" cy="15" r="6" fill="#fff" stroke="#333" strokeWidth="1.5" />
            <polygon points="320,10 326,15 320,20" fill="#333" />
            <text x="335" y="19" fontSize="8" fill="#333">调节阀</text>

            {/* 换热器 */}
            <rect x="420" y="8" width="22" height="14" fill="#fff" stroke="#333" strokeWidth="1" />
            <text x="450" y="19" fontSize="8" fill="#333">换热器</text>

            {/* 管道流向 */}
            <line x1="530" y1="15" x2="560" y2="15" stroke="#333" strokeWidth="2" className="pipe-line" markerEnd="url(#arrowhead)" />
            <text x="570" y="19" fontSize="8" fill="#333">管道流向</text>

            {/* 介质颜色 */}
            <text x="670" y="12" fontSize="7" fill="#666">介质:</text>
            <circle cx="705" cy="15" r="5" fill="#ff6b00" />
            <text x="715" y="19" fontSize="7" fill="#333">碱液</text>
            <circle cx="750" cy="15" r="5" fill="#8854d0" />
            <text x="760" y="19" fontSize="7" fill="#333">酸液</text>
            <circle cx="795" cy="15" r="5" fill="#c0392b" />
            <text x="805" y="19" fontSize="7" fill="#333">热水</text>
            <circle cx="840" cy="15" r="5" fill="#1e90ff" />
            <text x="850" y="19" fontSize="7" fill="#333">纯水</text>
            <circle cx="885" cy="15" r="5" fill="#52c41a" />
            <text x="895" y="19" fontSize="7" fill="#333">清洗液</text>
            <circle cx="935" cy="15" r="5" fill="#e91e63" />
            <text x="945" y="19" fontSize="7" fill="#333">排放</text>
          </g>

          {/* ===== 设计信息 ===== */}
          <line x1="50" y1="1175" x2="1350" y2="1175" stroke="#333" strokeWidth="1" />
          <text x="60" y="1188" fontSize="7" fill="#666">设计标准: ISO 14617 / ISA S5.1 | 图号: CIP-PID-001 | 版本: V1.1（增加计量泵和每区阀门）</text>
          <text x="1350" y="1188" textAnchor="end" fontSize="7" fill="#666">第1张 共1张</text>
        </svg>
          </div>
        </div>
      </Card>

      {/* 设备详情弹窗 */}
      <Modal
        title={`📋 ${selectedDevice?.name || '设备详情'}`}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        {renderDeviceDetail()}
      </Modal>
    </div>
  );
};

export default FlowDiagram;
