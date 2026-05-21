/**
 * CIP数字孪生 - 中等复杂度3D场景
 * 平衡性能和视觉效果
 */

import React, { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';
import { useCIPStore } from '@/store';

// ============ 专业材质配置 ============
const createMetalMaterial = (color: string) => ({
  color,
  metalness: 0.85,
  roughness: 0.35,
});

const createGlassMaterial = () => ({
  color: '#88ccff',
  transparent: true,
  opacity: 0.5,
});

// ============ 储罐组件 ============
const Tank: React.FC<{
  position: [number, number, number];
  label: string;
  level: number;
  temp: number;
  color: string;
  onClick?: () => void;
}> = ({ position, label, level, temp, color, onClick }) => {
  const liquidHeight = (3.2 * level) / 100;
  const baseY = position[1];
  const tempColor = temp > 70 ? '#ff4444' : temp > 50 ? '#ff8800' : '#4488ff';

  return (
    <group position={position} onClick={onClick}>
      {/* 底座 */}
      <mesh position={[0, baseY - 2.2, 0]}>
        <cylinderGeometry args={[1.4, 1.6, 0.3, 24]} />
        <meshStandardMaterial {...createMetalMaterial('#555555')} />
      </mesh>

      {/* 支撑腿 */}
      {[0, 1, 2, 3].map((i) => {
        const angle = (i / 4) * Math.PI * 2 + Math.PI / 4;
        return (
          <mesh key={i} position={[Math.cos(angle) * 1.2, baseY - 1.5, Math.sin(angle) * 1.2]}>
            <boxGeometry args={[0.15, 1.2, 0.15]} />
            <meshStandardMaterial {...createMetalMaterial('#666666')} />
          </mesh>
        );
      })}

      {/* 罐体 */}
      <mesh position={[0, baseY, 0]}>
        <cylinderGeometry args={[1.2, 1.2, 4, 24]} />
        <meshStandardMaterial {...createMetalMaterial('#e0e0e0')} />
      </mesh>

      {/* 液位 */}
      <mesh position={[0, baseY - 2 + liquidHeight / 2 + 0.2, 0]}>
        <cylinderGeometry args={[1.05, 1.05, liquidHeight, 24]} />
        <meshStandardMaterial color={tempColor} transparent opacity={0.75} />
      </mesh>

      {/* 顶部 */}
      <mesh position={[0, baseY + 2.1, 0]}>
        <sphereGeometry args={[1.2, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial {...createMetalMaterial('#d0d0d0')} />
      </mesh>

      {/* 人孔 */}
      <mesh position={[0, baseY + 2.4, 0.6]}>
        <cylinderGeometry args={[0.25, 0.25, 0.15, 16]} />
        <meshStandardMaterial {...createMetalMaterial('#888888')} />
      </mesh>

      {/* 法兰圈 */}
      <mesh position={[0, baseY + 2.15, 0]}>
        <torusGeometry args={[1.25, 0.06, 8, 32]} />
        <meshStandardMaterial {...createMetalMaterial('#aaaaaa')} />
      </mesh>

      {/* 液位计 */}
      <group position={[1.35, baseY - 0.5, 0]}>
        <mesh>
          <cylinderGeometry args={[0.08, 0.08, 3.2, 8]} />
          <meshStandardMaterial {...createMetalMaterial('#888888')} />
        </mesh>
        <mesh>
          <cylinderGeometry args={[0.05, 0.05, 3.0, 8]} />
          <meshStandardMaterial {...createGlassMaterial()} />
        </mesh>
      </group>

      {/* 栏杆 */}
      {[0, 1, 2, 3].map((i) => {
        const angle = (i / 4) * Math.PI * 2;
        return (
          <mesh key={`rail-${i}`} position={[Math.cos(angle) * 1.8, baseY + 3.2, Math.sin(angle) * 1.8]}>
            <cylinderGeometry args={[0.03, 0.03, 0.6, 8]} />
            <meshStandardMaterial color="#ff9900" metalness={0.8} roughness={0.4} />
          </mesh>
        );
      })}

      {/* 梯子 */}
      <group position={[1.7, baseY - 0.5, 0]}>
        <mesh>
          <boxGeometry args={[0.06, 3.5, 0.06]} />
          <meshStandardMaterial {...createMetalMaterial('#666666')} />
        </mesh>
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <mesh key={i} position={[0.1, -1.5 + i * 0.6, 0]}>
            <boxGeometry args={[0.2, 0.04, 0.04]} />
            <meshStandardMaterial {...createMetalMaterial('#666666')} />
          </mesh>
        ))}
      </group>

      {/* 铭牌 */}
      <Text position={[0, baseY + 3.8, 0]} fontSize={0.4} color="#333" fontWeight="bold" anchorX="center">{label}</Text>
    </group>
  );
};

// ============ 泵组件 ============
const Pump: React.FC<{
  position: [number, number, number];
  label: string;
  running: boolean;
  color: string;
  onClick?: () => void;
}> = ({ position, label, running, color, onClick }) => {
  const impellerRef = useRef<THREE.Group>(null);
  const frameCount = useRef(0);

  useFrame(() => {
    frameCount.current++;
    if (frameCount.current % 4 !== 0) return;

    if (impellerRef.current && running) {
      impellerRef.current.rotation.z += 0.15;
    }
  });

  const statusColor = running ? '#52c41a' : '#999999';

  return (
    <group position={position} onClick={onClick}>
      {/* 基座 */}
      <mesh position={[0, -0.5, 0]}>
        <boxGeometry args={[2, 0.3, 1.6]} />
        <meshStandardMaterial color="#808080" metalness={0.1} roughness={0.9} />
      </mesh>

      {/* 泵体 */}
      <mesh position={[0, 0, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[0.6, 0.6, 1.4, 20]} />
        <meshStandardMaterial {...createMetalMaterial('#e0e0e0')} />
      </mesh>

      {/* 电机 */}
      <mesh position={[0, 0.9, 0]}>
        <cylinderGeometry args={[0.45, 0.45, 1, 20]} />
        <meshStandardMaterial {...createMetalMaterial('#444444')} />
      </mesh>

      {/* 散热片 */}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
        <mesh key={`fin-${i}`} position={[0, 0.9, 0]} rotation={[0, (i / 8) * Math.PI * 2, 0]}>
          <boxGeometry args={[0.5, 0.9, 0.02]} />
          <meshStandardMaterial {...createMetalMaterial('#333333')} />
        </mesh>
      ))}

      {/* 叶轮 */}
      <group ref={impellerRef} position={[0, 0, 0.75]}>
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <mesh key={i} rotation={[0, 0, (i / 6) * Math.PI * 2]}>
            <boxGeometry args={[0.03, 0.35, 0.1]} />
            <meshStandardMaterial color={statusColor} metalness={0.8} roughness={0.3} />
          </mesh>
        ))}
      </group>

      {/* 法兰 */}
      {[-0.8, 0.8].map((x, i) => (
        <mesh key={`flange-${i}`} position={[x, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.3, 0.3, 0.12, 16]} />
          <meshStandardMaterial {...createMetalMaterial('#888888')} />
        </mesh>
      ))}

      {/* 状态指示 */}
      <mesh position={[0.6, 1.5, 0]}>
        <sphereGeometry args={[0.12, 12, 12]} />
        <meshBasicMaterial color={statusColor} />
      </mesh>

      <Text position={[0, 2.2, 0]} fontSize={0.4} color="#333" anchorX="center">{label}</Text>
    </group>
  );
};

// ============ 阀门组件 ============
const Valve: React.FC<{
  position: [number, number, number];
  label: string;
  open: boolean;
  color: string;
  onClick?: () => void;
}> = ({ position, label, open, color, onClick }) => {
  const valveColor = open ? color : '#aaaaaa';

  return (
    <group position={position} onClick={onClick}>
      {/* 阀体 */}
      <mesh>
        <sphereGeometry args={[0.35, 16, 16]} />
        <meshStandardMaterial {...createMetalMaterial(valveColor)} />
      </mesh>

      {/* 阀盖 */}
      <mesh position={[0, 0.3, 0]}>
        <cylinderGeometry args={[0.2, 0.25, 0.15, 16]} />
        <meshStandardMaterial {...createMetalMaterial(valveColor)} />
      </mesh>

      {/* 手轮 */}
      <mesh position={[0, open ? 0.5 : 0.4, 0]} rotation={[0, 0, open ? Math.PI / 4 : 0]}>
        <torusGeometry args={[0.22, 0.035, 8, 20]} />
        <meshStandardMaterial {...createMetalMaterial('#333333')} />
      </mesh>

      {/* 阀杆 */}
      <mesh position={[0, 0.55, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 0.4, 8]} />
        <meshStandardMaterial {...createMetalMaterial('#888888')} />
      </mesh>

      {/* 连接法兰 */}
      {[-0.4, 0.4].map((z, i) => (
        <group key={i} position={[0, 0, z]}>
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.25, 0.25, 0.1, 16]} />
            <meshStandardMaterial {...createMetalMaterial('#888888')} />
          </mesh>
        </group>
      ))}
    </group>
  );
};

// ============ 管道组件 ============
const Pipeline: React.FC<{
  points: [number, number, number][];
  color: string;
  radius?: number;
  animated?: boolean;
}> = ({ points, color, radius = 0.12, animated = true }) => {
  const curve = useMemo(() => new THREE.CatmullRomCurve3(
    points.map(p => new THREE.Vector3(...p))
  ), [points]);

  const tubeGeometry = useMemo(() => {
    return new THREE.TubeGeometry(curve, 32, radius, 10, false);
  }, [curve, radius]);

  return (
    <group>
      <mesh>
        <primitive object={tubeGeometry} attach="geometry" />
        <meshStandardMaterial {...createMetalMaterial(color)} />
      </mesh>

      {/* 高光环 */}
      <mesh>
        <primitive object={tubeGeometry} attach="geometry" />
        <meshStandardMaterial color="#ffffff" transparent opacity={0.15} metalness={0.5} roughness={0.2} />
      </mesh>
    </group>
  );
};

// ============ 清洗区域 ============
const Zone: React.FC<{
  position: [number, number, number];
  name: string;
  index: number;
  temp: number;
  flow: number;
}> = ({ position, name, index, temp, flow }) => {
  const colors = ['#4caf50', '#ff9800', '#2196f3', '#e91e63', '#9c27b0'];

  return (
    <group position={position}>
      {/* 地面 */}
      <mesh position={[0, -1.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[5.5, 4.5]} />
        <meshStandardMaterial color="#e8e8e8" />
      </mesh>

      {/* 边框 */}
      <mesh position={[0, 2, 2.3]}>
        <boxGeometry args={[5.8, 0.15, 0.15]} />
        <meshStandardMaterial {...createMetalMaterial('#666666')} />
      </mesh>
      <mesh position={[0, 2, -2.3]}>
        <boxGeometry args={[5.8, 0.15, 0.15]} />
        <meshStandardMaterial {...createMetalMaterial('#666666')} />
      </mesh>
      <mesh position={[2.85, 2, 0]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[4.9, 0.15, 0.15]} />
        <meshStandardMaterial {...createMetalMaterial('#666666')} />
      </mesh>
      <mesh position={[-2.85, 2, 0]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[4.9, 0.15, 0.15]} />
        <meshStandardMaterial {...createMetalMaterial('#666666')} />
      </mesh>

      {/* 立柱 */}
      {[[-2.8, -2.2], [-2.8, 2.2], [2.8, -2.2], [2.8, 2.2]].map(([x, z], i) => (
        <mesh key={i} position={[x, 1, z]}>
          <boxGeometry args={[0.12, 4, 0.12]} />
          <meshStandardMaterial {...createMetalMaterial('#666666')} />
        </mesh>
      ))}

      {/* 护栏 */}
      <mesh position={[0, 1.5, 2.35]}>
        <boxGeometry args={[5.5, 0.04, 0.04]} />
        <meshStandardMaterial color="#ff6600" metalness={0.8} roughness={0.4} />
      </mesh>
      <mesh position={[0, 1.2, 2.35]}>
        <boxGeometry args={[5.5, 0.04, 0.04]} />
        <meshStandardMaterial color="#ff6600" metalness={0.8} roughness={0.4} />
      </mesh>

      {/* 区域标注 */}
      <Text position={[0, 3.5, 0]} fontSize={0.5} color={colors[index]} fontWeight="bold" anchorX="center">
        Zone-{index + 1} - {name}
      </Text>

      {/* 数据指示 */}
      <Text position={[0, 0.5, 2.5]} fontSize={0.3} color="#666" anchorX="center">
        {temp.toFixed(1)}°C | {flow.toFixed(1)} m³/h
      </Text>
    </group>
  );
};

// ============ 排放罐 ============
const DrainTank: React.FC<{
  position: [number, number, number];
  onClick?: () => void;
}> = ({ position, onClick }) => {
  return (
    <group position={position} onClick={onClick}>
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[1.2, 1, 4, 24]} />
        <meshStandardMaterial {...createMetalMaterial('#e0e0e0')} />
      </mesh>
      <mesh position={[0, -2.2, 0]}>
        <coneGeometry args={[1, 1.2, 24]} />
        <meshStandardMaterial {...createMetalMaterial('#cccccc')} />
      </mesh>
      <mesh position={[0, 2.15, 0]}>
        <cylinderGeometry args={[1.3, 1.2, 0.2, 24]} />
        <meshStandardMaterial {...createMetalMaterial('#aaaaaa')} />
      </mesh>
      <Text position={[0, 3.5, 0]} fontSize={0.45} color="#e91e63" fontWeight="bold" anchorX="center">排放罐</Text>
    </group>
  );
};

// ============ 管道支架 ============
const PipeSupport: React.FC<{ position: [number, number, number]; height?: number }> = ({ position, height = 2 }) => {
  return (
    <group position={position}>
      <mesh position={[0, height / 2, 0]}>
        <boxGeometry args={[0.15, height, 0.15]} />
        <meshStandardMaterial {...createMetalMaterial('#555555')} />
      </mesh>
      <mesh position={[0, height, 0]}>
        <boxGeometry args={[0.6, 0.1, 0.6]} />
        <meshStandardMaterial {...createMetalMaterial('#666666')} />
      </mesh>
    </group>
  );
};

// ============ 地板 ============
const Floor: React.FC = () => {
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color="#e0e0e0" />
      </mesh>
      <gridHelper args={[100, 50, '#ccc', '#e8e8e8']} position={[0, 0.001, 0]} />
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.002, 0]}>
        <ringGeometry args={[8, 8.15, 64]} />
        <meshStandardMaterial color="#ffd700" transparent opacity={0.3} />
      </mesh>
    </group>
  );
};

// ============ 主场景 ============
const DigitalTwinCanvas: React.FC<{
  onDeviceSelect?: (deviceId: string, deviceType: string) => void;
  selectedDevice?: string;
}> = ({ onDeviceSelect, selectedDevice }) => {
  const { zones } = useCIPStore();
  const [internalSelected, setInternalSelected] = useState<string | null>(null);
  const currentSelected = selectedDevice || internalSelected;

  const handleClick = (id: string) => {
    setInternalSelected(prev => prev === id ? null : id);
    onDeviceSelect?.(id, 'device');
  };

  const zoneColors = ['#4caf50', '#ff9800', '#2196f3', '#e91e63', '#9c27b0'];
  const zoneNames = ['水处理', '茶叶萃取', '调配系统', 'UHT杀菌', '灌装设备'];

  return (
    <>
      {/* 光照 */}
      <ambientLight intensity={0.5} />
      <directionalLight position={[20, 30, 20]} intensity={1.2} />
      <directionalLight position={[-10, 20, -10]} intensity={0.4} />
      <hemisphereLight args={['#ffffff', '#d0d7de', 0.3]} />
      <pointLight position={[15, 15, 15]} intensity={0.6} color="#ffffff" />

      <Floor />

      {/* ========== 介质制备区 ========== */}
      <group position={[-14, 0, -10]}>
        <Text position={[3, 5.5, 0]} fontSize={0.55} color="#333" fontWeight="bold" anchorX="center">介质制备区</Text>

        <Tank position={[0, 2, 0]} label="TK-101 碱液罐" level={85} temp={85} color="#ff9800" onClick={() => handleClick('TK-101')} />
        <Tank position={[4, 2, 0]} label="TK-102 酸液罐" level={72} temp={60} color="#9c27b0" onClick={() => handleClick('TK-102')} />
        <Tank position={[0, 2, 4]} label="TK-103 热水罐" level={95} temp={85} color="#ff5722" onClick={() => handleClick('TK-103')} />
        <Tank position={[4, 2, 4]} label="TK-104 纯水罐" level={88} temp={25} color="#2196f3" onClick={() => handleClick('TK-104')} />
      </group>

      {/* 管道连接 */}
      <Pipeline points={[[-14, 0.5, 0], [-10, 0.5, 0], [-10, 2, -3]]} color="#4caf50" />
      <Pipeline points={[[-10, 0.5, 0], [-10, 0.5, -3]]} color="#4caf50" />
      <Pipeline points={[[-10, 0.5, 4], [-10, 0.5, -1], [-10, 2, -3]]} color="#4caf50" />
      <Pipeline points={[[-10, 0.5, 4], [-10, 0.5, -1]]} color="#4caf50" />
      <PipeSupport position={[-12, 0, 0]} height={2} />
      <PipeSupport position={[-10, 0, -1]} height={3} />

      {/* ========== 公用阀组 ========== */}
      <group position={[-10, 0, -3]}>
        <Text position={[2, 3.5, 0]} fontSize={0.4} color="#333" fontWeight="bold" anchorX="center">公用介质阀组</Text>
        <Valve position={[0, 1.5, 0]} label="M-V-01" open={true} color="#ff9800" onClick={() => handleClick('V1')} />
        <Valve position={[1.5, 1.5, 0]} label="M-V-02" open={true} color="#9c27b0" onClick={() => handleClick('V2')} />
        <Valve position={[0, 1.5, 2]} label="M-V-03" open={true} color="#ff5722" onClick={() => handleClick('V3')} />
        <Valve position={[1.5, 1.5, 2]} label="M-V-04" open={true} color="#2196f3" onClick={() => handleClick('V4')} />
      </group>

      {/* 管道到计量泵 */}
      <Pipeline points={[[-7.5, 1.5, -3], [-5, 1.5, -3], [-5, 1.5, -1]]} color="#4caf50" />
      <Pipeline points={[[-5, 1.5, -1], [-5, 1.5, 1]]} color="#4caf50" />
      <PipeSupport position={[-6, 0, -3]} height={2.5} />

      {/* ========== 计量泵 ========== */}
      <group position={[-5, 0, 1]}>
        <Text position={[1.5, 4, 0]} fontSize={0.45} color="#333" fontWeight="bold" anchorX="center">计量泵组</Text>
        <Pump position={[0, 1, 0]} label="P-CP06" running={true} color="#ff9800" onClick={() => handleClick('P1')} />
        <Pump position={[3, 1, 0]} label="P-CP07" running={false} color="#9c27b0" onClick={() => handleClick('P2')} />
      </group>

      {/* 管道到清洗泵 */}
      <Pipeline points={[[-5, 0.5, 1], [-5, 0.5, 5]]} color="#4caf50" />
      <Pipeline points={[[-2, 0.5, 1], [-2, 0.5, 5]]} color="#4caf50" />
      <Pipeline points={[[-5, 0.5, 5], [-2, 0.5, 5]]} color="#4caf50" />
      <Pipeline points={[[-3.5, 0.5, 5], [-3.5, 0.5, 7]]} color="#4caf50" />
      <PipeSupport position={[-5, 0, 3]} height={1.5} />
      <PipeSupport position={[-3.5, 0, 5]} height={2} />

      {/* ========== 清洗泵组 ========== */}
      <group position={[-3.5, 0, 7]}>
        <Text position={[6, 4.5, 0]} fontSize={0.5} color="#333" fontWeight="bold" anchorX="center">清洗泵组</Text>
        {[0, 1, 2, 3, 4].map((index) => (
          <Pump
            key={index}
            position={[index * 3.5, 1, 0]}
            label={`P-CP0${index + 1}`}
            running={zones[index]?.pump_running || false}
            color={zoneColors[index]}
            onClick={() => handleClick(`CP${index + 1}`)}
          />
        ))}
      </group>

      {/* 管道到清洗区域 */}
      {[0, 1, 2, 3, 4].map((index) => (
        <Pipeline
          key={`pump-zone-${index}`}
          points={[[-3.5 + index * 3.5, 0.5, 7], [-3.5 + index * 3.5, 0.5, 10]]}
          color={zoneColors[index]}
        />
      ))}

      {/* ========== 清洗区域 ========== */}
      <group position={[0, 0, 10]}>
        <Text position={[7, 4.5, 0]} fontSize={0.55} color="#333" fontWeight="bold" anchorX="center">清洗区域</Text>
        {[0, 1, 2, 3, 4].map((index) => (
          <Zone
            key={index}
            position={[index * 5.5, 1.75, 0]}
            name={zoneNames[index]}
            index={index}
            temp={zones[index]?.temp_pv || 0}
            flow={zones[index]?.flow_pv || 0}
          />
        ))}
      </group>

      {/* 管道到排放 */}
      {[0, 1, 2, 3, 4].map((index) => (
        <Pipeline
          key={`zone-drain-${index}`}
          points={[[index * 5.5, 0.5, 10], [index * 5.5, 0.5, 14], [20, 0.5, 14]]}
          color="#e91e63"
          radius={0.1}
          animated={false}
        />
      ))}

      {/* ========== 排放系统 ========== */}
      <group position={[20, 0, 14]}>
        <Text position={[0, 5, 0]} fontSize={0.45} color="#e91e63" fontWeight="bold" anchorX="center">排放系统</Text>
        <DrainTank position={[0, 2, 0]} onClick={() => handleClick('DRAIN')} />
        <Valve position={[3, 2, 0]} label="M-V-06" open={false} color="#e91e63" onClick={() => handleClick('V6')} />
      </group>

      {/* 方向标注 */}
      <Text position={[0, 0.5, -15]} fontSize={0.5} color="#666" anchorX="center">← 介质入口方向</Text>
      <Text position={[28, 0.5, 14]} fontSize={0.5} color="#e91e63" anchorX="center">排放出口 →</Text>
    </>
  );
};

// ============ 主组件 ============
const DigitalTwinScene: React.FC<{
  onDeviceSelect?: (deviceId: string, deviceType: string) => void;
  selectedDevice?: string;
}> = ({ onDeviceSelect, selectedDevice }) => {
  return (
    <Canvas
      dpr={1}
      gl={{ antialias: true, powerPreference: 'low-power' }}
      camera={{ position: [10, 12, 25], fov: 45 }}
      style={{ background: 'linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%)' }}
    >
      <DigitalTwinCanvas onDeviceSelect={onDeviceSelect} selectedDevice={selectedDevice} />

      <OrbitControls
        makeDefault
        minPolarAngle={0.2}
        maxPolarAngle={Math.PI / 2 - 0.1}
        minDistance={10}
        maxDistance={60}
        enablePan
        panSpeed={0.8}
        target={[5, 2, 5]}
      />
    </Canvas>
  );
};

export default DigitalTwinScene;
