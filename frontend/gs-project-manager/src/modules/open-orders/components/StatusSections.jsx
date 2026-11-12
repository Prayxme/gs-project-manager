import { useMemo } from "react";
import { Badge } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";
import { STATUS_STYLE } from "../constants";
import { seccionesPorEstado } from "../utils/grouping";
import CustomerGroup from "./CustomerGroup";
import RouteLink from "./RouteLink";

const ABIERTAS = new Set(["OVERDUE", "LAST DAY", "ATTENTION"]);   // lo urgente se muestra desplegado

// Órdenes activas por secciones: una por estado (vencidas, último día, atención, a tiempo...) y,
// dentro, un grupo por Customer No. Cada sección y cada grupo abre Routing con esas órdenes.
export default function StatusSections({ orders, t }) {
  const secciones = useMemo(() => seccionesPorEstado(orders), [orders]);
  if (!secciones.length) return <p className="text-sm py-10 text-center text-muted">{t.noData}</p>;

  return (
    <div className="space-y-6">
      {secciones.map(({ status, orders: delEstado, groups }) => (
        <section key={status} className="space-y-2">
          <header className="flex flex-wrap items-center gap-x-3 gap-y-1.5 border-b border-line pb-2">
            <Badge className={STATUS_STYLE[status].badge}>{status}</Badge>
            <h3 className="text-base font-black text-ink">{t.kpis[status]}</h3>
            <span className="text-xs font-bold text-muted">
              {fmt(t.sectionCount, { n: delEstado.length, g: groups.length })} · {t.sectionHint[status]}
            </span>
            {status !== "ROUTED" && (
              <RouteLink statuses={[status]} className="btn-secondary text-xs px-3 py-1.5 sm:ml-auto">
                🚚 {t.routeSection}
              </RouteLink>
            )}
          </header>
          {groups.map((g) => (
            <CustomerGroup key={g.cust} status={status} group={g} open={ABIERTAS.has(status)} t={t} />
          ))}
        </section>
      ))}
    </div>
  );
}
