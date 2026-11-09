import { API_BASE_URL } from "../../../shared/api";

const BASE_URL = `${API_BASE_URL}/open-orders`;

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
    throw new Error((typeof data?.detail === "string" && data.detail) || texto || `HTTP ${response.status}`);
  }
  return data;
}

// Fecha y zona horaria del navegador: "hoy" depende de dónde se abre la app.
export function contextoLocal() {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const today = new Date().toLocaleDateString("en-CA"); // AAAA-MM-DD en hora local
  return { tz, today };
}

export function getOrders() {
  const { today } = contextoLocal();
  return request(`/orders?today=${today}`);
}

export function getSummary() {
  const { today, tz } = contextoLocal();
  return request(`/summary?today=${today}&tz=${encodeURIComponent(tz)}`);
}

export const refreshNow = () => request("/refresh", { method: "POST" });
export const getEvents = (limit = 500) => request(`/events?limit=${limit}`);
export const getClosed = () => request("/closed");

export const setAutoRefresh = (enabled) =>
  request("/auto-refresh", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled }),
  });

export function importCompletedCsv(file) {
  const fd = new FormData();
  fd.append("file", file);
  return request("/import-completed", { method: "POST", body: fd });
}
