import { API_BASE_URL } from "../../../shared/api";

const BASE_URL = `${API_BASE_URL}/order-intake`;

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, options);
  } catch (netErr) {
    throw new Error("No se pudo conectar con el servidor backend.", { cause: netErr });
  }
  const texto = await response.text();
  let data;
  try {
    data = texto ? JSON.parse(texto) : null;
  } catch {
    data = null;
  }
  if (!response.ok) {
    const d = data?.detail;
    throw new Error((typeof d === "string" && d) || (d && JSON.stringify(d)) || texto || `HTTP ${response.status}`);
  }
  return data;
}

const json = (body) => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export function analyzePdf(file) {
  const fd = new FormData();
  fd.append("file", file);
  return request("/analyze", { method: "POST", body: fd });
}

export const checkOrders = (orders) => request("/check", json({ orders }));
export const applyOrders = (orders, sourceRef) => request("/apply", json({ orders, source_ref: sourceRef }));
export const getSuggestions = () => request("/suggestions");
export const getLog = () => request("/log");

// Campos que el backend espera para cada orden de ingreso.
export const aOrden = (r) => ({
  piktik: String(r.piktik),
  company: r.company,
  store: r.store,
  po: r.po,
  containers: r.containers,
  ship_date: r.ship_date,
  cancel_date: r.cancel_date,
  ctns: Number(r.ctns) || 0,
});
