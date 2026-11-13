// Pre Routing: líneas de POs sin Pick Ticket. Weight y Cube son POR CARTÓN.

// Columnas de la tabla editable: [campo, tipo de input, ancho]. Los textos están en i18n (t.pre.cols).
export const PRE_COLUMNS = [
  ["cust", "text", "w-24"],
  ["po", "text", "w-28"],
  ["ship_date", "date", "w-36"],
  ["cancel_date", "date", "w-36"],
  ["qty", "number", "w-20"],
  ["cases", "number", "w-20"],
  ["weight", "number", "w-20"],
  ["cube", "number", "w-20"],
  ["style", "text", "w-28"],
  ["color", "text", "w-24"],
  ["ship_to", "text", "w-28"],
];

let serie = 0;
// `id` solo sirve para la interfaz (clave de fila); el backend lo ignora.
export const nuevaLinea = (datos = {}) => ({
  cust: "", po: "", ship_date: "", cancel_date: "", qty: "", cases: "", weight: "", cube: "",
  style: "", color: "", ship_to: "", ...datos, id: `${Date.now()}-${serie++}`,
});

const num = (v) => Number(v) || 0;

// Totales de lo escrito: cartones, lb (cartones × peso) y cubo (cartones × cubo) de todas las líneas.
export function totalesPreRoute(lineas) {
  return lineas.reduce(
    (t, l) => ({
      pos: t.pos.add(`${l.cust}|${l.po}`),
      units: t.units + num(l.qty),
      cases: t.cases + num(l.cases),
      weight: t.weight + num(l.cases) * num(l.weight),
      cube: t.cube + num(l.cases) * num(l.cube),
    }),
    { pos: new Set(), units: 0, cases: 0, weight: 0, cube: 0 },
  );
}

// Líneas con algo escrito, sin el `id` de la interfaz, para enviar al backend.
export const lineasParaEnviar = (lineas) =>
  lineas
    .filter((l) => String(l.cust).trim() || String(l.po).trim())
    .map((l) => Object.fromEntries(Object.entries(l).filter(([campo]) => campo !== "id")));
