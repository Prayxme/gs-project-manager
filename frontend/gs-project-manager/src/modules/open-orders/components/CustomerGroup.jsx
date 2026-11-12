import { DataTable } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";
import { groupColumns } from "../columns/groupColumns";
import { isoAMdy } from "../utils/dates";
import RouteLink from "./RouteLink";

// Órdenes de un Customer No dentro de un estado, con el acceso a Routing para ese grupo.
export default function CustomerGroup({ status, group, open, t }) {
  const enrutable = status !== "ROUTED";
  return (
    <details className="card overflow-hidden" open={open}>
      <summary className="cursor-pointer select-none px-3 py-2.5 flex flex-wrap items-center gap-x-4 gap-y-1.5">
        <span className="text-sm font-black text-ink font-mono">{group.cust}</span>
        <span className="text-xs font-bold text-muted">
          {fmt(t.groupCount, { n: group.orders.length, c: group.ctns.toLocaleString() })}
        </span>
        {enrutable && group.deadline && (
          <span className="text-xs text-ink-2">
            <span className="font-bold text-muted">{t.cols.deadline}</span>{" "}
            <span className="font-extrabold">{isoAMdy(group.deadline)}</span>
            <span className="font-mono font-bold"> ({group.days} d)</span>
          </span>
        )}
        {enrutable && (
          <RouteLink statuses={[status]} cust={group.cust} className="btn-secondary text-xs px-3 py-1.5 sm:ml-auto">
            🚚 {t.routeGroup}
          </RouteLink>
        )}
      </summary>
      <div className="p-2 pt-0">
        <DataTable columns={groupColumns(t)} rows={group.orders} rowKey={(o) => o.pick_ticket} emptyText="—" />
      </div>
    </details>
  );
}
