// "2026-11-17" -> "11/17/26" (formato de fechas de Wiesner).
export function usDate(iso) {
  if (!iso) return "";
  const [y, m, d] = iso.split("-");
  return `${m}/${d}/${y.slice(2)}`;
}

// Dirección SHIP TO en una línea: "570 EAST MILL STREET, SAN BERNARDINO, CA 92408".
export function addressLine(shipTo) {
  if (!shipTo) return "";
  const ciudad = [shipTo.city, [shipTo.state, shipTo.zip].filter(Boolean).join(" ")].filter(Boolean).join(", ");
  return [shipTo.street, ciudad].filter(Boolean).join(", ") || shipTo.text || "";
}
