import { API_BASE_URL } from "./config";

export const MSG_SIN_CONEXION = "No se pudo conectar con el servidor backend.";

// Texto de error legible a partir de la respuesta de FastAPI ({ detail: "..." } o lista de errores).
function mensajeDeError(data, texto, porDefecto) {
  const detalle = data?.detail;
  if (typeof detalle === "string" && detalle) return detalle;
  if (detalle) return JSON.stringify(detalle);
  return texto || porDefecto;
}

/**
 * Cliente HTTP de un módulo: createApiClient("/open-orders") -> request(path, options, opciones).
 * opciones: { errorMessage, requireBody } (mensaje si el servidor no explica el error, y si una
 * respuesta vacía debe tratarse como error).
 */
export function createApiClient(prefix, { offlineMessage = MSG_SIN_CONEXION } = {}) {
  const base = `${API_BASE_URL}${prefix}`;

  return async function request(path, options = {}, { errorMessage, requireBody = false } = {}) {
    let response;
    try {
      response = await fetch(`${base}${path}`, options);
    } catch (netErr) {
      throw new Error(offlineMessage, { cause: netErr });
    }
    // El cuerpo solo puede leerse una vez: se lee como texto y luego se interpreta.
    const texto = await response.text();
    let data;
    try {
      data = texto ? JSON.parse(texto) : null;
    } catch {
      data = null;
    }
    if (!response.ok) {
      throw new Error(mensajeDeError(data, texto, errorMessage || `HTTP ${response.status}`));
    }
    if (requireBody && !data) {
      throw new Error("El servidor devolvió una respuesta vacía.");
    }
    return data;
  };
}

// Opciones de fetch para enviar JSON.
export const jsonBody = (body, method = "POST") => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

// Opciones de fetch para subir un archivo en el campo "file".
export function fileBody(file) {
  const fd = new FormData();
  fd.append("file", file);
  return { method: "POST", body: fd };
}
