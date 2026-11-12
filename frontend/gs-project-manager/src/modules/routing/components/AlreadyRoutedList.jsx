import { CopyValue } from "../../../shared/components";
import { usDate } from "../utils/format";

// POs que el portal de Wiesner ya muestra enrutadas: no se estiman, solo se informan.
export default function AlreadyRoutedList({ pos, t }) {
  if (!pos.length) return null;
  return (
    <section className="card p-3 sm:p-4 space-y-2">
      <div>
        <h3 className="text-base font-black text-ink">✔ {t.routedTitle} ({pos.length})</h3>
        <p className="text-xs text-muted">{t.routedHint}</p>
      </div>
      <ul className="divide-y divide-line text-sm">
        {pos.map((po) => (
          <li key={po.po} className="py-1.5 flex flex-wrap items-center gap-x-4 gap-y-1">
            <CopyValue value={po.po} />
            <span className="text-xs text-muted font-bold">{po.cust} · PT {po.piktiks.join(", ")}</span>
            <span className="text-xs">
              <span className="text-muted font-bold">{t.cfrm}</span> <CopyValue value={po.cfrm_number} />
            </span>
            {po.appt_date && (
              <span className="text-xs">
                <span className="text-muted font-bold">{t.appt}</span>{" "}
                <span className="font-extrabold text-ink">{usDate(po.appt_date)}</span>
              </span>
            )}
            <span className="text-xs text-muted">{po.cartons} {t.cols.cartons.toLowerCase()}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
