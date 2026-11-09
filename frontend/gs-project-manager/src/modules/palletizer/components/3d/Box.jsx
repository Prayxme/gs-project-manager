import { Edges } from '@react-three/drei';

export default function Box({ item, color, isDarkMode, offsetX, offsetZ }) {
  const { x, y, z } = item.position;
  const { width_in, height_in, length_in } = item.rendered_dimensions;
  const centerX = x + offsetX + width_in / 2;
  const centerY = y + height_in / 2;
  const centerZ = z + offsetZ + length_in / 2;

  return (
    <mesh position={[centerX, centerY, centerZ]}>
      <boxGeometry args={[width_in, height_in, length_in]} />
      <meshStandardMaterial color={color || "#0284C7"} transparent opacity={0.88} />
      <Edges
        color={isDarkMode ? "#ffffff" : "#0F172A"}
        transparent
        opacity={isDarkMode ? 0.35 : 0.65}
      />
    </mesh>
  );
}