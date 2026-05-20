import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { Valve3DProps, mediaColors } from './types';

// 阀门3D模型组件
const Valve3D: React.FC<Valve3DProps> = ({
  id,
  valveId,
  valveName,
  position,
  open,
  openPercent,
  mediaType,
  selected = false,
  onClick,
}) => {
  const groupRef = useRef<THREE.Group>(null);
  const handleRef = useRef<THREE.Mesh>(null);
  const indicatorRef = useRef<THREE.Mesh>(null);

  // 阀门颜色（基于开度）
  const valveColor = useMemo(() => {
    if (!open) return '#8c8c8c'; // 关闭 - 灰色
    if (openPercent > 80) return '#52c41a'; // 大开 - 绿色
    if (openPercent > 20) return '#faad14'; // 中开 - 黄色
    return '#ff4d4f'; // 小开 - 红色
  }, [open, openPercent]);

  // 介质颜色
  const mediaColor = useMemo(() => {
    return mediaColors[mediaType] || '#90A4AE';
  }, [mediaType]);

  // 手柄旋转角度（基于开度）
  const handleRotation = useMemo(() => {
    return (openPercent / 100) * Math.PI * 1.5 - Math.PI * 0.75;
  }, [openPercent]);

  // 动画效果
  useFrame((_, delta) => {
    if (handleRef.current) {
      // 平滑转动
      const targetRotation = handleRotation;
      handleRef.current.rotation.y += (targetRotation - handleRef.current.rotation.y) * 0.1;
    }

    if (indicatorRef.current) {
      // 指示灯脉冲
      if (open) {
        indicatorRef.current.scale.setScalar(1 + Math.sin(Date.now() * 0.005) * 0.1);
      } else {
        indicatorRef.current.scale.setScalar(1);
      }
    }

    if (groupRef.current) {
      // 轻微振动（开阀时）
      if (open && openPercent > 50) {
        groupRef.current.position.y = position[1] + Math.sin(Date.now() * 0.01) * 0.01;
      }
    }
  });

  return (
    <group ref={groupRef} position={position} onClick={onClick}>
      {/* 阀门底座 */}
      <mesh position={[0, 0.1, 0]} receiveShadow>
        <boxGeometry args={[0.4, 0.2, 0.4]} />
        <meshStandardMaterial
          color="#607D8B"
          metalness={0.6}
          roughness={0.4}
        />
      </mesh>

      {/* 阀门主体 */}
      <mesh position={[0, 0.3, 0]} castShadow>
        <sphereGeometry args={[0.2, 32, 32]} />
        <meshStandardMaterial
          color={valveColor}
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>

      {/* 阀杆 */}
      <mesh position={[0, 0.55, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 0.2, 16]} />
        <meshStandardMaterial
          color="#78909C"
          metalness={0.6}
          roughness={0.4}
        />
      </mesh>

      {/* 手柄（可旋转） */}
      <group ref={handleRef} position={[0, 0.65, 0]}>
        {/* 手柄横杆 */}
        <mesh rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.03, 0.03, 0.4, 16]} />
          <meshStandardMaterial
            color="#455A64"
            metalness={0.7}
            roughness={0.3}
          />
        </mesh>
        {/* 手柄端点 */}
        <mesh position={[0.2, 0, 0]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshStandardMaterial
            color="#37474F"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        <mesh position={[-0.2, 0, 0]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshStandardMaterial
            color="#37474F"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
      </group>

      {/* 状态指示灯 */}
      <mesh ref={indicatorRef} position={[0.25, 0.3, 0]}>
        <sphereGeometry args={[0.04, 16, 16]} />
        <meshStandardMaterial
          color={valveColor}
          emissive={valveColor}
          emissiveIntensity={0.8}
        />
      </mesh>

      {/* 介质颜色环 */}
      <mesh position={[0, 0.3, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.22, 0.02, 8, 32]} />
        <meshStandardMaterial
          color={mediaColor}
          emissive={mediaColor}
          emissiveIntensity={0.3}
        />
      </mesh>

      {/* 阀位刻度 */}
      {[0, 25, 50, 75, 100].map((percent, i) => {
        const angle = (percent / 100) * Math.PI * 1.5 - Math.PI * 0.75;
        return (
          <mesh
            key={percent}
            position={[
              0.28 * Math.cos(angle),
              0.55 + 0.08 * Math.sin(angle - Math.PI / 2),
              0,
            ]}
          >
            <boxGeometry args={[0.02, 0.02, 0.04]} />
            <meshStandardMaterial
              color={percent === openPercent ? '#fff' : '#555'}
              emissive={percent === openPercent ? '#fff' : '#000'}
              emissiveIntensity={percent === openPercent ? 0.5 : 0}
            />
          </mesh>
        );
      })}

      {/* 阀门标签 */}
      <Html position={[0, 1, 0]} center distanceFactor={10}>
        <div
          style={{
            background: 'rgba(0,0,0,0.8)',
            padding: '6px 10px',
            borderRadius: '4px',
            color: '#fff',
            fontSize: '11px',
            whiteSpace: 'nowrap',
            border: selected ? '2px solid #1890ff' : '1px solid #555',
            pointerEvents: 'none',
          }}
        >
          <div style={{ fontWeight: 'bold', marginBottom: '2px' }}>{valveName}</div>
          <div style={{ color: '#aaa' }}>ID: {valveId}</div>
          <div>
            状态: {open ? '开启' : '关闭'} {openPercent}%
          </div>
        </div>
      </Html>

      {/* 选择高亮 */}
      {selected && (
        <mesh position={[0, 0.3, 0]}>
          <sphereGeometry args={[0.35, 16, 16]} />
          <meshBasicMaterial color="#1890ff" transparent opacity={0.15} />
        </mesh>
      )}

      {/* 打开时的发光效果 */}
      {open && openPercent > 20 && (
        <pointLight
          position={[0, 0.3, 0]}
          color={valveColor}
          intensity={0.3}
          distance={1}
        />
      )}
    </group>
  );
};

export default Valve3D;
