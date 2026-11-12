import { Badge } from "../../../shared/components";
import { formatShortDateTime } from "../../../shared/utils/dates";
import { STATUS_STYLE } from "../constants";
import { isoAMdy, limpiarFecha, mdyOrdenable } from "../utils/dates";

// Columnas de la pestaña "Órdenes activas".
export const activeColumns = (t) => [
  {
    key: "priority_rank", label: t.cols.status, mobile: "title",
    render: (o) => <Badge className={STATUS_STYLE[o.status]?.badge || ""}>{o.status || "—"}</Badge>,
  },
  {
    key: "days_remaining", label: t.cols.days, mobile: "title",
    render: (o) =>
      o.status === "ROUTED" ? <span className="text-brand font-bold">✔</span>
      : <span className="font-mono font-bold">{o.days_remaining} d</span>,
  },
  {
    key: "pick_ticket", label: t.cols.pickTicket, mobile: "title",
    render: (o) => <span className="font-mono font-bold">PT {o.pick_ticket}</span>,
  },
  {
    key: "routing_deadline", label: t.cols.deadline,
    render: (o) => (
      <span title={o.routing_earliest ? `${t.window}: ${isoAMdy(o.routing_earliest)}` : undefined}>
        {isoAMdy(o.routing_deadline)}
      </span>
    ),
  },
  { key: "po", label: t.cols.po, render: (o) => <span className="font-mono font-bold">{o.po}</span> },
  { key: "cust", label: t.cols.customer },
  { key: "ship_date", label: t.cols.shipDate, sortValue: (o) => mdyOrdenable(o.ship_date) },
  { key: "cancel_date", label: t.cols.cancelDate, sortValue: (o) => mdyOrdenable(o.cancel_date) },
  {
    key: "cfrm_number", label: t.cols.cfrm,
    render: (o) =>
      o.cfrm_number ? (
        <span>
          <span className="font-mono">{o.cfrm_number}</span>
          <span className="ml-1.5 text-[11px] text-muted">({t.cfrmType[o.cfrm_type] || ""})</span>
        </span>
      ) : "",
  },
  {
    key: "appt_date", label: t.cols.appt, sortValue: (o) => mdyOrdenable(o.appt_date),
    render: (o) => `${limpiarFecha(o.appt_date)} ${o.appt_time || ""}`.trim(),
  },
  { key: "ctns", label: t.cols.ctns, sortValue: (o) => Number(o.ctns) || 0 },
  { key: "notes", label: t.cols.notes, className: "min-w-[12rem]" },
  {
    key: "last_change_at", label: t.cols.lastChange,
    render: (o) =>
      o.last_change ? (
        <span>
          <span className="font-bold">{o.last_change}</span>
          <span className="block text-[11px] text-muted">{formatShortDateTime(o.last_change_at)}</span>
        </span>
      ) : "",
  },
];
