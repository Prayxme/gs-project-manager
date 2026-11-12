import { LOGISTICS_DEFAULTS } from "../constants/logisticsConfig";

// Estimación de tráiler: pallets, pies cúbicos, RTs necesarios y peso bruto (con madera).
export function trailerMetrics(grupos, items) {
  const totalPallets = grupos.reduce((acc, g) => acc + g.count, 0);
  const totalCubeFeet = totalPallets * LOGISTICS_DEFAULTS.CFT_POR_PALLET;
  const totalNetWeight = items.reduce((acc, i) => acc + Number(i.qty) * Number(i.weight), 0);
  return {
    totalPallets,
    totalCubeFeet,
    numRTs: Math.ceil(totalCubeFeet / LOGISTICS_DEFAULTS.MAX_CFT_POR_RT),
    totalGrossWeight: totalNetWeight + totalPallets * LOGISTICS_DEFAULTS.PESO_MADERA_LBS,
  };
}
