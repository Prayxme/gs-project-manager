import { Badge } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";

// Selección de órdenes que viene del Monitor (estados + Customer No) y su resultado.
export default function SelectionBar({ seleccion, plan, busy, onRecalc, onClear, t }) {
  if (!seleccion.key) return null;
  const info = plan?.selection;
  return (
    <section className="card p-3 sm:p-4 space-y-2 border-brand/40">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-sm font-black text-ink">🎯 {t.selectionTitle}:</span>
          {seleccion.statuses.map((s) => <Badge key={s} className="bg-surface-3 text-ink-2">{s}</Badge>)}
          <Badge className="bg-brand-soft text-brand-ink">{seleccion.cust || t.allCustomers}</Badge>
        </div>
        <div className="flex gap-2">
          <button type="button" className="btn-secondary" disabled={busy} onClick={onRecalc}>↻ {t.recalc}</button>
          <button type="button" className="btn-secondary" disabled={busy} onClick={onClear}>✕ {t.clearSelection}</button>
        </div>
      </div>
      {info && (
        <p className="text-sm font-bold text-ink-2">
          {fmt(t.selectionIntro, { n: info.orders, m: plan.summary.missing })}
          {info.ignored > 0 && <span className="text-muted"> {fmt(t.selectionIgnored, { n: info.ignored })}</span>}
        </p>
      )}
      <p className="text-xs text-muted">{t.selectionUploadHint}</p>
    </section>
  );
}
