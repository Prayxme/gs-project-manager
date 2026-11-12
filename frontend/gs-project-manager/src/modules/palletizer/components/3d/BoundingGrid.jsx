import { Text, Billboard } from '@react-three/drei';

// Colores tomados de la paleta (pizarra) para que el visor combine con la interfaz.
export default function BoundingGrid({ isDarkMode, t }) {
  const texto = isDarkMode ? "#9BA8AB" : "#4A5C6A";
  return (
    <group>
      <mesh position={[20, 42.5, 24]}>
        <boxGeometry args={[40, 85, 48]} />
        <meshBasicMaterial
          color={isDarkMode ? "#CCD0CF" : "#253745"}
          wireframe
          transparent
          opacity={isDarkMode ? 0.18 : 0.35}
        />
      </mesh>
      <Billboard position={[20, -5, 52]}>
        <Text fontSize={3} color={texto}>{t.axisWidth}</Text>
      </Billboard>
      <Billboard position={[-6, -5, 24]}>
        <Text fontSize={3} color={texto}>{t.axisLength}</Text>
      </Billboard>
      <Billboard position={[45, 42.5, 48]}>
        <Text fontSize={3} color={texto}>{t.axisHeight}</Text>
      </Billboard>
    </group>
  );
}
