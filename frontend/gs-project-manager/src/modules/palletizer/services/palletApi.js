import { API_BASE_URL } from "../../../shared/api";

// Endpoints del módulo Paletizador en el backend.
const BASE_URL = `${API_BASE_URL}/palletizer`;

const MSG_SIN_CONEXION = "No se pudo conectar con el servidor backend (revisa que Uvicorn esté activo).";

async function request(path, options, mensajePorDefecto) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, options);
  } catch (netErr) {
    throw new Error(MSG_SIN_CONEXION, { cause: netErr });
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
    const detalle = data?.detail;
    throw new Error(
      (typeof detalle === "string" ? detalle : detalle && JSON.stringify(detalle)) || texto || mensajePorDefecto
    );
  }
  if (!data) {
    throw new Error("El servidor devolvió una respuesta vacía.");
  }
  return data;
}

export function parsePdfTicket(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/parse-pdf", { method: "POST", body: formData }, "Error analizando el PDF.");
}

export function packOrder(payload) {
  return request(
    "/pack",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
    "Error del motor de optimización."
  );
}
