import { STATUSES, STATUS_STYLE } from "../constants";

// Indicadores. Los de estado funcionan como filtro rápido al hacer clic.
export default function KpiBar({ summary, t, theme, isDarkMode, statusFilter, onToggleStatus }) {
  if (!summary) return null;
  const card = `rounded-xl border px-3 py-2 text-left transition ${isDarkMode ? "bg-[#11131F]" : "bg-white shadow-sm"}`;
  const extras = [
    ["newToday", summary.new_today],
    ["apptsToday", summary.appointments_today],
    ["completedToday", summary.completed_today],
  ];
  return (
    <div className="grid gap-2 grid-cols-2 sm:grid-cols-4 lg:grid-cols-10">
      <div className={`${card} border-[#0284C7]/50`}>
        <p className={`text-[11px] font-bold uppercase ${theme.textMuted}`}>{t.kpis.total}</p>
        <p className={`text-2xl font-black ${theme.textTitle}`}>{summary.total_active}</p>
      </div>
      {STATUSES.map((s) => {
        const activo = statusFilter.includes(s);
        return (
          <button
            key={s}
            onClick={() => onToggleStatus(s)}
            className={`${card} ${STATUS_STYLE[s].kpi} ${activo ? "ring-2 ring-[#0284C7]" : ""} hover:brightness-110`}
          >
            <p className={`text-[11px] font-bold uppercase ${theme.textMuted}`}>{t.kpis[s]}</p>
            <p className={`text-2xl font-black ${theme.textTitle}`}>{summary.by_status[s] ?? 0}</p>
          </button>
        );
      })}
      {extras.map(([k, v]) => (
        <div key={k} className={`${card} ${isDarkMode ? "border-[#1E2235]" : "border-slate-200"}`}>
          <p className={`text-[11px] font-bold uppercase ${theme.textMuted}`}>{t.kpis[k]}</p>
          <p className={`text-2xl font-black ${theme.textTitle}`}>{v}</p>
        </div>
      ))}
    </div>
  );
}
