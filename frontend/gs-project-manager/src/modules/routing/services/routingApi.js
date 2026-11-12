import { createApiClient } from "../../../shared/api";

const request = createApiClient("/routing");

// PDFs de Pick Tickets -> plan de RTS (conciliado con el portal de Wiesner).
export function planRouting(files, today) {
  const fd = new FormData();
  files.forEach((f) => fd.append("files", f));
  fd.append("today", today);
  return request("/plan", { method: "POST", body: fd }, { requireBody: true });
}
