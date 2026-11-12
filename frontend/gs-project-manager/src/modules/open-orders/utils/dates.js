// Fechas del portal: llegan como MM/DD/YY ("00/00/00" = vacía) o ISO (AAAA-MM-DD) desde el backend.

// "2026-11-12" -> "11/12/26"
export const isoAMdy = (iso) => (iso ? `${iso.slice(5, 7)}/${iso.slice(8, 10)}/${iso.slice(2, 4)}` : "");

// "11/12/26" -> "261112" (para ordenar columnas por fecha)
export const mdyOrdenable = (mdy) =>
  mdy && mdy !== "00/00/00" ? `${mdy.slice(6)}${mdy.slice(0, 2)}${mdy.slice(3, 5)}` : "";

// "00/00/00" -> ""
export const limpiarFecha = (mdy) => (mdy === "00/00/00" ? "" : mdy);
