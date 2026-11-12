import { DataTable } from "../../../shared/components";

const columnas = (t) => [
  { key: "piktik", label: t.cols.piktik, mobile: "title", render: (s) => <span className="font-mono font-bold">PT {s.piktik}</span> },
  { key: "row", label: t.cols.row },
  { key: "containers", label: t.cols.containers, render: (s) => s.containers.join(" ") },
];

// Pestaña "Sugerencias de Received".
export default function SuggestionsTab({ suggestions, onLoad, busy, t }) {
  return (
    <div className="space-y-3">
      <p className="text-sm max-w-3xl text-muted">{t.sugIntro}</p>
      <button className="btn-secondary" disabled={!!busy} onClick={onLoad}>{busy || t.sugLoad}</button>
      {suggestions && (
        <DataTable columns={columnas(t)} rows={suggestions} rowKey={(s) => s.row} emptyText={t.sugNone} />
      )}
    </div>
  );
}
