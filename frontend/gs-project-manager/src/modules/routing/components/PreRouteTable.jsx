import { PRE_COLUMNS } from "../utils/preroute";

// Tabla editable de líneas de Pre Routing (una fila por PO / estilo / color).
export default function PreRouteTable({ lines, onEdit, onRemove, t }) {
  if (!lines.length) return <p className="text-sm text-muted py-4 text-center">{t.pre.empty}</p>;
  return (
    <div className="overflow-auto max-h-[55vh] rounded-xl border border-line">
      <table className="text-sm min-w-max w-full">
        <thead className="sticky top-0 z-10 bg-surface-2 text-muted">
          <tr>
            <th className="px-2 py-2 text-left text-[11px] font-extrabold">#</th>
            {PRE_COLUMNS.map(([campo]) => (
              <th key={campo} className="px-1.5 py-2 text-left text-[11px] font-extrabold uppercase tracking-wide whitespace-nowrap">
                {t.pre.cols[campo]}
              </th>
            ))}
            <th />
          </tr>
        </thead>
        <tbody>
          {lines.map((linea, i) => (
            <tr key={linea.id} className="border-t border-line">
              <td className="px-2 text-xs font-mono text-muted">{i + 1}</td>
              {PRE_COLUMNS.map(([campo, tipo, ancho]) => (
                <td key={campo} className="px-1 py-1">
                  <input
                    type={tipo}
                    step="any"
                    min={tipo === "number" ? 0 : undefined}
                    value={linea[campo] ?? ""}
                    onChange={(e) => onEdit(linea.id, campo, e.target.value)}
                    aria-label={`${t.pre.cols[campo]} ${i + 1}`}
                    className={`input py-1 px-2 text-sm font-mono ${ancho}`}
                  />
                </td>
              ))}
              <td className="px-1">
                <button
                  type="button"
                  onClick={() => onRemove(linea.id)}
                  title={t.pre.remove}
                  aria-label={`${t.pre.remove} ${i + 1}`}
                  className="px-2 py-1 rounded-lg text-muted hover:text-red-600 hover:bg-red-500/10 font-bold"
                >
                  ✕
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
