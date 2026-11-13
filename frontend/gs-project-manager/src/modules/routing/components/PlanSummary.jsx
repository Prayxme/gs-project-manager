import { Alert } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";

const KPIS = ["pos", "rts", "pallets", "already_routed", "excluded"];

// Estado del portal, archivos subidos, cifras del plan y avisos de lectura de los PDFs.
export default function PlanSummary({ plan, files, t }) {
  const { portal, summary, warnings } = plan;
  return (
    <div className="space-y-3">
      {portal.ok ? (
        <p className="text-xs font-bold text-brand-ink">✔ {fmt(t.portalOk, { n: portal.orders })}</p>
      ) : (
        <Alert kind="warning">{fmt(t.portalDown, { e: portal.error })}</Alert>
      )}
      {plan.preroute && (
        <p className="text-sm font-bold text-ink">
          📊 {fmt(t.pre.intro, { l: plan.preroute.lines, c: plan.preroute.cube.toLocaleString(), k: plan.preroute.cft_per_pallet })}
        </p>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
        {KPIS.map((k) => (
          <div key={k} className="card px-3 py-2">
            <p className="text-[11px] uppercase tracking-wide font-extrabold text-muted">{t.summary[k]}</p>
            <p className={`text-2xl font-black ${k === "excluded" && summary[k] ? "text-red-600" : "text-ink"}`}>
              {summary[k]}
            </p>
          </div>
        ))}
      </div>
      {files.length > 0 && <p className="text-xs text-muted break-words">{t.files}: {files.join(", ")}</p>}
      {warnings.length > 0 && (
        <details className="text-xs text-ink-2">
          <summary className="cursor-pointer font-bold text-amber-700 dark:text-amber-300">
            {fmt(t.warnings, { n: warnings.length })}
          </summary>
          <ul className="mt-1 list-disc pl-5 space-y-0.5">{warnings.map((w, i) => <li key={i}>{w}</li>)}</ul>
        </details>
      )}
    </div>
  );
}
