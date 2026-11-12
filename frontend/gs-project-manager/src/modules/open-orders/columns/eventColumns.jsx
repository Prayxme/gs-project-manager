import { formatShortDateTime } from "../../../shared/utils/dates";

// Columnas de la pestaña "Historial de cambios".
export const eventColumns = (t) => [
  { key: "event", label: t.cols.event, mobile: "title", render: (e) => <span className="font-bold">{e.event}</span> },
  { key: "ts", label: t.cols.when, render: (e) => formatShortDateTime(e.ts) },
  { key: "pick_ticket", label: t.cols.pickTicket, render: (e) => <span className="font-mono">{e.pick_ticket}</span> },
  { key: "po", label: t.cols.po, render: (e) => <span className="font-mono">{e.po}</span> },
  { key: "cust", label: t.cols.customer },
  { key: "old_value", label: t.cols.old },
  { key: "new_value", label: t.cols.new },
];
