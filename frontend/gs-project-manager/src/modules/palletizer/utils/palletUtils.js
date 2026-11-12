// Punto de entrada de las utilidades del paletizador (cada tema vive en su archivo).
export { buildSkuColorMap, colorKey, skuDeLinea } from "./colors";
export { calculateCenteredOffsets } from "./geometry";
export { agruparPallets } from "./grouping";
export { conPalletsDeMargen, margenPorPo } from "./margin";
export { trailerMetrics } from "./metrics";
export { buildPackingPayload, formDesdePdf, lineaVacia } from "./payload";
