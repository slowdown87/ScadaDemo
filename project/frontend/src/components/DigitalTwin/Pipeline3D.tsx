import React, { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Pipeline3DProps, mediaColors, MediaType } from './types';

// 管道类型颜色映射
const pipelineTypeColors: Record<string, string> = {
  raw: '#FFB74D',       // 原料管道 - 橙色
  clean: '#4FC3F7',     // 清水管道 - 蓝色
  process: '#66BB6A',   // 工艺管道 - 绿色
  bypass: '#BDBDBD',    // 旁通管道 - 灰色
};

// 管道3D模型组件
const Pipeline3D: React.FC<Pipeline3DProps> = ({
  id,
  startPoint,
  endPoint,
  radius = 0.08,
  mediaType,
  flowRate,
  active = false,
}) => {
  const flowRef = useRef<THREE.Mesh[]>([]);
  const arrowRef = useRef<THREE.Group>(null);

  // 管道颜色
  const pipeColor = useMemo(() => {
    // 根据介质类型或管道类型选择颜色
    if (mediaType && mediaType !== MediaType.PURE_WATER) {
      return mediaColors[mediaType];
    }
    // 默认灰色
    return '#90A4AE';
  }, [mediaType]);

  // 计算管道长度和方向
  const { length, midpoint, direction, rotation } = useMemo(() => {
    const start = new THREE.Vector3(...startPoint);
    const end = new THREE.Vector3(...endPoint);
    const len = start.distanceTo(end);
    const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
    const dir = new THREE.Vector3().subVectors(end, start).normalize();
    
    // 计算旋转角度
    const axis = new THREE.Vector3(0, 1, 0);
    const quaternion = new THREE.Quaternion().setFromUnitVectors(axis, dir);
    const euler = new THREE.Euler().setFromQuaternion(quaternion);
    
    return {
      length: len,
      midpoint: mid.toArray() as [number, number, number],
      direction: dir.toArray() as [number, number, number],
      rotation: [euler.x, euler.y, euler.z] as [number, number, number],
    };
  }, [startPoint, endPoint]);

  // 流动粒子数量
  const particleCount = useMemo(() => {
    return Math.max(3, Math.floor(length * 2));
  }, [length]);

  // 流动动画
  useFrame((_, delta) => {
    if (active && flowRate > 0) {
      // 粒子流动
      flowRef.current.forEach((mesh, i) => {
        if (mesh) {
          const speed = flowRate * 0.01;
          const offset = (Date.now() * speed + i * 0.5) % 1;
          const start = new THREE.Vector3(...startPoint);
          const end = new THREE.Vector3(...endPoint);
          const pos = new THREE.Vector3().lerpVectors(start, end, offset);
          mesh.position.copy(pos);
        }
      });

      // 箭头旋转
      if (arrowRef.current) {
        arrowRef.current.rotation.z += delta * 2;
      }
    }
  });

  return (
    <group>
      {/* 主管道 */}
      <mesh
        position={midpoint}
        rotation={rotation}
        castShadow
      >
        <cylinderGeometry args={[radius, radius, length, 16]} />
        <meshStandardMaterial
          color={pipeColor}
          metalness={0.6}
          roughness={0.3}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* 管道连接头 - 起点 */}
      <mesh position={startPoint}>
        <sphereGeometry args={[radius * 1.5, 16, 16]} />
        <meshStandardMaterial
          color={pipeColor}
          metalness={0.7}
          roughness={0.2}
        />
      </mesh>

      {/* 管道连接头 - 终点 */}
      <mesh position={endPoint}>
        <sphereGeometry args={[radius * 1.5, 16, 16]} />
        <meshStandardMaterial
          color={pipeColor}
          metalness={0.7}
          roughness={0.2}
        />
      </mesh>

      {/* 流动箭头（运行时显示） */}
      {active && flowRate > 0 && (
        <>
          {/* 流动粒子 */}
          {Array.from({ length: particleCount }).map((_, i) => (
            <mesh
              key={`particle-${i}`}
              ref={(el) => {
                if (el) flowRef.current[i] = el;
              }}
              position={startPoint}
            >
              <sphereGeometry args={[radius * 0.8, 8, 8]} />
              <meshBasicMaterial
                color={pipeColor}
                transparent
                opacity={0.8}
              />
            </mesh>
          ))}

          {/* 方向箭头 */}
          <group
            ref={arrowRef}
            position={[
              (startPoint[0] + endPoint[0]) / 2,
              (startPoint[1] + endPoint[1]) / 2 + 0.1,
              (startPoint[2] + endPoint[2]) / 2,
            ]}
          >
            <mesh
              rotation={[
                Math.PI / 2,
                Math.atan2(
                  endPoint[2] - startPoint[2],
                  endPoint[0] - startPoint[0]
                ),
                0,
              ]}
            >
              <coneGeometry args={[0.1, 0.2, 8]} />
              <meshBasicMaterial color="#FFFFFF" transparent opacity={0.8} />
            </mesh>
          </group>

          {/* 流动光效 */}
          <pointLight
            position={midpoint}
            color={pipeColor}
            intensity={0.2}
            distance={length / 2}
          />
        </>
      )}

      {/* 高压管道加强圈 */}
      {active && flowRate > 50 && (
        <>
          <mesh position={startPoint}>
            <torusGeometry args={[radius * 1.8, radius * 0.3, 8, 16]} />
            <meshStandardMaterial
              color="#607D8B"
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>
          <mesh position={endPoint}>
            <torusGeometry args={[radius * 1.8, radius * 0.3, 8, 16]} />
            <meshStandardMaterial
              color="#607D8B"
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>
        </>
      )}
    </group>
  );
};

export default Pipeline3D;
