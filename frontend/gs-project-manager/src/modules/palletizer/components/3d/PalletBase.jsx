import { Edges } from '@react-three/drei';

export default function PalletBase() {
  return (
    <mesh position={[20, 2.75, 24]}>
      <boxGeometry args={[40, 5.5, 48]} />
      <meshStandardMaterial color="#5C4033" />
      <Edges color="#3a2820" />
    </mesh>
  );
}