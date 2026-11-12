import { Badge, CopyValue } from "../../../shared/components";
import { STATUS_STYLE } from "../constants";

// POs que no entran en ningún RTS (no coinciden con el portal, ya enrutadas, PDF sin líneas...).
export default function ExcludedList({ pos, t }) {
  if (!pos.length) return null;
  return (
    <section className="card p-3 sm:p-4 space-y-2 border-red-500/30">
      <div>
        <h3 className="text-base font-black text-ink">{t.excludedTitle} ({pos.length})</h3>
        <p className="text-xs text-muted">{t.excludedHint}</p>
      </div>
      <ul className="divide-y divide-line">
        {pos.map((po) => (
          <li key={po.po} className="py-2 flex flex-col sm:flex-row sm:items-start gap-1.5 sm:gap-3">
            <div className="flex items-center gap-2 shrink-0">
              <CopyValue value={po.po} />
              <span className="text-xs text-muted font-bold">{po.cust} · PT {po.piktiks.join(", ")}</span>
            </div>
            <Badge className={STATUS_STYLE[po.status] || ""}>{t.status[po.status] || po.status}</Badge>
            <span className="text-xs text-ink-2 min-w-0 break-words">{po.issues.join(" · ")}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
