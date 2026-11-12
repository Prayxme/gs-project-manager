// Estados del monitor y sus estilos (equivalentes a los colores del Google Sheet).
export const STATUSES = ["OVERDUE", "LAST DAY", "ATTENTION", "SAFE", "TOO EARLY", "ROUTED"];

export const STATUS_STYLE = {
  OVERDUE: { row: "bg-red-500/[0.07]", badge: "bg-red-600 text-white", kpi: "bg-red-500" },
  "LAST DAY": { row: "bg-orange-500/[0.07]", badge: "bg-orange-500 text-white", kpi: "bg-orange-500" },
  ATTENTION: { row: "bg-amber-400/[0.08]", badge: "bg-amber-400 text-slate-900", kpi: "bg-amber-400" },
  SAFE: { row: "", badge: "bg-surface-3 text-ink-2", kpi: "bg-[#4A5C6A]" },
  "TOO EARLY": { row: "opacity-70", badge: "bg-[#9BA8AB] text-[#06141B]", kpi: "bg-[#9BA8AB]" },
  ROUTED: { row: "bg-brand/[0.05]", badge: "bg-brand text-on-brand", kpi: "bg-brand" },
};

export const CLOSED_STYLE = {
  COMPLETED: "bg-brand text-on-brand",
  REMOVED: "bg-amber-400 text-slate-900",
  CANCELLED: "bg-red-600 text-white",
};

// Burlington (BURL y MODE) a tiempo se resalta en azul (ventana de 5 días naturales).
const BURLINGTON = ["BURL", "MODE"];
export const rowStyle = (o) =>
  BURLINGTON.includes(o.customer_code) && o.status === "SAFE"
    ? "bg-sky-500/[0.07]"
    : STATUS_STYLE[o.status]?.row || "";

export const AUTO_REFRESH_POLL_MS = 60_000; // la vista relee la base cada minuto
