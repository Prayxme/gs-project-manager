import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import PalletBase from './PalletBase';
import BoundingGrid from './BoundingGrid';
import Box from './Box';
import { SKU_PALETTE } from '../../constants/palette';
import { colorKey } from '../../utils/palletUtils';

export default function Viewport3D({ palletData, isDarkMode, t, grupoSeleccionadoIdx, skuColorMap, offsets }) {
  // Leyenda: solo las combinaciones PO + SKU presentes en el pallet visible.
  const leyenda = [];
  const vistos = new Set();
  (palletData?.placed_items || []).forEach((item) => {
    const sku = item.sku?.trim() || "UNKNOWN";
    const key = colorKey(item.po, sku);
    if (!vistos.has(key)) {
      vistos.add(key);
      leyenda.push({ key, sku, po: item.po, color: skuColorMap[key] || SKU_PALETTE[0] });
    }
  });

  return (
    <div className="flex-1 flex flex-col relative min-h-[320px] bg-viewport">
      {/* Título y leyenda */}
      <div className="px-4 sm:px-6 py-3 sm:py-4 absolute top-0 left-0 right-0 md:right-auto md:max-w-[calc(100%-360px)] z-10 pointer-events-none">
        <h2 className="text-base sm:text-lg font-black tracking-tight text-ink">{t.viewportTitle}</h2>
        {palletData && (
          <div className="flex flex-wrap gap-1.5 mt-2 pointer-events-auto max-h-20 overflow-y-auto pr-2">
            {leyenda.map(({ key, sku, po, color }) => (
              <span
                key={key}
                title={po ? `${sku} · PO ${po}` : sku}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-bold border border-line bg-surface/90 text-ink-2 backdrop-blur-md shadow-sm max-w-[220px]"
              >
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: color }} />
                <span className="truncate font-mono">
                  {sku}
                  {po && <span className="opacity-60"> · PO {po}</span>}
                </span>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Escena 3D */}
      <div className="flex-1 relative">
        {palletData ? (
          <Canvas camera={{ position: [90, 110, 130], fov: 45 }} className="touch-none">
            <ambientLight intensity={isDarkMode ? 0.65 : 1.1} />
            <directionalLight position={[30, 50, 20]} intensity={isDarkMode ? 1.5 : 1.2} />
            <group position={[-20, -45, -24]} key={`layout-${grupoSeleccionadoIdx}`}>
              <PalletBase />
              <BoundingGrid isDarkMode={isDarkMode} t={t} />
              {palletData.placed_items.map((item, index) => (
                <Box
                  key={`box-${index}`}
                  item={item}
                  color={skuColorMap[colorKey(item.po, item.sku?.trim() || "UNKNOWN")] || SKU_PALETTE[0]}
                  isDarkMode={isDarkMode}
                  offsetX={offsets.x}
                  offsetZ={offsets.z}
                />
              ))}
            </group>
            <OrbitControls makeDefault minPolarAngle={0} maxPolarAngle={Math.PI / 2} />
          </Canvas>
        ) : (
          <div className="w-full h-full flex flex-col items-center justify-center gap-3 px-6 text-center">
            <span className="text-5xl opacity-40" aria-hidden="true">📦</span>
            <p className="text-xs tracking-widest uppercase font-extrabold text-muted">{t.awaitingParameters}</p>
          </div>
        )}
      </div>
    </div>
  );
}
