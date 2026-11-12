import { STATUSES, STATUS_STYLE } from "../constants";

// Indicadores. Los de estado funcionan como filtro rápido al hacer clic.
export default function KpiBar({ summary, t, statusFilter, onToggleStatus }) {
  if (!summary) return null;
  const tarjeta = "card relative overflow-hidden px-3 py-2.5 text-left";
  const franja = (cls) => <span className={`absolute left-0 top-0 bottom-0 w-1 ${cls}`} />;
  const extras = [
    ["newToday", summary.new_today],
    ["apptsToday", summary.appointments_today],
    ["completedToday", summary.completed_today],
  ];
  return (
    <div className="space-y-2">
      <div className="grid gap-2 grid-cols-2 sm:grid-cols-4 xl:grid-cols-7">
        <div className={`${tarjeta} col-span-2 sm:col-span-1`}>
          {franja("bg-[#253745] dark:bg-[#CCD0CF]")}
          <p className="text-[11px] font-bold uppercase tracking-wide text-muted">{t.kpis.total}</p>
          <p className="text-2xl font-black text-ink">{summary.total_active}</p>
        </div>
        {STATUSES.map((s) => {
          const activo = statusFilter.includes(s);
          return (
            <button
              key={s}
              onClick={() => onToggleStatus(s)}
              aria-pressed={activo}
              className={`${tarjeta} transition hover:border-brand/60 ${activo ? "ring-2 ring-brand border-brand" : ""}`}
            >
              {franja(STATUS_STYLE[s].kpi)}
              <p className="text-[11px] font-bold uppercase tracking-wide text-muted">{t.kpis[s]}</p>
              <p className="text-2xl font-black text-ink">{summary.by_status[s] ?? 0}</p>
            </button>
          );
        })}
      </div>
      <div className="grid gap-2 grid-cols-3">
        {extras.map(([k, v]) => (
          <div key={k} className="rounded-xl bg-brand-soft px-3 py-2 flex flex-col sm:flex-row sm:items-baseline sm:gap-2">
            <span className="text-lg font-black text-brand-ink">{v}</span>
            <span className="text-[11px] font-bold uppercase tracking-wide text-brand-ink/80">{t.kpis[k]}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
