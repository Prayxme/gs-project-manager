// Fecha y zona horaria del navegador: "hoy" depende de dónde se abre la app.
export function contextoLocal() {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const today = new Date().toLocaleDateString("en-CA"); // AAAA-MM-DD en hora local
  return { tz, today };
}

// Fecha y hora en el formato local del navegador ("" si no hay valor).
export const formatDateTime = (ts, opciones) => (ts ? new Date(ts).toLocaleString(undefined, opciones) : "");

// Fecha y hora cortas: "11/12/26, 7:20 AM".
export const formatShortDateTime = (ts) => formatDateTime(ts, { dateStyle: "short", timeStyle: "short" });
