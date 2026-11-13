import { FileButton } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";
import { totalesPreRoute } from "../utils/preroute";
import PreRouteTable from "./PreRouteTable";

// Pre Routing: POs sin Pick Ticket. Se importan de un Excel o se escriben a mano, se revisan y se calculan.
export default function PreRoutePanel({ pre, busy, t }) {
  const tot = totalesPreRoute(pre.lines);
  const cifra = (n) => n.toLocaleString(undefined, { maximumFractionDigits: 1 });
  return (
    <section className="card p-3 sm:p-4 space-y-3">
      <div className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
        <div className="min-w-0">
          <h3 className="text-base font-black text-ink">{t.pre.title}</h3>
          <p className="text-xs text-muted">{t.pre.hint}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <FileButton accept=".xlsx,.xlsm" onFiles={pre.importar} disabled={busy}>📊 {t.pre.import}</FileButton>
          <button type="button" className="btn-secondary" disabled={busy} onClick={pre.agregar}>＋ {t.pre.add}</button>
          {pre.lines.length > 0 && (
            <button type="button" className="btn-secondary" disabled={busy} onClick={pre.vaciar}>{t.pre.clear}</button>
          )}
          <button type="button" className="btn-primary" disabled={busy || !pre.lines.length} onClick={pre.calcular}>
            {t.pre.calculate}
          </button>
        </div>
      </div>

      {pre.file && <p className="text-xs text-muted break-words">{t.files}: {pre.file}</p>}
      {pre.warnings.length > 0 && (
        <ul className="text-xs text-amber-700 dark:text-amber-300 list-disc pl-5 space-y-0.5">
          {pre.warnings.map((w) => <li key={w}>{w}</li>)}
        </ul>
      )}

      <PreRouteTable lines={pre.lines} onEdit={pre.editar} onRemove={pre.quitar} t={t} />

      {pre.lines.length > 0 && (
        <p className="text-xs font-bold text-ink-2">
          {fmt(t.pre.totals, {
            l: pre.lines.length, p: tot.pos.size, u: cifra(tot.units), c: cifra(tot.cases),
            w: cifra(tot.weight), f: cifra(tot.cube),
          })}
        </p>
      )}
    </section>
  );
}
