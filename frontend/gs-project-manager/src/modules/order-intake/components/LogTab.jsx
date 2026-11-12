import { DataTable } from "../../../shared/components";
import { formatDateTime } from "../../../shared/utils/dates";
import StatusBadge from "./StatusBadge";

const columnas = (t) => [
  { key: "action", label: t.cols.action, mobile: "title", render: (l) => <StatusBadge status={l.action} t={t} /> },
  { key: "piktik", label: t.cols.piktik, mobile: "title", render: (l) => <span className="font-mono font-bold">PT {l.piktik}</span> },
  { key: "ts", label: t.cols.when, render: (l) => formatDateTime(l.ts) },
  { key: "po", label: t.cols.po },
  { key: "store", label: t.cols.store },
  { key: "sheet_row", label: t.cols.row },
  { key: "source_ref", label: t.cols.source, className: "min-w-[12rem]" },
];

// Pestaña "Historial": lo escrito en la hoja desde la app.
export default function LogTab({ log, t }) {
  if (log === null) return <p className="text-sm py-10 text-center text-muted">{t.reading}</p>;
  return <DataTable columns={columnas(t)} rows={log} rowKey={(l) => l.id} emptyText={t.noLog} />;
}
