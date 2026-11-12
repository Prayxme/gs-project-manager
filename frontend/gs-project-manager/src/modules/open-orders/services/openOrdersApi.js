import { createApiClient, fileBody, jsonBody } from "../../../shared/api";
import { contextoLocal } from "../../../shared/utils/dates";

const request = createApiClient("/open-orders");

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
export const setAutoRefresh = (enabled) => request("/auto-refresh", jsonBody({ enabled }, "PUT"));
export const importCompletedCsv = (file) => request("/import-completed", fileBody(file));
