import { API_BASE_URL, createApiClient, fileBody, jsonBody } from "../../../shared/api";

const request = createApiClient("/order-intake");

export const analyzePdf = (file) => request("/analyze", fileBody(file));
export const checkOrders = (orders) => request("/check", jsonBody({ orders }));
export const applyOrders = (orders, sourceRef, inboxId = null) =>
  request("/apply", jsonBody({ orders, source_ref: sourceRef, inbox_id: inboxId }));
export const getSuggestions = () => request("/suggestions");
export const getLog = () => request("/log");

// Bandeja de Gmail
export const getInbox = (all = false) => request(`/inbox${all ? "?all=true" : ""}`);
export const checkGmailNow = () => request("/inbox/check", { method: "POST" });
export const analyzeInboxItem = (id) => request(`/inbox/${id}/analyze`, { method: "POST" });
export const dismissInboxItem = (id) => request(`/inbox/${id}/dismiss`, { method: "POST" });
export const restoreInboxItem = (id) => request(`/inbox/${id}/restore`, { method: "POST" });
export const inboxPdfUrl = (id) => `${API_BASE_URL}/order-intake/inbox/${id}/pdf`;

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
