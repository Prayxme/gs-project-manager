import { useMemo, useState } from "react";

// Tabla genérica con orden por columna. columns: [{ key, label, render?, sortValue?, className? }]
export default function DataTable({ columns, rows, rowKey, rowClassName, theme, isDarkMode, initialSort }) {
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

  const head = isDarkMode ? "bg-[#171A29] text-slate-300" : "bg-slate-100 text-slate-600";
  const borde = isDarkMode ? "border-[#1E2235]" : "border-slate-200";

  return (
    <div className={`overflow-auto rounded-xl border ${borde}`}>
      <table className="w-full text-sm">
        <thead className={`sticky top-0 z-10 ${head}`}>
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                onClick={() => alternar(c.key)}
                className="px-2.5 py-2 text-left text-xs font-extrabold uppercase tracking-wide whitespace-nowrap cursor-pointer select-none"
              >
                {c.label}
                {sort?.key === c.key && <span className="ml-1">{sort.dir === 1 ? "▲" : "▼"}</span>}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ordenadas.map((r) => (
            <tr key={rowKey(r)} className={`border-t ${borde} ${rowClassName ? rowClassName(r) : ""}`}>
              {columns.map((c) => (
                <td key={c.key} className={`px-2.5 py-1.5 align-top ${c.className || "whitespace-nowrap"} ${theme.textTitle}`}>
                  {c.render ? c.render(r) : r[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
