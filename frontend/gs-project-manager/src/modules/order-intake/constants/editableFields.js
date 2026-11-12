// Campos de la orden que el usuario puede corregir antes de escribir en la hoja.
// key: campo de la orden · col: texto de encabezado (I18N.cols) · w: ancho en escritorio
export const EDITABLE_FIELDS = [
  { key: "company", col: "company", w: "md:w-36" },
  { key: "store", col: "store", w: "md:w-24" },
  { key: "po", col: "po", w: "md:w-28" },
  { key: "containers", col: "containers", w: "md:w-56" },
  { key: "ship_date", col: "ship", w: "md:w-28" },
  { key: "cancel_date", col: "cancel", w: "md:w-28" },
  { key: "ctns", col: "ctns", w: "md:w-20", type: "number" },
];

// En celular estos campos ocupan toda la fila.
export const FULL_WIDTH_MOBILE = new Set(["containers", "company"]);
