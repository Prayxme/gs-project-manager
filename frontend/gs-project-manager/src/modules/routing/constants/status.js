// Estilos por estado de conciliación y por urgencia de la fecha límite.
export const STATUS_STYLE = {
  OK: "bg-brand-soft text-brand-ink",
  UNVERIFIED: "bg-amber-400 text-slate-900",
  MISMATCH: "bg-red-600 text-white",
  NOT_IN_PORTAL: "bg-red-600 text-white",
  ALREADY_ROUTED: "bg-surface-3 text-ink-2",
  NO_ITEMS: "bg-amber-400 text-slate-900",
};

export const ATTENTION_DAYS = 3;

// Urgencia según los días que faltan para la fecha límite.
export function urgency(daysLeft) {
  if (daysLeft === null || daysLeft === undefined) return { key: null, style: "bg-surface-3 text-ink-2" };
  if (daysLeft < 0) return { key: "overdue", style: "bg-red-600 text-white" };
  if (daysLeft === 0) return { key: "today", style: "bg-orange-500 text-white" };
  if (daysLeft <= ATTENTION_DAYS) return { key: "soon", style: "bg-amber-400 text-slate-900" };
  return { key: "later", style: "bg-surface-3 text-ink-2" };
}
