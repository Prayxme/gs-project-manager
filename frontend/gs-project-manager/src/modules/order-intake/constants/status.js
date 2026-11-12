// Clasificación de cada PikTik frente a la hoja de control.
export const STATUS_STYLE = {
  NEW: "bg-brand text-on-brand",
  REVISION: "bg-amber-400 text-slate-900",
  REGISTERED: "bg-surface-3 text-muted",
};

export const STATUS_ORDER = ["NEW", "REVISION", "REGISTERED"];

// Estado de cada PDF en la bandeja de Gmail.
export const INBOX_STYLE = {
  PENDING: "bg-amber-400 text-slate-900",
  NO_CHANGES: "bg-surface-3 text-muted",
  APPLIED: "bg-brand text-on-brand",
  DISMISSED: "bg-surface-3 text-muted line-through",
  ERROR: "bg-red-600 text-white",
};

export const INBOX_REFRESH_MS = 120_000; // la vista relee la bandeja cada 2 minutos
