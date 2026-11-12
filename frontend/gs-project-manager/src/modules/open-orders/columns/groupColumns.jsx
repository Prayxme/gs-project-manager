import { activeColumns } from "./activeColumns";

// Dentro de un grupo (un estado + un Customer No) sobran las columnas que ya da el encabezado.
const OCULTAS = new Set(["priority_rank", "cust", "notes", "last_change_at"]);

export const groupColumns = (t) => activeColumns(t).filter((c) => !OCULTAS.has(c.key));
