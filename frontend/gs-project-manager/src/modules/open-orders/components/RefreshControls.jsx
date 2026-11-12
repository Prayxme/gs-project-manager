import { fmt } from "../../../shared/i18n/format";

// Casilla de actualización automática + botón "Actualizar ahora".
export default function RefreshControls({ summary, refrescando, onToggleAuto, onRefresh, t }) {
  return (
    <>
      <label className="flex items-center gap-2 text-sm font-bold text-ink cursor-pointer select-none">
        <input
          type="checkbox"
          className="w-4 h-4 accent-[var(--brand)]"
          checked={!!summary?.auto_refresh}
          onChange={onToggleAuto}
        />
        {fmt(t.auto, { n: summary?.auto_refresh_minutes ?? 5 })}
      </label>
      <button onClick={onRefresh} disabled={refrescando} className="btn-primary">
        {refrescando ? t.updating : `🔄 ${t.updateNow}`}
      </button>
    </>
  );
}
