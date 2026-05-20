import React, { Suspense, useState, useCallback, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Environment, Grid, Html } from '@react-three/drei';
import { useCIPStore } from '@/store';
import type { ZoneStatus } from '@/types';
import Tank3D from './Tank3D';
import Pump3D from './Pump3D';
import Pipeline3D from './Pipeline3D';
import Valve3D from './Valve3D';
import SensorIndicator from './SensorIndicator';
import { defaultCIPLLayout, MediaType } from './types';

interface DigitalTwinSceneProps {
  onDeviceSelect?: (deviceId: string, deviceType: string) => void;
  selectedDevice?: string;
  selectedZone?: number;
}

// 加载器组件
const Loader: React.FC = () => (
  <Html center>
    <div style={{ color: '#fff', fontSize: '14px' }}>加载3D场景中...</div>
  </Html>
);

// 地板组件
const Floor: React.FC = () => {
  return (
    <group>
      {/* 主地板 */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]} receiveShadow>
        <planeGeometry args={[30, 20]} />
        <meshStandardMaterial color="#263238" metalness={0.1} roughness={0.9} />
      </mesh>
      
      {/* 网格 */}
      <Grid
        position={[0, -0.05, 0]}
        args={[30, 20]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#37474F"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#455A64"
        fadeDistance={50}
        infiniteGrid
      />
    </group>
  );
};

// 场景环境
const SceneEnvironment: React.FC = () => {
  return (
    <>
      {/* 环境光 */}
      <ambientLight intensity={0.4} />
      
      {/* 主光源 */}
      <directionalLight
        position={[10, 20, 10]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={50}
        shadow-camera-left={-20}
        shadow-camera-right={20}
        shadow-camera-top={20}
        shadow-camera-bottom={-20}
      />
      
      {/* 补光 */}
      <directionalLight position={[-10, 10, -10]} intensity={0.3} />
      
      {/* 地面反射光 */}
      <hemisphereLight
        args={['#87CEEB', '#363636', 0.5]}
        position={[0, 20, 0]}
      />
    </>
  );
};

// 区域框架组件
const ZoneFrame: React.FC = () => {
  return (
    <group>
      {/* 左侧框架 - 原料区 */}
      <mesh position={[-8, 2.5, 2]}>
        <boxGeometry args={[0.2, 5, 14]} />
        <meshStandardMaterial
          color="#455A64"
          transparent
          opacity={0.3}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>
      
      {/* 右侧框架 - 清水区 */}
      <mesh position={[8, 2.5, 2]}>
        <boxGeometry args={[0.2, 5, 14]} />
        <meshStandardMaterial
          color="#455A64"
          transparent
          opacity={0.3}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>
      
      {/* 顶部框架 */}
      <mesh position={[0, 5.1, 2]}>
        <boxGeometry args={[16.4, 0.2, 14]} />
        <meshStandardMaterial
          color="#455A64"
          transparent
          opacity={0.2}
          metalness={0.5}
          roughness={0.5}
        />
      </mesh>

      {/* 区域标签 */}
      <Html position={[-8, 5.5, 6]} center>
        <div style={{
          color: '#FFB74D',
          fontSize: '18px',
          fontWeight: 'bold',
          textShadow: '0 0 10px rgba(255,183,77,0.5)',
        }}>
          原料区
        </div>
      </Html>
      
      <Html position={[8, 5.5, 6]} center>
        <div style={{
          color: '#4FC3F7',
          fontSize: '18px',
          fontWeight: 'bold',
          textShadow: '0 0 10px rgba(79,195,247,0.5)',
        }}>
          清水区
        </div>
      </Html>
      
      <Html position={[0, 5.5, 6]} center>
        <div style={{
          color: '#66BB6A',
          fontSize: '18px',
          fontWeight: 'bold',
          textShadow: '0 0 10px rgba(102,187,106,0.5)',
        }}>
          工艺区
        </div>
      </Html>
    </group>
  );
};

// 主3D场景组件
const DigitalTwinScene: React.FC<DigitalTwinSceneProps> = ({
  onDeviceSelect,
  selectedDevice,
  selectedZone,
}) => {
  // 从Zustand store获取数据
  const zones = useCIPStore((state) => state.zones);

  // 处理设备点击
  const handleDeviceClick = useCallback(
    (deviceId: string, deviceType: string) => {
      if (onDeviceSelect) {
        onDeviceSelect(deviceId, deviceType);
      }
    },
    [onDeviceSelect]
  );

  // 模拟设备数据（实际应从store或API获取）
  const tankData = useMemo(() => {
    return defaultCIPLLayout.tanks.map((tank, index) => ({
      ...tank,
      level: zones[index]?.flow_pv * 10 || 50, // 模拟液位
      temp: zones[index]?.temp_pv || 25,
      conductivity: zones[index]?.conductivity || 0,
      currentMedia: zones[index]?.current_media || MediaType.PURE_WATER,
      state: zones[index]?.state || 'IDLE',
    }));
  }, [zones]);

  const pumpData = useMemo(() => {
    return defaultCIPLLayout.pumps.map((pump, index) => ({
      ...pump,
      running: zones[index]?.pump_running || false,
      frequency: zones[index]?.flow_pv * 5 || 0,
      current: zones[index]?.pump_running ? 15 : 0,
      state: zones[index]?.state || 'IDLE',
    }));
  }, [zones]);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      <Canvas shadows>
        <Suspense fallback={<Loader />}>
          {/* 相机 */}
          <PerspectiveCamera makeDefault position={[0, 12, 18]} fov={50} />
          
          {/* 控制器 */}
          <OrbitControls
            enablePan={true}
            enableZoom={true}
            enableRotate={true}
            minDistance={5}
            maxDistance={50}
            maxPolarAngle={Math.PI / 2 - 0.1}
          />

          {/* 环境 */}
          <SceneEnvironment />

          {/* 地板 */}
          <Floor />

          {/* 区域框架 */}
          <ZoneFrame />

          {/* 储罐 */}
          {tankData.map((tank) => (
            <Tank3D
              key={tank.id}
              id={tank.id}
              tankId={tank.id}
              tankName={tank.name}
              position={tank.position}
              level={tank.level}
              temp={tank.temp}
              conductivity={tank.conductivity}
              currentMedia={tank.currentMedia}
              state={tank.state}
              selected={selectedDevice === tank.id}
              onClick={() => handleDeviceClick(tank.id, 'tank')}
            />
          ))}

          {/* 泵 */}
          {pumpData.map((pump) => (
            <Pump3D
              key={pump.id}
              id={pump.id}
              pumpId={pump.id}
              pumpName={pump.name}
              position={pump.position}
              running={pump.running}
              frequency={pump.frequency}
              current={pump.current}
              state={pump.state}
              selected={selectedDevice === pump.id}
              onClick={() => handleDeviceClick(pump.id, 'pump')}
            />
          ))}

          {/* 阀门 */}
          {defaultCIPLLayout.valves.map((valve, index) => (
            <Valve3D
              key={valve.id}
              id={valve.id}
              valveId={valve.id}
              valveName={valve.name}
              position={valve.position}
              open={index % 3 === 0} // 模拟数据
              openPercent={index % 3 === 0 ? 100 : index % 3 === 1 ? 50 : 0}
              mediaType={index < 4 ? MediaType.CAUSTIC : MediaType.PURE_WATER}
              selected={selectedDevice === valve.id}
              onClick={() => handleDeviceClick(valve.id, 'valve')}
            />
          ))}

          {/* 管道 */}
          {defaultCIPLLayout.pipelines.map((pipeline) => (
            <Pipeline3D
              key={pipeline.id}
              id={pipeline.id}
              startPoint={pipeline.start}
              endPoint={pipeline.end}
              radius={0.06}
              mediaType={MediaType.PURE_WATER}
              flowRate={pipeline.type === 'process' ? 50 : 30}
              active={pipeline.type === 'process'}
            />
          ))}

          {/* 传感器 */}
          {/* 温度传感器 */}
          <SensorIndicator
            id="TT-01"
            sensorId="TT-01"
            sensorName="原料区温度"
            sensorType="TT"
            position={[-8, 2, -2]}
            value={zones[0]?.temp_pv || 45}
            unit="°C"
            alarm={false}
          />
          <SensorIndicator
            id="TT-02"
            sensorId="TT-02"
            sensorName="清水区温度"
            sensorType="TT"
            position={[8, 2, -2]}
            value={zones[4]?.temp_pv || 85}
            unit="°C"
            alarm={false}
          />

          {/* 流量传感器 */}
          <SensorIndicator
            id="FT-01"
            sensorId="FT-01"
            sensorName="主管流量"
            sensorType="FT"
            position={[0, 0.3, 2]}
            value={zones[0]?.flow_pv || 12.5}
            unit="m³/h"
            alarm={false}
          />

          {/* 电导率传感器 */}
          <SensorIndicator
            id="CD-01"
            sensorId="CD-01"
            sensorName="清洗液电导"
            sensorType="CD"
            position={[3, 0.3, 2]}
            value={zones[0]?.conductivity || 350}
            unit="μS/cm"
            alarm={false}
            alarmLow={100}
            alarmHigh={500}
          />

          {/* 压力传感器 */}
          <SensorIndicator
            id="PT-01"
            sensorId="PT-01"
            sensorName="泵出口压力"
            sensorType="PT"
            position={[-3, 0.3, 2]}
            value={3.2}
            unit="bar"
            alarm={false}
            alarmHigh={4.0}
          />

        </Suspense>
      </Canvas>

      {/* 3D场景控制提示 */}
      <div
        style={{
          position: 'absolute',
          bottom: '20px',
          left: '20px',
          background: 'rgba(0,0,0,0.7)',
          padding: '12px 16px',
          borderRadius: '8px',
          color: '#fff',
          fontSize: '12px',
        }}
      >
        <div style={{ marginBottom: '8px', fontWeight: 'bold' }}>操作提示</div>
        <div>鼠标左键：旋转视角</div>
        <div>鼠标右键：平移</div>
        <div>滚轮：缩放</div>
        <div>点击设备：查看详情</div>
      </div>

      {/* 图例 */}
      <div
        style={{
          position: 'absolute',
          top: '20px',
          right: '20px',
          background: 'rgba(0,0,0,0.7)',
          padding: '12px 16px',
          borderRadius: '8px',
          color: '#fff',
          fontSize: '11px',
        }}
      >
        <div style={{ marginBottom: '8px', fontWeight: 'bold' }}>状态图例</div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <span style={{ color: '#52c41a', marginRight: '8px' }}>●</span>
          运行中
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <span style={{ color: '#1890ff', marginRight: '8px' }}>●</span>
          就绪
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <span style={{ color: '#faad14', marginRight: '8px' }}>●</span>
          暂停
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
          <span style={{ color: '#8c8c8c', marginRight: '8px' }}>●</span>
          待机
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: '#ff4d4f', marginRight: '8px' }}>●</span>
          故障/报警
        </div>
      </div>
    </div>
  );
};

export default DigitalTwinScene;
