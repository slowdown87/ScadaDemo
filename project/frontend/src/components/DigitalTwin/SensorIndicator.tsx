import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';
import * as THREE from 'three';
import { SensorIndicator3DProps } from './types';

// 传感器类型配置
const sensorConfig: Record<
  string,
  { label: string; unit: string; color: string; icon: string }
> = {
  TT: { label: '温度', unit: '°C', color: '#EF5350', icon: 'T' },
  PT: { label: '压力', unit: 'bar', color: '#FFA726', icon: 'P' },
  FT: { label: '流量', unit: 'm³/h', color: '#42A5F5', icon: 'F' },
  CD: { label: '电导', unit: 'μS/cm', color: '#66BB6A', icon: 'C' },
};

// 传感器3D指示器组件
const SensorIndicator: React.FC<SensorIndicator3DProps> = ({
  id,
  sensorId,
  sensorName,
  sensorType,
  position,
  value,
  unit,
  alarm = false,
  alarmLow,
  alarmHigh,
  selected = false,
  onClick,
}) => {
  const indicatorRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const pulseRef = useRef<THREE.Mesh>(null);

  // 传感器配置
  const config = useMemo(() => sensorConfig[sensorType] || sensorConfig.TT, [sensorType]);

  // 计算颜色（基于报警状态）
  const indicatorColor = useMemo(() => {
    if (!alarm) return config.color;
    
    // 检查是否超出报警范围
    if (alarmHigh !== undefined && value > alarmHigh) return '#ff4d4f';
    if (alarmLow !== undefined && value < alarmLow) return '#ff4d4f';
    return config.color;
  }, [alarm, value, alarmLow, alarmHigh, config.color]);

  // 是否闪烁
  const isFlashing = useMemo(() => {
    if (!alarm) return false;
    if (alarmHigh !== undefined && value > alarmHigh) return true;
    if (alarmLow !== undefined && value < alarmLow) return true;
    return false;
  }, [alarm, value, alarmLow, alarmHigh]);

  // 动画效果
  useFrame(() => {
    if (ringRef.current) {
      // 外环旋转
      ringRef.current.rotation.z += 0.02;
    }

    if (pulseRef.current) {
      // 脉冲效果（报警时）
      if (isFlashing) {
        const scale = 1 + Math.sin(Date.now() * 0.01) * 0.2;
        pulseRef.current.scale.setScalar(scale);
        pulseRef.current.visible = true;
      } else {
        pulseRef.current.visible = false;
      }
    }
  });

  return (
    <group position={position} onClick={onClick}>
      {/* 传感器主体 */}
      <mesh ref={indicatorRef} castShadow>
        <cylinderGeometry args={[0.12, 0.12, 0.05, 32]} />
        <meshStandardMaterial
          color="#37474F"
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>

      {/* 显示面 */}
      <mesh position={[0, 0.03, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.1, 32]} />
        <meshStandardMaterial
          color="#263238"
          metalness={0.3}
          roughness={0.7}
        />
      </mesh>

      {/* 指示灯 */}
      <mesh position={[0, 0.06, 0]}>
        <sphereGeometry args={[0.05, 16, 16]} />
        <meshStandardMaterial
          color={indicatorColor}
          emissive={indicatorColor}
          emissiveIntensity={isFlashing ? 1.5 : 0.8}
        />
      </mesh>

      {/* 旋转光环 */}
      <mesh ref={ringRef} position={[0, 0.06, 0]}>
        <torusGeometry args={[0.09, 0.01, 8, 32]} />
        <meshStandardMaterial
          color={indicatorColor}
          emissive={indicatorColor}
          emissiveIntensity={0.5}
          transparent
          opacity={0.6}
        />
      </mesh>

      {/* 脉冲光环（报警时） */}
      <mesh ref={pulseRef} position={[0, 0.06, 0]}>
        <ringGeometry args={[0.1, 0.15, 32]} />
        <meshBasicMaterial
          color="#ff4d4f"
          transparent
          opacity={0.5}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* 类型标识 */}
      <mesh position={[0, 0.08, 0.06]}>
        <planeGeometry args={[0.06, 0.06]} />
        <meshBasicMaterial color={config.color} transparent opacity={0.8} />
      </mesh>

      {/* 传感器标签 */}
      <Html position={[0, 0.3, 0]} center distanceFactor={8} rotation={[0, 0, 0]}>
        <div
          style={{
            background: 'rgba(0,0,0,0.9)',
            padding: '8px 12px',
            borderRadius: '6px',
            color: '#fff',
            fontSize: '12px',
            whiteSpace: 'nowrap',
            border: selected ? '2px solid #1890ff' : '1px solid #444',
            boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
            pointerEvents: 'none',
            minWidth: '120px',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              color: config.color,
              fontWeight: 'bold',
              fontSize: '14px',
              marginBottom: '4px',
            }}
          >
            {config.icon} {value.toFixed(1)} {unit}
          </div>
          <div style={{ color: '#aaa', fontSize: '10px', marginBottom: '2px' }}>
            {sensorId}
          </div>
          <div style={{ color: '#ccc', fontSize: '11px' }}>{sensorName}</div>
          {alarm && (
            <div
              style={{
                color: '#ff4d4f',
                fontSize: '10px',
                marginTop: '4px',
                fontWeight: 'bold',
              }}
            >
              {isFlashing ? '报警!' : '监控中'}
            </div>
          )}
          {alarmLow !== undefined && alarmHigh !== undefined && (
            <div style={{ color: '#888', fontSize: '9px', marginTop: '2px' }}>
              范围: {alarmLow} - {alarmHigh}
            </div>
          )}
        </div>
      </Html>

      {/* 传感器支架 */}
      <mesh position={[0, -0.02, 0]}>
        <cylinderGeometry args={[0.02, 0.02, 0.05, 8]} />
        <meshStandardMaterial
          color="#546E7A"
          metalness={0.6}
          roughness={0.4}
        />
      </mesh>

      {/* 报警时的发光效果 */}
      {isFlashing && (
        <pointLight
          position={[0, 0.1, 0]}
          color="#ff4d4f"
          intensity={1}
          distance={1}
        />
      )}

      {/* 选择高亮 */}
      {selected && (
        <>
          <mesh position={[0, 0.03, 0]}>
            <ringGeometry args={[0.13, 0.16, 32]} />
            <meshBasicMaterial color="#1890ff" transparent opacity={0.8} />
          </mesh>
        </>
      )}
    </group>
  );
};

export default SensorIndicator;
