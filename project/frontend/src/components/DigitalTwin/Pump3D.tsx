import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { Pump3DProps, stateColors } from './types';

// 泵3D模型组件
const Pump3D: React.FC<Pump3DProps> = ({
  id,
  pumpId,
  pumpName,
  position,
  running,
  frequency,
  current,
  state,
  selected = false,
  onClick,
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const rotorRef = useRef<THREE.Mesh>(null);
  const indicatorRef = useRef<THREE.Mesh>(null);

  // 状态颜色
  const stateColor = useMemo(() => stateColors[state], [state]);

  // 指示灯颜色: 绿=运行, 红=故障, 黄=待机
  const indicatorColor = useMemo(() => {
    if (state === 'FAULT') return '#ff4d4f';
    if (state === 'STEP_EXEC' || running) return '#52c41a';
    if (state === 'READY') return '#1890ff';
    return '#faad14';
  }, [state, running]);

  // 动画效果
  useFrame((_, delta) => {
    if (groupRef.current) {
      // 轻微振动效果
      if (running) {
        groupRef.current.position.y = position[1] + Math.sin(Date.now() * 0.02) * 0.02;
      }
    }

    if (rotorRef.current && running) {
      // 转子旋转动画
      rotorRef.current.rotation.y += delta * (frequency / 60) * Math.PI * 2;
    }

    if (indicatorRef.current) {
      // 指示灯闪烁
      if (state === 'FAULT') {
        indicatorRef.current.visible = Math.sin(Date.now() * 0.01) > 0;
      } else {
        indicatorRef.current.visible = true;
      }
    }
  });

  return (
    <group ref={groupRef} position={position} onClick={onClick}>
      {/* 泵底座 */}
      <mesh position={[0, 0.05, 0]} receiveShadow>
        <boxGeometry args={[1.2, 0.1, 0.8]} />
        <meshStandardMaterial color="#455A64" metalness={0.5} roughness={0.5} />
      </mesh>

      {/* 泵主体 */}
      <mesh position={[0, 0.4, 0]} castShadow>
        <cylinderGeometry args={[0.35, 0.35, 0.6, 32]} />
        <meshStandardMaterial
          color="#607D8B"
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* 泵盖 */}
      <mesh position={[0, 0.75, 0]}>
        <cylinderGeometry args={[0.4, 0.35, 0.1, 32]} />
        <meshStandardMaterial
          color="#546E7A"
          metalness={0.6}
          roughness={0.4}
        />
      </mesh>

      {/* 转子（运行时旋转） */}
      <mesh ref={rotorRef} position={[0, 0.6, 0]}>
        <boxGeometry args={[0.02, 0.02, 0.5]} />
        <meshStandardMaterial
          color="#90A4AE"
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
      <mesh ref={rotorRef} position={[0, 0.6, 0]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[0.02, 0.02, 0.5]} />
        <meshStandardMaterial
          color="#90A4AE"
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* 入口管道 */}
      <mesh position={[-0.5, 0.4, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.1, 0.1, 0.4, 16]} />
        <meshStandardMaterial
          color="#78909C"
          metalness={0.5}
          roughness={0.4}
        />
      </mesh>

      {/* 出口管道 */}
      <mesh position={[0.5, 0.4, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[0.1, 0.1, 0.4, 16]} />
        <meshStandardMaterial
          color="#78909C"
          metalness={0.5}
          roughness={0.4}
        />
      </mesh>

      {/* 状态指示灯 */}
      <mesh ref={indicatorRef} position={[0, 0.9, 0.36]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial
          color={indicatorColor}
          emissive={indicatorColor}
          emissiveIntensity={0.8}
        />
      </mesh>

      {/* 铭牌 */}
      <mesh position={[0, 0.15, 0.41]}>
        <planeGeometry args={[0.6, 0.3]} />
        <meshStandardMaterial color="#ECEFF1" metalness={0.2} roughness={0.8} />
      </mesh>

      {/* 运行指示光效 */}
      {running && (
        <>
          <pointLight position={[0, 0.4, 0.5]} color={indicatorColor} intensity={0.3} distance={2} />
          {/* 流动粒子效果 */}
          {Array.from({ length: 3 }).map((_, i) => (
            <mesh
              key={i}
              position={[
                -0.3 + (i * 0.3),
                0.4 + Math.sin(Date.now() * 0.005 + i) * 0.1,
                0,
              ]}
            >
              <sphereGeometry args={[0.03, 8, 8]} />
              <meshBasicMaterial color="#4FC3F7" transparent opacity={0.6} />
            </mesh>
          ))}
        </>
      )}

      {/* 泵标签 */}
      <Html position={[0, 1.2, 0]} center distanceFactor={10}>
        <div
          style={{
            background: 'rgba(0,0,0,0.8)',
            padding: '8px 12px',
            borderRadius: '4px',
            color: '#fff',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            border: selected ? '2px solid #1890ff' : '1px solid #555',
            pointerEvents: 'none',
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{pumpName}</div>
          <div style={{ color: '#aaa' }}>ID: {pumpId}</div>
          <div>状态: {running ? '运行' : '停止'}</div>
          {running && (
            <>
              <div>频率: {frequency.toFixed(1)} Hz</div>
              <div>电流: {current.toFixed(1)} A</div>
            </>
          )}
        </div>
      </Html>

      {/* 选择高亮 */}
      {selected && (
        <mesh position={[0, 0.5, 0]}>
          <boxGeometry args={[1.4, 1.1, 1]} />
          <meshBasicMaterial color="#1890ff" transparent opacity={0.1} />
        </mesh>
      )}
    </group>
  );
};

export default Pump3D;
