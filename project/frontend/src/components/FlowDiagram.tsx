/**
 * CIP清洗系统 P&ID工艺流程图 - 专业完整版
 * 
 * 遵循标准：ISO 14617 / ISA S5.1
 * 完整工艺流程：介质制备 → 公用阀组 → 清洗泵 → 板式换热器 → 各区阀门 → 清洗对象 → 排放
 */

import React, { useState } from 'react';
import { Modal, Descriptions, Tag, Tooltip } from 'antd';
import { useCIPStore } from '@/store';
import './FlowDiagram.css';

interface DeviceDetail {
  type: string;
  id: string;
  name: string;
  tag?: string;
  data: Record<string, any>;
}

const FlowDiagram: React.FC = () => {
  const { zones } = useCIPStore();
  const [selectedDevice, setSelectedDevice] = useState<DeviceDetail | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [zoom, setZoom] = useState(0.8);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });

  const handleDeviceClick = (device: DeviceDetail) => {
    setSelectedDevice(device);
    setModalVisible(true);
  };

  const handleZoom = (delta: number) => {
    setZoom(prev => Math.min(Math.max(prev + delta, 0.3), 2));
  };

  const handleReset = () => {
    setZoom(0.8);
    setPanX(0);
    setPanY(0);
  };

  const handleWheel = (e: React.WheelEvent) => {
    if (e.ctrlKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? -0.05 : 0.05;
      setZoom(prev => Math.min(Math.max(prev + delta, 0.3), 2));
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsDragging(true);
      setStartPos({ x: e.clientX - panX, y: e.clientY - panY });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPanX(e.clientX - startPos.x);
      setPanY(e.clientY - startPos.y);
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const getZoneColor = (index: number) => ['#4caf50', '#ff9800', '#2196f3', '#e91e63', '#9c27b0'][index];
  const getZoneName = (index: number) => ['水处理系统', '茶叶萃取系统', '调配系统', 'UHT杀菌系统', '灌装设备'][index];
  const getZoneEquipment = (index: number) => ['WT-101~201', 'TH/EX-101~106', 'BL-101~106', 'UH-101~106', 'PF-101~106'][index];
  const getZoneBgColor = (index: number) => ['#e8f5e9', '#fff3e0', '#e3f2fd', '#fce4ec', '#f3e5f5'][index];

  return (
    <div style={{ width: '100%', height: '100%', overflow: 'hidden', position: 'relative' }}>
      <div
        style={{
          position: 'absolute',
          top: 16,
          right: 16,
          zIndex: 100,
          display: 'flex',
          gap: 8,
          background: 'rgba(255,255,255,0.95)',
          padding: '8px 12px',
          borderRadius: 8,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
        }}
      >
        <button className="zoom-btn" onClick={() => handleZoom(0.1)} title="放大">+</button>
        <span className="zoom-level">{Math.round(zoom * 100)}%</span>
        <button className="zoom-btn" onClick={() => handleZoom(-0.1)} title="缩小">-</button>
        <button className="zoom-btn reset" onClick={handleReset} title="重置">⟲</button>
      </div>

      <div className="operation-hint">
        <span>🖱️ 拖拽平移</span>
        <span>⌨️ Ctrl+滚轮缩放</span>
        <span>📱 滚轮页面滚动</span>
      </div>

      <div
        style={{ width: '100%', height: 'calc(100vh - 180px)', overflow: 'auto' }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <svg
          width="1600"
          height="1350"
          style={{
            transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
            transformOrigin: 'top left',
            cursor: isDragging ? 'grabbing' : 'grab',
            minWidth: '1600px',
            minHeight: '1350px'
          }}
        >
          <defs>
            <marker id="arrow" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#333" />
            </marker>
            <marker id="arrowGreen" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#52c41a" />
            </marker>
            <marker id="arrowRed" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="#e91e63" />
            </marker>
            <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
              <feDropShadow dx="1" dy="1" stdDeviation="1" floodOpacity="0.3" />
            </filter>
            <linearGradient id="alkaliGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ffb74d" />
              <stop offset="100%" stopColor="#ff9800" />
            </linearGradient>
            <linearGradient id="acidGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ce93d8" />
              <stop offset="100%" stopColor="#9c27b0" />
            </linearGradient>
            <linearGradient id="hotWaterGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#ef5350" />
              <stop offset="100%" stopColor="#c62828" />
            </linearGradient>
            <linearGradient id="pureWaterGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#64b5f6" />
              <stop offset="100%" stopColor="#1976d2" />
            </linearGradient>
            <style>{`
              @keyframes flow {
                0% { stroke-dashoffset: 20; }
                100% { stroke-dashoffset: 0; }
              }
              .flow-anim { animation: flow 1s linear infinite; }
            `}</style>
          </defs>

          <rect width="100%" height="100%" fill="#fafafa" />

          <text x="800" y="30" textAnchor="middle" fontSize="18" fontWeight="bold" fill="#1a1a1a">茶饮料生产线 CIP清洗系统 P&ID工艺流程图</text>
          <text x="800" y="50" textAnchor="middle" fontSize="10" fill="#666">设计标准: ISO 14617 / ISA S5.1 | 图号: CIP-PID-001 | 版本: V2.0</text>
          <line x1="50" y1="60" x2="1550" y2="60" stroke="#333" strokeWidth="2" />

          {/* ========== 1. 介质制备系统 ========== */}
          <g transform="translate(50, 80)">
            <rect x="0" y="0" width="1500" height="120" fill="none" stroke="#ddd" strokeWidth="1" strokeDasharray="5,5" rx="5" />
            <text x="10" y="15" fontSize="11" fontWeight="bold" fill="#333">1. 介质制备系统</text>

            {/* TK-101 碱液罐 */}
            <g transform="translate(30, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-101', name: '碱液储罐', tag: 'TK-101', data: { level: 85, temp: 85, conductivity: 32 } })} style={{ cursor: 'pointer' }}>
              <rect x="0" y="0" width="55" height="85" fill="url(#alkaliGrad)" stroke="#e65100" strokeWidth="2" rx="5" filter="url(#shadow)" />
              <ellipse cx="27" cy="0" rx="27" ry="6" fill="#ff9800" />
              <rect x="22" y="10" width="10" height="60" fill="rgba(255,255,255,0.3)" />
              <text x="27" y="105" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-101</text>
              <text x="27" y="117" textAnchor="middle" fontSize="7" fill="#666">碱液罐</text>
              <text x="27" y="35" textAnchor="middle" fontSize="10" fill="#fff" fontWeight="bold">85%</text>
              <text x="27" y="50" textAnchor="middle" fontSize="8" fill="#fff">85℃</text>
              <Tooltip title="TT01: 温度  LT01: 液位  CD01: 电导率">
                <circle cx="50" cy="8" r="6" fill="#ff9800" stroke="#fff" strokeWidth="1" />
                <text x="50" y="11" textAnchor="middle" fontSize="7" fill="#fff">T</text>
              </Tooltip>
            </g>

            {/* TK-102 酸液罐 */}
            <g transform="translate(140, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-102', name: '酸液储罐', tag: 'TK-102', data: { level: 72, temp: 60, conductivity: 28 } })} style={{ cursor: 'pointer' }}>
              <rect x="0" y="0" width="55" height="85" fill="url(#acidGrad)" stroke="#6a1b9a" strokeWidth="2" rx="5" filter="url(#shadow)" />
              <ellipse cx="27" cy="0" rx="27" ry="6" fill="#9c27b0" />
              <rect x="22" y="20" width="10" height="50" fill="rgba(255,255,255,0.3)" />
              <text x="27" y="105" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-102</text>
              <text x="27" y="117" textAnchor="middle" fontSize="7" fill="#666">酸液罐</text>
              <text x="27" y="35" textAnchor="middle" fontSize="10" fill="#fff" fontWeight="bold">72%</text>
              <text x="27" y="50" textAnchor="middle" fontSize="8" fill="#fff">60℃</text>
              <Tooltip title="TT02: 温度  LT02: 液位  CD02: 电导率">
                <circle cx="50" cy="8" r="6" fill="#9c27b0" stroke="#fff" strokeWidth="1" />
                <text x="50" y="11" textAnchor="middle" fontSize="7" fill="#fff">T</text>
              </Tooltip>
            </g>

            {/* TK-103 热水罐 */}
            <g transform="translate(250, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-103', name: '热水储罐', tag: 'TK-103', data: { level: 95, temp: 85 } })} style={{ cursor: 'pointer' }}>
              <rect x="0" y="0" width="55" height="85" fill="url(#hotWaterGrad)" stroke="#b71c1c" strokeWidth="2" rx="5" filter="url(#shadow)" />
              <ellipse cx="27" cy="0" rx="27" ry="6" fill="#c62828" />
              <rect x="22" y="5" width="10" height="65" fill="rgba(255,255,255,0.3)" />
              <text x="27" y="105" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-103</text>
              <text x="27" y="117" textAnchor="middle" fontSize="7" fill="#666">热水罐</text>
              <text x="27" y="35" textAnchor="middle" fontSize="10" fill="#fff" fontWeight="bold">95%</text>
              <text x="27" y="50" textAnchor="middle" fontSize="8" fill="#fff">85℃</text>
              <Tooltip title="TT03: 温度  LT03: 液位">
                <circle cx="50" cy="8" r="6" fill="#c62828" stroke="#fff" strokeWidth="1" />
                <text x="50" y="11" textAnchor="middle" fontSize="7" fill="#fff">T</text>
              </Tooltip>
            </g>

            {/* TK-104 纯水罐 */}
            <g transform="translate(360, 25)" onClick={() => handleDeviceClick({ type: 'tank', id: 'TK-104', name: '纯水储罐', tag: 'TK-104', data: { level: 88, temp: 25 } })} style={{ cursor: 'pointer' }}>
              <rect x="0" y="0" width="55" height="85" fill="url(#pureWaterGrad)" stroke="#0d47a1" strokeWidth="2" rx="5" filter="url(#shadow)" />
              <ellipse cx="27" cy="0" rx="27" ry="6" fill="#1976d2" />
              <rect x="22" y="12" width="10" height="58" fill="rgba(255,255,255,0.3)" />
              <text x="27" y="105" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">TK-104</text>
              <text x="27" y="117" textAnchor="middle" fontSize="7" fill="#666">纯水罐</text>
              <text x="27" y="35" textAnchor="middle" fontSize="10" fill="#fff" fontWeight="bold">88%</text>
              <text x="27" y="50" textAnchor="middle" fontSize="8" fill="#fff">25℃</text>
              <Tooltip title="TT04: 温度  LT04: 液位">
                <circle cx="50" cy="8" r="6" fill="#1976d2" stroke="#fff" strokeWidth="1" />
                <text x="50" y="11" textAnchor="middle" fontSize="7" fill="#fff">T</text>
              </Tooltip>
            </g>

            {/* 计量泵 P-CP06 */}
            <g transform="translate(500, 35)" onClick={() => handleDeviceClick({ type: 'meteringPump', id: 'P-CP06', name: '碱液计量泵', tag: 'P-CP06', data: { running: zones[0]?.current_media === 'CAUSTIC', frequency: 50 } })} style={{ cursor: 'pointer' }}>
              <ellipse cx="30" cy="35" rx="28" ry="18" fill={zones[0]?.current_media === 'CAUSTIC' ? '#ff9800' : '#fff'} stroke="#ff9800" strokeWidth="2" filter="url(#shadow)" />
              <ellipse cx="30" cy="35" rx="15" ry="10" fill="#fff" stroke="#ff9800" strokeWidth="1" />
              <text x="30" y="38" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#ff9800">MP</text>
              <text x="30" y="75" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">P-CP06</text>
              <text x="30" y="87" textAnchor="middle" fontSize="7" fill="#666">碱液计量</text>
              <text x="30" y="99" textAnchor="middle" fontSize="8" fill={zones[0]?.current_media === 'CAUSTIC' ? '#52c41a' : '#999'}>
                {zones[0]?.current_media === 'CAUSTIC' ? '● 运行' : '○ 待机'}
              </text>
            </g>

            {/* 计量泵 P-CP07 */}
            <g transform="translate(620, 35)" onClick={() => handleDeviceClick({ type: 'meteringPump', id: 'P-CP07', name: '酸液计量泵', tag: 'P-CP07', data: { running: zones[0]?.current_media === 'ACID', frequency: 50 } })} style={{ cursor: 'pointer' }}>
              <ellipse cx="30" cy="35" rx="28" ry="18" fill={zones[0]?.current_media === 'ACID' ? '#9c27b0' : '#fff'} stroke="#9c27b0" strokeWidth="2" filter="url(#shadow)" />
              <ellipse cx="30" cy="35" rx="15" ry="10" fill="#fff" stroke="#9c27b0" strokeWidth="1" />
              <text x="30" y="38" textAnchor="middle" fontSize="10" fontWeight="bold" fill="#9c27b0">MP</text>
              <text x="30" y="75" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">P-CP07</text>
              <text x="30" y="87" textAnchor="middle" fontSize="7" fill="#666">酸液计量</text>
              <text x="30" y="99" textAnchor="middle" fontSize="8" fill={zones[0]?.current_media === 'ACID' ? '#52c41a' : '#999'}>
                {zones[0]?.current_media === 'ACID' ? '● 运行' : '○ 待机'}
              </text>
            </g>

            {/* 传感器面板 */}
            <g transform="translate(750, 30)">
              <rect x="0" y="0" width="300" height="100" fill="#fff" stroke="#ddd" strokeWidth="1" rx="3" />
              <text x="10" y="15" fontSize="9" fontWeight="bold" fill="#333">传感器配置</text>
              <line x1="0" y1="20" x2="300" y2="20" stroke="#eee" />
              <text x="10" y="35" fontSize="7" fill="#666">TT01~04: 温度传感器</text>
              <text x="10" y="48" fontSize="7" fill="#666">LT01~04: 液位传感器</text>
              <text x="10" y="61" fontSize="7" fill="#666">CD01~02: 电导率传感器</text>
              <text x="10" y="74" fontSize="7" fill="#666">PT-01: 压力变送器</text>
              <text x="10" y="87" fontSize="7" fill="#666">FT-01: 主管流量计</text>
            </g>
          </g>

          {/* ========== 管道: 储罐→公用阀组 ========== */}
          <path d="M 82 205 L 82 240 L 120 240" fill="none" stroke="#ff9800" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          <path d="M 192 205 L 192 240 L 230 240" fill="none" stroke="#9c27b0" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          <path d="M 302 205 L 302 240 L 340 240" fill="none" stroke="#c62828" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          <path d="M 412 205 L 412 240 L 450 240" fill="none" stroke="#1976d2" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />

          {/* ========== 2. 公用介质阀组 ========== */}
          <g transform="translate(50, 240)">
            <rect x="0" y="0" width="1500" height="90" fill="none" stroke="#ddd" strokeWidth="1" strokeDasharray="5,5" rx="5" />
            <text x="10" y="15" fontSize="11" fontWeight="bold" fill="#333">2. 公用介质阀组</text>

            {/* 阀门 */}
            {[
              { id: 'M-V-01', name: '碱液', color: '#ff9800', x: 20, media: 'CAUSTIC' },
              { id: 'M-V-02', name: '酸液', color: '#9c27b0', x: 120, media: 'ACID' },
              { id: 'M-V-03', name: '热水', color: '#c62828', x: 220, media: 'HOT_WATER' },
              { id: 'M-V-04', name: '纯水', color: '#1976d2', x: 320, media: 'PURE_WATER' },
              { id: 'M-V-05', name: '循环', color: '#43a047', x: 420, media: null },
              { id: 'M-V-06', name: '排放', color: '#e91e63', x: 520, media: null }
            ].map((valve) => (
              <g key={valve.id} transform={`translate(${valve.x}, 25)`} onClick={() => handleDeviceClick({ type: 'valve', id: valve.id, name: `${valve.name}阀`, tag: valve.id, data: { open: valve.media ? zones[0]?.current_media === valve.media : false } })} style={{ cursor: 'pointer' }}>
                <circle cx="25" cy="20" r="18" fill={valve.media && zones[0]?.current_media === valve.media ? valve.color : '#fff'} stroke={valve.color} strokeWidth="2" filter="url(#shadow)" />
                <polygon points="25,6 35,20 25,34" fill={valve.media && zones[0]?.current_media === valve.media ? '#fff' : valve.color} />
                <text x="25" y="55" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">{valve.id}</text>
                <text x="25" y="67" textAnchor="middle" fontSize="7" fill="#666">{valve.name}</text>
              </g>
            ))}

            {/* DN80总管 */}
            <text x="650" y="30" fontSize="8" fill="#666">DN80总管</text>
            <line x1="620" y1="35" x2="750" y2="35" stroke="#666" strokeWidth="4" />
          </g>

          {/* ========== 管道: 公用阀→清洗泵 ========== */}
          <path d="M 95 330 L 95 370 L 150 370" fill="none" stroke="#ff9800" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          <path d="M 195 330 L 195 370 L 250 370" fill="none" stroke="#9c27b0" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          <path d="M 295 330 L 295 370 L 350 370" fill="none" stroke="#c62828" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          <path d="M 395 330 L 395 370 L 450 370" fill="none" stroke="#1976d2" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          <path d="M 495 330 L 495 370 L 550 370" fill="none" stroke="#e91e63" strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />

          {/* ========== 3. 清洗泵组 ========== */}
          <g transform="translate(50, 370)">
            <rect x="0" y="0" width="1500" height="110" fill="none" stroke="#ddd" strokeWidth="1" strokeDasharray="5,5" rx="5" />
            <text x="10" y="15" fontSize="11" fontWeight="bold" fill="#333">3. 清洗泵组</text>

            {[0, 1, 2, 3, 4].map((index) => (
              <g key={index} transform={`translate(${20 + index * 160}, 25)`} onClick={() => handleDeviceClick({ type: 'pump', id: `P-CP0${index + 1}`, name: `${index + 1}区清洗泵`, tag: `P-CP0${index + 1}`, data: { running: zones[index]?.pump_running || false, frequency: 50 } })} style={{ cursor: 'pointer' }}>
                <circle cx="35" cy="30" r="25" fill={zones[index]?.pump_running ? '#43a047' : '#fff'} stroke="#43a047" strokeWidth="2" filter="url(#shadow)" />
                <circle cx="35" cy="30" r="12" fill="#fff" stroke="#43a047" strokeWidth="1" />
                <text x="35" y="34" textAnchor="middle" fontSize="14" fontWeight="bold" fill={zones[index]?.pump_running ? '#fff' : '#43a047'}>P</text>
                <text x="35" y="70" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">P-CP0{index + 1}</text>
                <text x="35" y="82" textAnchor="middle" fontSize="8" fill={getZoneColor(index)} fontWeight="bold">Zone-{index + 1}</text>
                <text x="35" y="95" textAnchor="middle" fontSize="8" fill={zones[index]?.pump_running ? '#52c41a' : '#999'}>
                  {zones[index]?.pump_running ? '● 运行' : '○ 待机'}
                </text>
              </g>
            ))}

            {/* 主管道汇总 */}
            <line x1="150" y1="55" x2="850" y2="55" stroke="#666" strokeWidth="5" />
            <text x="500" y="48" textAnchor="middle" fontSize="8" fill="#666">DN125 清洗液主管</text>
          </g>

          {/* ========== 管道: 清洗泵→板式换热器 ========== */}
          <path d="M 95 480 L 95 510 L 700 510 L 700 540" fill="none" stroke="#43a047" strokeWidth="4" className="flow-anim" markerEnd="url(#arrowGreen)" />
          <path d="M 255 480 L 255 510" fill="none" stroke="#43a047" strokeWidth="4" />
          <path d="M 415 480 L 415 510" fill="none" stroke="#43a047" strokeWidth="4" />
          <path d="M 575 480 L 575 510" fill="none" stroke="#43a047" strokeWidth="4" />
          <path d="M 735 480 L 735 510" fill="none" stroke="#43a047" strokeWidth="4" />

          {/* ========== 4. 板式换热器 ========== */}
          <g transform="translate(580, 540)">
            <rect x="0" y="0" width="240" height="140" fill="none" stroke="#ddd" strokeWidth="1" strokeDasharray="5,5" rx="5" />
            <text x="10" y="15" fontSize="11" fontWeight="bold" fill="#333">4. 板式换热器</text>

            <g onClick={() => handleDeviceClick({ type: 'heatExchanger', id: 'E-101', name: '板式换热器', tag: 'E-101', data: { temp: 85 } })} style={{ cursor: 'pointer' }}>
              <rect x="60" y="30" width="100" height="80" fill="#fff" stroke="#333" strokeWidth="2" filter="url(#shadow)" />
              {[15, 33, 51, 68].map((y) => (
                <line key={y} x1="60" y1={y} x2="160" y2={y} stroke="#999" strokeWidth="1" />
              ))}
              <circle cx="55" cy="45" r="5" fill="#333" />
              <circle cx="165" cy="45" r="5" fill="#333" />
              <circle cx="55" cy="95" r="5" fill="#333" />
              <circle cx="165" cy="95" r="5" fill="#333" />
              <text x="110" y="65" textAnchor="middle" fontSize="12" fontWeight="bold" fill="#333">E-101</text>
              <text x="110" y="80" textAnchor="middle" fontSize="8" fill="#666">板式换热器</text>
              <text x="110" y="130" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#333">E-101</text>
              <text x="110" y="142" textAnchor="middle" fontSize="7" fill="#666">换热面积: 25m²</text>
            </g>

            {/* 温度传感器 */}
            <g transform="translate(170, 50)">
              <rect x="0" y="0" width="60" height="25" fill="#fff" stroke="#ff5722" strokeWidth="1" rx="3" />
              <text x="30" y="16" textAnchor="middle" fontSize="9" fill="#ff5722">TT-E1</text>
              <text x="30" y="28" textAnchor="middle" fontSize="7" fill="#666">85℃</text>
            </g>
          </g>

          {/* ========== 管道: 换热器→各区阀门 ========== */}
          <path d="M 700 680 L 700 710 L 150 710 L 150 740" fill="none" stroke="#43a047" strokeWidth="4" className="flow-anim" markerEnd="url(#arrowGreen)" />
          <path d="M 750 680 L 750 710 L 310 710 L 310 740" fill="none" stroke="#43a047" strokeWidth="4" className="flow-anim" markerEnd="url(#arrowGreen)" />
          <path d="M 750 680 L 750 710 L 470 710 L 470 740" fill="none" stroke="#43a047" strokeWidth="4" className="flow-anim" markerEnd="url(#arrowGreen)" />
          <path d="M 750 680 L 750 710 L 630 710 L 630 740" fill="none" stroke="#43a047" strokeWidth="4" className="flow-anim" markerEnd="url(#arrowGreen)" />
          <path d="M 750 680 L 750 710 L 790 710 L 790 740" fill="none" stroke="#43a047" strokeWidth="4" className="flow-anim" markerEnd="url(#arrowGreen)" />

          {/* ========== 5. 每区阀门组 ========== */}
          <g transform="translate(50, 740)">
            <rect x="0" y="0" width="1500" height="150" fill="none" stroke="#ddd" strokeWidth="1" strokeDasharray="5,5" rx="5" />
            <text x="10" y="15" fontSize="11" fontWeight="bold" fill="#333">5. 每区阀门组</text>

            {[0, 1, 2, 3, 4].map((zoneIndex) => (
              <g key={zoneIndex} transform={`translate(${20 + zoneIndex * 155}, 25)`}>
                <text x="55" y="0" textAnchor="middle" fontSize="10" fontWeight="bold" fill={getZoneColor(zoneIndex)}>Zone-{zoneIndex + 1}</text>
                
                {[
                  { id: `Z${zoneIndex+1}-V-01`, name: '进液', color: '#4caf50', type: 'inlet' },
                  { id: `Z${zoneIndex+1}-V-02`, name: '回流', color: '#ff9800', type: 'return' },
                  { id: `Z${zoneIndex+1}-V-03`, name: '排放', color: '#e91e63', type: 'drain' },
                  { id: `Z${zoneIndex+1}-V-04`, name: '循环', color: '#2196f3', type: 'circulation' }
                ].map((valve, valveIndex) => (
                  <g key={valve.id} transform={`translate(0, ${valveIndex * 28})`} onClick={() => handleDeviceClick({ type: 'valve', id: valve.id, name: `${zoneIndex+1}区${valve.name}`, tag: valve.id, data: { valveType: valve.type } })} style={{ cursor: 'pointer' }}>
                    <rect x="0" y="0" width="110" height="24" fill={valve.color} stroke="#fff" strokeWidth="1" rx="3" opacity="0.9" />
                    <text x="5" y="15" fontSize="7" fill="#fff" fontWeight="bold">{valve.id}</text>
                    <text x="60" y="15" fontSize="6" fill="rgba(255,255,255,0.9)">{valve.name}</text>
                  </g>
                ))}
              </g>
            ))}
          </g>

          {/* ========== 管道: 各区阀门→清洗对象 ========== */}
          {[0, 1, 2, 3, 4].map((index) => (
            <path key={index} d={`M ${110 + index * 155} 890 L ${110 + index * 155} 920}`} fill="none" stroke={getZoneColor(index)} strokeWidth="3" className="flow-anim" markerEnd="url(#arrow)" />
          ))}

          {/* ========== 6. 清洗对象 ========== */}
          <g transform="translate(50, 920)">
            <rect x="0" y="0" width="1500" height="200" fill="none" stroke="#ddd" strokeWidth="1" strokeDasharray="5,5" rx="5" />
            <text x="10" y="15" fontSize="11" fontWeight="bold" fill="#333">6. 清洗对象（被清洗设备）</text>

            {[0, 1, 2, 3, 4].map((index) => (
              <g key={index} transform={`translate(${20 + index * 155}, 25)`} onClick={() => handleDeviceClick({ type: 'zone', id: `Zone-${index + 1}`, name: getZoneName(index), tag: `CIP-Z${index + 1}`, data: { state: zones[index]?.state || 'IDLE', temp: zones[index]?.temp_pv || 0, conductivity: zones[index]?.conductivity || 0, flow: zones[index]?.flow_pv || 0 } })} style={{ cursor: 'pointer' }}>
                <rect x="0" y="0" width="145" height="165" fill={getZoneBgColor(index)} stroke={getZoneColor(index)} strokeWidth="2" rx="5" filter="url(#shadow)" />
                <text x="72" y="18" textAnchor="middle" fontSize="11" fontWeight="bold" fill="#333">Zone-{index + 1}</text>
                <text x="72" y="32" textAnchor="middle" fontSize="7" fill="#666">{getZoneName(index)}</text>
                <line x1="5" y1="40" x2="140" y2="40" stroke={getZoneColor(index)} strokeWidth="1" strokeDasharray="3,2" />
                <text x="72" y="55" textAnchor="middle" fontSize="9" fill={getZoneColor(index)} fontWeight="bold">{getZoneEquipment(index)}</text>
                
                <line x1="5" y1="62" x2="140" y2="62" stroke="#ddd" strokeWidth="1" />
                <text x="10" y="78" fontSize="8" fill="#333">温度: </text>
                <text x="135" y="78" textAnchor="end" fontSize="9" fontWeight="bold" fill="#ff5722">{zones[index]?.temp_pv?.toFixed(1) || '0.0'}℃</text>
                
                <text x="10" y="95" fontSize="8" fill="#333">电导: </text>
                <text x="135" y="95" textAnchor="end" fontSize="9" fontWeight="bold" fill="#9c27b0">{zones[index]?.conductivity?.toFixed(1) || '0.0'}</text>
                
                <text x="10" y="112" fontSize="8" fill="#333">流量: </text>
                <text x="135" y="112" textAnchor="end" fontSize="9" fontWeight="bold" fill="#1976d2">{zones[index]?.flow_pv?.toFixed(2) || '0.00'} m³/h</text>

                <line x1="5" y1="120" x2="140" y2="120" stroke="#ddd" strokeWidth="1" />
                <text x="10" y="135" fontSize="7" fill="#666">TT-{index+1}: </text>
                <text x="135" y="135" textAnchor="end" fontSize="7" fill="#ff5722">{zones[index]?.temp_pv?.toFixed(1) || '0.0'}℃</text>
                <text x="10" y="148" fontSize="7" fill="#666">FT-{index+1}: </text>
                <text x="135" y="148" textAnchor="end" fontSize="7" fill="#1976d2">{zones[index]?.flow_pv?.toFixed(2) || '0.00'}</text>

                <rect x="5" y="152" width="135" height="10" fill={zones[index]?.state === 'STEP_EXEC' ? '#4caf50' : zones[index]?.state === 'PAUSE' ? '#ff9800' : '#999'} rx="2" />
                <text x="72" y="160" textAnchor="middle" fontSize="6" fill="#fff">
                  {zones[index]?.state === 'STEP_EXEC' ? '清洗中' : zones[index]?.state === 'PAUSE' ? '已暂停' : '待机'}
                </text>
              </g>
            ))}
          </g>

          {/* ========== 管道: 清洗对象→排放 ========== */}
          {[0, 1, 2, 3, 4].map((index) => (
            <path key={index} d={`M ${110 + index * 155} 1120 L ${110 + index * 155} 1150 L 1350 1150}`} fill="none" stroke="#e91e63" strokeWidth="2" className="flow-anim" markerEnd="url(#arrowRed)" />
          ))}

          {/* ========== 7. 排放系统 ========== */}
          <g transform="translate(1250, 920)">
            <rect x="0" y="0" width="300" height="280" fill="none" stroke="#e91e63" strokeWidth="2" strokeDasharray="5,5" rx="5" />
            <text x="10" y="15" fontSize="11" fontWeight="bold" fill="#e91e63">7. 排放系统</text>

            {/* 排放总管 */}
            <rect x="100" y="40" width="80" height="180" fill="#fff" stroke="#e91e63" strokeWidth="2" rx="5" filter="url(#shadow)" />
            <line x1="140" y1="50" x2="140" y2="200" stroke="#e91e63" strokeWidth="6" className="flow-anim" />
            <text x="140" y="240" textAnchor="middle" fontSize="9" fontWeight="bold" fill="#e91e63">排放总管</text>
            <text x="140" y="252" textAnchor="middle" fontSize="7" fill="#666">DN150</text>

            {/* 排放阀 M-V-06 */}
            <g transform="translate(200, 100)" onClick={() => handleDeviceClick({ type: 'valve', id: 'M-V-06', name: '排放总阀', tag: 'M-V-06', data: {} })} style={{ cursor: 'pointer' }}>
              <circle cx="20" cy="20" r="18" fill="#fff" stroke="#e91e63" strokeWidth="2" filter="url(#shadow)" />
              <polygon points="20,6 30,20 20,34" fill="#e91e63" />
              <text x="20" y="50" textAnchor="middle" fontSize="8" fontWeight="bold" fill="#333">M-V-06</text>
              <text x="20" y="62" textAnchor="middle" fontSize="7" fill="#666">排放总阀</text>
            </g>

            {/* 液位计 */}
            <rect x="50" y="80" width="30" height="100" fill="#fff" stroke="#e91e63" strokeWidth="1" rx="2" />
            <rect x="55" y="100" width="20" height="60" fill="#e91e63" opacity="0.5" rx="1" />
            <text x="65" y="195" textAnchor="middle" fontSize="7" fill="#666">LT-D</text>
          </g>

          {/* ========== 图例 ========== */}
          <g transform="translate(50, 1210)">
            <rect x="0" y="0" width="1500" height="55" fill="#fff" stroke="#ddd" strokeWidth="1" rx="3" />
            <text x="10" y="15" fontSize="10" fontWeight="bold" fill="#333">图例</text>
            <line x1="0" y1="20" x2="1500" y2="20" stroke="#eee" />

            <rect x="50" y="28" width="20" height="15" fill="url(#alkaliGrad)" stroke="#e65100" strokeWidth="1" rx="2" />
            <text x="78" y="40" fontSize="8" fill="#333">储罐</text>

            <circle cx="130" cy="35" r="8" fill="#fff" stroke="#43a047" strokeWidth="2" />
            <text x="130" y="38" textAnchor="middle" fontSize="6" fill="#43a047" fontWeight="bold">P</text>
            <text x="148" y="40" fontSize="8" fill="#333">离心泵</text>

            <ellipse cx="220" cy="35" rx="12" ry="8" fill="#fff" stroke="#ff9800" strokeWidth="1.5" />
            <text x="220" y="38" textAnchor="middle" fontSize="5" fill="#ff9800" fontWeight="bold">MP</text>
            <text x="240" y="40" fontSize="8" fill="#333">计量泵</text>

            <circle cx="320" cy="35" r="8" fill="#fff" stroke="#333" strokeWidth="1.5" />
            <polygon points="320,28 327,35 320,42" fill="#333" />
            <text x="338" y="40" fontSize="8" fill="#333">调节阀</text>

            <rect x="430" y="28" width="24" height="15" fill="#fff" stroke="#333" strokeWidth="1" />
            <line x1="430" y1="33" x2="454" y2="33" stroke="#999" />
            <line x1="430" y1="38" x2="454" y2="38" stroke="#999" />
            <text x="462" y="40" fontSize="8" fill="#333">换热器</text>

            <line x1="550" y1="35" x2="590" y2="35" stroke="#666" strokeWidth="4" className="flow-anim" />
            <text x="600" y="40" fontSize="8" fill="#333">管道流向</text>

            <circle cx="680" cy="35" r="5" fill="#ff9800" />
            <text x="692" y="40" fontSize="7" fill="#333">碱液</text>
            <circle cx="740" cy="35" r="5" fill="#9c27b0" />
            <text x="752" y="40" fontSize="7" fill="#333">酸液</text>
            <circle cx="800" cy="35" r="5" fill="#c62828" />
            <text x="812" y="40" fontSize="7" fill="#333">热水</text>
            <circle cx="860" cy="35" r="5" fill="#1976d2" />
            <text x="872" y="40" fontSize="7" fill="#333">纯水</text>
            <circle cx="920" cy="35" r="5" fill="#43a047" />
            <text x="932" y="40" fontSize="7" fill="#333">清洗液</text>
            <circle cx="990" cy="35" r="5" fill="#e91e63" />
            <text x="1002" y="40" fontSize="7" fill="#333">排放</text>
          </g>

          {/* ========== 设计信息 ========== */}
          <line x1="50" y1="1270" x2="1550" y2="1270" stroke="#333" strokeWidth="1" />
          <text x="60" y="1285" fontSize="8" fill="#666">设计标准: ISO 14617 / ISA S5.1 | 图号: CIP-PID-001 | 版本: V2.0（完整P&ID流程图）</text>
          <text x="1550" y="1285" textAnchor="end" fontSize="8" fill="#666">第1张 共1张</text>
        </svg>
      </div>

      <Modal
        title={selectedDevice?.name || '设备详情'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={500}
      >
        {selectedDevice && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="设备编号" span={2}>{selectedDevice.id}</Descriptions.Item>
            <Descriptions.Item label="设备名称">{selectedDevice.name}</Descriptions.Item>
            <Descriptions.Item label="位号">{selectedDevice.tag || 'N/A'}</Descriptions.Item>
            {selectedDevice.data.level !== undefined && (
              <Descriptions.Item label="液位">{selectedDevice.data.level}%</Descriptions.Item>
            )}
            {selectedDevice.data.temp !== undefined && (
              <Descriptions.Item label="温度">{selectedDevice.data.temp}℃</Descriptions.Item>
            )}
            {selectedDevice.data.frequency !== undefined && (
              <Descriptions.Item label="频率">{selectedDevice.data.frequency} Hz</Descriptions.Item>
            )}
            {selectedDevice.data.conductivity !== undefined && (
              <Descriptions.Item label="电导率">{selectedDevice.data.conductivity} μS/cm</Descriptions.Item>
            )}
            {selectedDevice.data.flow !== undefined && (
              <Descriptions.Item label="流量">{selectedDevice.data.flow} m³/h</Descriptions.Item>
            )}
            {selectedDevice.data.state !== undefined && (
              <Descriptions.Item label="状态">
                <Tag color={selectedDevice.data.state === 'RUNNING' ? 'green' : selectedDevice.data.state === 'PAUSED' ? 'orange' : 'default'}>
                  {selectedDevice.data.state === 'RUNNING' ? '运行中' : selectedDevice.data.state === 'PAUSED' ? '已暂停' : '待机'}
                </Tag>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default FlowDiagram;
