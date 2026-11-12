import { createApiClient, fileBody, jsonBody } from "../../../shared/api";

const request = createApiClient("/order-intake");

export const analyzePdf = (file) => request("/analyze", fileBody(file));
export const checkOrders = (orders) => request("/check", jsonBody({ orders }));
export const applyOrders = (orders, sourceRef) => request("/apply", jsonBody({ orders, source_ref: sourceRef }));
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
