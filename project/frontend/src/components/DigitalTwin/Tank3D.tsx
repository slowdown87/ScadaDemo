import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html, Text } from '@react-three/drei';
import * as THREE from 'three';
import { Tank3DProps, mediaColors, stateColors } from './types';

// 储罐3D模型组件
const Tank3D: React.FC<Tank3DProps> = ({
  id,
  tankId,
  tankName,
  position,
  level,
  temp,
  conductivity,
  currentMedia,
  state,
  selected = false,
  onClick,
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const liquidRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.PointLight>(null);

  // 颜色计算
  const mediaColor = useMemo(() => mediaColors[currentMedia] || '#4FC3F7', [currentMedia]);
  const stateColor = useMemo(() => stateColors[state], [state]);

  // 液位高度计算 (0.1 到 1.8)
  const liquidHeight = useMemo(() => {
    return 0.1 + (level / 100) * 1.7;
  }, [level]);

  // 温度着色 (蓝色=冷, 红色=热)
  const temperatureColor = useMemo(() => {
    const normalizedTemp = Math.max(0, Math.min(1, (temp - 20) / 80)); // 20-100°C范围
    const r = normalizedTemp;
    const g = 0.5 - normalizedTemp * 0.3;
    const b = 1 - normalizedTemp;
    return new THREE.Color(r, g, b);
  }, [temp]);

  // 动画效果
  useFrame((_, delta) => {
    if (groupRef.current) {
      // 轻微摇晃效果
      groupRef.current.rotation.z = Math.sin(Date.now() * 0.001) * 0.01;
    }

    if (glowRef.current) {
      // 呼吸灯效果
      const intensity = 0.3 + Math.sin(Date.now() * 0.003) * 0.2;
      glowRef.current.intensity = state === 'STEP_EXEC' ? intensity : 0.1;
    }

    if (liquidRef.current) {
      // 液面波动
      liquidRef.current.position.y = liquidHeight / 2;
      const scale = 1 + Math.sin(Date.now() * 0.002) * 0.02;
      liquidRef.current.scale.set(scale, 1, scale);
    }
  });

  return (
    <group ref={groupRef} position={position} onClick={onClick}>
      {/* 储罐底座 */}
      <mesh position={[0, -0.05, 0]} receiveShadow>
        <cylinderGeometry args={[0.6, 0.7, 0.1, 32]} />
        <meshStandardMaterial color="#607D8B" metalness={0.6} roughness={0.4} />
      </mesh>

      {/* 储罐主体 - 圆柱 */}
      <mesh position={[0, 0.5, 0]} castShadow>
        <cylinderGeometry args={[0.5, 0.5, 1.8, 32]} />
        <meshStandardMaterial
          color={stateColor}
          transparent
          opacity={0.3}
          metalness={0.2}
          roughness={0.3}
        />
      </mesh>

      {/* 储罐圆顶 */}
      <mesh position={[0, 1.45, 0]}>
        <sphereGeometry args={[0.5, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshStandardMaterial
          color={stateColor}
          transparent
          opacity={0.4}
          metalness={0.2}
          roughness={0.3}
        />
      </mesh>

      {/* 液体填充 */}
      <mesh ref={liquidRef} position={[0, liquidHeight / 2, 0]}>
        <cylinderGeometry args={[0.48, 0.48, liquidHeight, 32]} />
        <meshStandardMaterial
          color={mediaColor}
          transparent
          opacity={0.7}
          metalness={0.1}
          roughness={0.2}
        />
      </mesh>

      {/* 液面波动效果 */}
      {state === 'STEP_EXEC' && (
        <mesh position={[0, liquidHeight, 0]}>
          <ringGeometry args={[0.3, 0.5, 32]} />
          <meshStandardMaterial
            color={mediaColor}
            transparent
            opacity={0.5}
            side={THREE.DoubleSide}
          />
        </mesh>
      )}

      {/* 温度着色层 */}
      <mesh position={[0, 0.5, 0]}>
        <cylinderGeometry args={[0.52, 0.52, 1.8, 32]} />
        <meshStandardMaterial
          color={temperatureColor}
          transparent
          opacity={0.2}
          metalness={0.1}
          roughness={0.5}
        />
      </mesh>

      {/* 状态指示灯 */}
      <mesh position={[0.6, 1.5, 0]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial
          color={stateColor}
          emissive={stateColor}
          emissiveIntensity={0.8}
        />
      </mesh>

      {/* 温度指示灯 */}
      <mesh position={[-0.6, 1.5, 0]}>
        <sphereGeometry args={[0.08, 16, 16]} />
        <meshStandardMaterial
          color={temperatureColor}
          emissive={temperatureColor}
          emissiveIntensity={0.5}
        />
      </mesh>

      {/* 发光效果 */}
      <pointLight
        ref={glowRef}
        position={[0, 1, 0]}
        color={stateColor}
        intensity={state === 'STEP_EXEC' ? 0.5 : 0.1}
        distance={3}
      />

      {/* 储罐标签 */}
      <Html position={[0, 2, 0]} center distanceFactor={10}>
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
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{tankName}</div>
          <div style={{ color: '#aaa' }}>ID: {tankId}</div>
          <div>液位: {level.toFixed(1)}%</div>
          <div>温度: {temp.toFixed(1)}°C</div>
          <div>电导: {conductivity.toFixed(1)} μS</div>
        </div>
      </Html>

      {/* 选择高亮 */}
      {selected && (
        <mesh position={[0, 1, 0]}>
          <boxGeometry args={[1.4, 2.2, 1.4]} />
          <meshBasicMaterial color="#1890ff" transparent opacity={0.1} />
        </mesh>
      )}
    </group>
  );
};

export default Tank3D;
