import { Alert } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";

const KPIS = ["pos", "rts", "pallets", "excluded"];

// Estado del portal, cifras del plan y avisos de lectura de los PDFs.
export default function PlanSummary({ plan, files, t }) {
  const { portal, summary, warnings } = plan;
  return (
    <div className="space-y-3">
      {portal.ok ? (
        <p className="text-xs font-bold text-brand-ink">✔ {fmt(t.portalOk, { n: portal.orders })}</p>
      ) : (
        <Alert kind="warning">{fmt(t.portalDown, { e: portal.error })}</Alert>
      )}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {KPIS.map((k) => (
          <div key={k} className="card px-3 py-2">
            <p className="text-[11px] uppercase tracking-wide font-extrabold text-muted">{t.summary[k]}</p>
            <p className={`text-2xl font-black ${k === "excluded" && summary[k] ? "text-red-600" : "text-ink"}`}>
              {summary[k]}
            </p>
          </div>
        ))}
      </div>
      <p className="text-xs text-muted break-words">{t.files}: {files.join(", ")}</p>
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
