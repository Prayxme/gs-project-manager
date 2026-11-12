import { Badge, CopyValue } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";
import { addressLine, usDate } from "../utils/format";
import DeadlineBadge from "./DeadlineBadge";
import PoRow from "./PoRow";
import ViewPalletsButton from "./ViewPalletsButton";

const COLUMNAS = ["po", "piktik", "cust", "units", "cartons", "weight", "cft", "pallets"];
const NUMERICAS = new Set(["units", "cartons", "weight", "cft", "pallets"]);

// Un RTS propuesto: destino, fechas, ocupación y sus POs con los valores a declarar.
export default function RtsCard({ rts, t }) {
  const lleno = Math.min(100, Math.round((100 * rts.pallets) / rts.limit));
  return (
    <section className="card p-3 sm:p-4 space-y-3">
      <header className="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <h3 className="text-base font-black text-ink">
            {fmt(t.rts, { n: rts.number })}
            <span className="text-muted font-bold"> · {rts.family}{rts.po_prefix ? ` · PO ${rts.po_prefix}…` : ""}</span>
          </h3>
          <p className="text-sm font-bold text-ink-2">{rts.ship_to?.name}</p>
          <p className="text-xs text-muted">{addressLine(rts.ship_to)}</p>
        </div>
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5">
          <span className="text-xs">
            <span className="text-muted font-bold">{t.cancel}</span>{" "}
            <span className="font-extrabold text-ink">{usDate(rts.cancel_date)}</span>
          </span>
          <DeadlineBadge deadline={rts.deadline} daysLeft={rts.days_left} t={t} />
          {!rts.verified && <Badge className="bg-amber-400 text-slate-900">{t.unverified}</Badge>}
          <ViewPalletsButton rts={rts} t={t} />
        </div>
      </header>

      <div>
        <div className="flex justify-between text-xs font-bold text-muted mb-1">
          <span>{fmt(t.limit, { p: rts.pallets, l: rts.limit })}</span>
          <span>{lleno}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-surface-3 overflow-hidden">
          <div className={`h-full ${rts.over_limit ? "bg-red-600" : "bg-brand"}`} style={{ width: `${lleno}%` }} />
        </div>
        {rts.over_limit && <p className="text-xs font-bold text-red-600 mt-1">{fmt(t.overLimit, { l: rts.limit })}</p>}
      </div>

      <div className="overflow-x-auto -mx-3 sm:mx-0 px-3 sm:px-0">
        <table className="w-full text-sm min-w-[640px]">
          <thead>
            <tr className="text-[11px] uppercase tracking-wide text-muted">
              {COLUMNAS.map((c) => (
                <th key={c} className={`pb-1.5 pr-2 font-extrabold ${NUMERICAS.has(c) ? "text-right" : "text-left"}`}>
                  {t.cols[c]}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rts.pos.map((po) => <PoRow key={po.po} po={po} t={t} />)}
          </tbody>
          <tfoot>
            <tr className="border-t-2 border-line-strong">
              <td colSpan={3} className="pt-1.5 text-xs font-extrabold uppercase text-muted">{t.totals}</td>
              <td className="pt-1.5 pr-2 text-right"><CopyValue value={rts.units} /></td>
              <td className="pt-1.5 pr-2 text-right"><CopyValue value={rts.cartons} /></td>
              <td className="pt-1.5 pr-2 text-right"><CopyValue value={rts.weight} /></td>
              <td className="pt-1.5 pr-2 text-right"><CopyValue value={rts.cft} /></td>
              <td className="pt-1.5 text-right"><CopyValue value={rts.pallets} className="text-brand-ink" /></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </section>
  );
}
