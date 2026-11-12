import { CopyValue } from "../../../shared/components";
import { usDate } from "../utils/format";
import DeadlineBadge from "./DeadlineBadge";

// Órdenes urgentes del portal de las que no se tiene el Pick Ticket: hay que subir su PDF.
export default function MissingList({ orders, t }) {
  if (!orders.length) return null;
  return (
    <section className="card p-3 sm:p-4 space-y-2 border-amber-500/40">
      <div>
        <h3 className="text-base font-black text-ink">⚠ {t.missingTitle} ({orders.length})</h3>
        <p className="text-xs text-muted">{t.missingHint}</p>
      </div>
      <ul className="divide-y divide-line text-sm">
        {orders.map((o) => (
          <li key={o.pick_ticket} className="py-1.5 flex flex-wrap items-center gap-x-4 gap-y-1">
            <CopyValue value={o.po} />
            <span className="text-xs text-muted font-bold">{o.cust} · PT {o.pick_ticket}</span>
            <span className="text-xs text-muted">{o.ctns} {t.cols.cartons.toLowerCase()}</span>
            <span className="text-xs">
              <span className="text-muted font-bold">{t.cancel}</span>{" "}
              <span className="font-extrabold text-ink">{usDate(o.cancel_date)}</span>
            </span>
            <DeadlineBadge deadline={o.deadline} daysLeft={o.days_left} t={t} />
          </li>
        ))}
      </ul>
    </section>
  );
}
