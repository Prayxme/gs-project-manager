import { Text, Billboard } from '@react-three/drei';

export default function BoundingGrid({ isDarkMode, t }) {
  return (
    <group>
      <mesh position={[20, 42.5, 24]}>
        <boxGeometry args={[40, 85, 48]} />
        <meshBasicMaterial
          color={isDarkMode ? "#ffffff" : "#1E293B"}
          wireframe
          transparent
          opacity={isDarkMode ? 0.15 : 0.4}
        />
      </mesh>
      <Billboard position={[20, -5, 52]}>
        <Text fontSize={3} color={isDarkMode ? "#94A3B8" : "#475569"}>
          {t.axisWidth}
        </Text>
      </Billboard>
      <Billboard position={[-6, -5, 24]}>
        <Text fontSize={3} color={isDarkMode ? "#94A3B8" : "#475569"}>
          {t.axisLength}
        </Text>
      </Billboard>
      <Billboard position={[45, 42.5, 48]}>
        <Text fontSize={3} color={isDarkMode ? "#94A3B8" : "#475569"}>
          {t.axisHeight}
        </Text>
      </Billboard>
    </group>
  );
}