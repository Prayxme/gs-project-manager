import { createApiClient, fileBody, jsonBody } from "../../../shared/api";

// Endpoints del módulo Paletizador en el backend.
const request = createApiClient("/palletizer", {
  offlineMessage: "No se pudo conectar con el servidor backend (revisa que Uvicorn esté activo).",
});

export const parsePdfTicket = (file) =>
  request("/parse-pdf", fileBody(file), { errorMessage: "Error analizando el PDF.", requireBody: true });

export const packOrder = (payload) =>
  request("/pack", jsonBody(payload), { errorMessage: "Error del motor de optimización.", requireBody: true });
