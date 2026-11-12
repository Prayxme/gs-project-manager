import { Badge } from "../../../shared/components";
import { CLOSED_STYLE } from "../constants";
import { limpiarFecha, mdyOrdenable } from "../utils/dates";

// Columnas de la pestaña "Cerradas".
export const closedColumns = (t) => [
  {
    key: "final_status", label: t.cols.finalStatus, mobile: "title",
    render: (c) => (
      <span title={c.original_status ? `${t.originally}: ${c.original_status} · ${c.original_reason || ""}` : undefined}>
        <Badge className={CLOSED_STYLE[c.final_status] || ""}>{c.final_status}</Badge>
        {c.original_status && <span className="ml-1 text-[11px] text-muted">*</span>}
      </span>
    ),
  },
  { key: "pick_ticket", label: t.cols.pickTicket, mobile: "title", render: (c) => <span className="font-mono font-bold">PT {c.pick_ticket}</span> },
  { key: "date_removed", label: t.cols.dateRemoved },
  { key: "reason", label: t.cols.reason },
  { key: "po", label: t.cols.po, render: (c) => <span className="font-mono font-bold">{c.po}</span> },
  { key: "cust", label: t.cols.customer },
  { key: "ship_date", label: t.cols.shipDate, sortValue: (c) => mdyOrdenable(c.ship_date) },
  { key: "cancel_date", label: t.cols.cancelDate, sortValue: (c) => mdyOrdenable(c.cancel_date) },
  { key: "cfrm_number", label: t.cols.cfrm, render: (c) => <span className="font-mono">{c.cfrm_number}</span> },
  { key: "appt_date", label: t.cols.appt, render: (c) => limpiarFecha(c.appt_date) },
  { key: "notes", label: t.cols.notes, className: "min-w-[10rem]" },
  { key: "source", label: t.cols.source, mobile: "hidden" },
];
