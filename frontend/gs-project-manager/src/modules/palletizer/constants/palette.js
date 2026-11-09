export const SKU_PALETTE = [
  "#0284C7", "#059669", "#DB2777", "#D97706", "#7C3AED", "#EA580C", "#0D9488", "#DC2626", "#4F46E5", "#16A34A",
  "#C026D3", "#0891B2", "#CA8A04", "#9333EA", "#E11D48", "#047857", "#2563EB", "#C2410C", "#65A30D", "#0F766E",
  "#4338CA", "#BE185D", "#6D28D9", "#0369A1", "#A21CAF", "#4D7C0F", "#B91C1C", "#A16207", "#15803D", "#9F1239"
];

// Color único para el índice n. Usa la paleta fija y, si se agota, genera
// tonos nuevos con el ángulo áureo para que nunca se repita un color.
export function colorPorIndice(n) {
  if (n < SKU_PALETTE.length) return SKU_PALETTE[n];
  const k = n - SKU_PALETTE.length;
  const hue = Math.round((k * 137.508) % 360);
  const light = 38 + (Math.floor(k / 12) % 3) * 9;
  return `hsl(${hue}, 70%, ${light}%)`;
}
