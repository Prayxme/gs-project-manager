import { createApiClient } from "../../../shared/api";
import { camposDeSeleccion } from "../utils/selection";

const request = createApiClient("/routing");

// PDFs de Pick Tickets -> plan de RTS (conciliado con el portal de Wiesner).
// Con una selección del Monitor, de los PDFs solo se toman las órdenes de esa selección.
export function planRouting(files, today, seleccion) {
  const fd = new FormData();
  files.forEach((f) => fd.append("files", f));
  fd.append("today", today);
  camposDeSeleccion(seleccion).forEach(([k, v]) => fd.append(k, v));
  return request("/plan", { method: "POST", body: fd }, { requireBody: true });
}

// Órdenes del portal sin routing de una selección (estados + Customer No), con los Pick Tickets ya recibidos.
export function selectionPlan(seleccion, today) {
  const query = new URLSearchParams([...camposDeSeleccion(seleccion), ["today", today]]);
  return request(`/selection?${query}`, {}, { requireBody: true });
}
