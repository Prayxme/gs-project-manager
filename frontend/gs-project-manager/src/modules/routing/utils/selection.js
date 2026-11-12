// Selección de órdenes que llega del Monitor por la URL:
//   ?status=OVERDUE&status=LAST%20DAY&cust=BURL120     (cust es opcional)
//   ?scope=urgent                                       (atajo: vencidas, último día y atención)
export const URGENT_STATUSES = ["OVERDUE", "LAST DAY", "ATTENTION"];

export const URGENT_QUERY = { scope: "urgent" };

export function seleccionDesdeUrl(params) {
  const statuses = params.get("scope") === "urgent" ? URGENT_STATUSES : params.getAll("status");
  const cust = statuses.length ? (params.get("cust") || "").trim().toUpperCase() : "";
  // `key` identifica la selección ("" = sin selección: se trabaja con los PDFs subidos).
  return { statuses, cust, key: statuses.length ? `${[...statuses].sort().join(",")}|${cust}` : "" };
}

// Campos de la selección para el backend (query string o FormData).
export function camposDeSeleccion(seleccion) {
  const campos = seleccion.statuses.map((s) => ["status", s]);
  if (seleccion.cust) campos.push(["cust", seleccion.cust]);
  return campos;
}
