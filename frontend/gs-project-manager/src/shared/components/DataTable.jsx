import { useMemo, useState } from "react";

/**
 * Tabla con orden por columna. En pantallas pequeñas cada fila se muestra como tarjeta.
 * columns: [{ key, label, render?, sortValue?, className?, mobile?: "title" | "hidden" }]
 *   mobile="title"  -> la columna encabeza la tarjeta en celular
 *   mobile="hidden" -> no se muestra en celular
 */
export default function DataTable({ columns, rows, rowKey, rowClassName, initialSort, emptyText }) {
  const [sort, setSort] = useState(initialSort || null); // { key, dir: 1 | -1 }

  const ordenadas = useMemo(() => {
    if (!sort) return rows;
    const col = columns.find((c) => c.key === sort.key);
    const valor = col?.sortValue || ((r) => r[sort.key]);
    return [...rows].sort((a, b) => {
      const va = valor(a);
      const vb = valor(b);
      if (va === vb) return 0;
      if (va === null || va === undefined || va === "") return 1;
      if (vb === null || vb === undefined || vb === "") return -1;
      return (va > vb ? 1 : -1) * sort.dir;
    });
  }, [rows, sort, columns]);

  const alternar = (key) =>
    setSort((s) => (s && s.key === key ? (s.dir === 1 ? { key, dir: -1 } : null) : { key, dir: 1 }));

  const celda = (c, r) => (c.render ? c.render(r) : r[c.key]);
  const titulos = columns.filter((c) => c.mobile === "title");
  const cuerpo = columns.filter((c) => c.mobile !== "title" && c.mobile !== "hidden");

  if (!rows.length) {
    return <p className="text-sm py-10 text-center text-muted">{emptyText || "—"}</p>;
  }

  return (
    <>
      {/* Escritorio / tablet */}
      <div className="hidden md:block overflow-auto rounded-xl border border-line bg-surface shadow-card max-h-[70vh]">
        <table className="w-full text-sm">
          <thead className="sticky top-0 z-10 bg-surface-2 text-muted">
            <tr>
              {columns.map((c) => (
                <th
                  key={c.key}
                  onClick={() => alternar(c.key)}
                  className="px-3 py-2.5 text-left text-xs font-extrabold uppercase tracking-wide whitespace-nowrap cursor-pointer select-none border-b border-line hover:text-ink"
                >
                  {c.label}
                  {sort?.key === c.key && <span className="ml-1 text-brand">{sort.dir === 1 ? "▲" : "▼"}</span>}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ordenadas.map((r) => (
              <tr
                key={rowKey(r)}
                className={`border-t border-line transition hover:bg-surface-3/60 ${rowClassName ? rowClassName(r) : ""}`}
              >
                {columns.map((c) => (
                  <td key={c.key} className={`px-3 py-2 align-top text-ink ${c.className || "whitespace-nowrap"}`}>
                    {celda(c, r)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Celular: tarjetas */}
      <div className="md:hidden space-y-2.5">
        {ordenadas.map((r) => (
          <div key={rowKey(r)} className={`card p-3.5 ${rowClassName ? rowClassName(r) : ""}`}>
            {titulos.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 mb-2 pb-2 border-b border-line">
                {titulos.map((c) => (
                  <span key={c.key} className="text-ink">{celda(c, r)}</span>
                ))}
              </div>
            )}
            <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
              {cuerpo.map((c) => {
                const v = celda(c, r);
                if (v === "" || v === null || v === undefined) return null;
                return (
                  <div key={c.key} className="contents">
                    <dt className="text-xs font-bold uppercase tracking-wide text-muted pt-0.5">{c.label}</dt>
                    <dd className="text-ink break-words min-w-0">{v}</dd>
                  </div>
                );
              })}
            </dl>
          </div>
        ))}
      </div>
    </>
  );
}
