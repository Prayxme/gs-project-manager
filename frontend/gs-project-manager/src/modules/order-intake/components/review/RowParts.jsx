// Piezas de una fila de revisión, compartidas por la tabla (escritorio) y las tarjetas (celular).

export function SelectCheckbox({ row, review }) {
  return (
    <input
      type="checkbox"
      className="w-5 h-5 md:w-4 md:h-4 accent-[var(--brand)]"
      disabled={row.status === "REGISTERED"}
      checked={review.selected.has(row.piktik)}
      onChange={() => review.alternar(row.piktik)}
      aria-label={`PikTik ${row.piktik}`}
    />
  );
}

export function EditableField({ row, field, review, className = "" }) {
  return (
    <input
      type={field.type || "text"}
      inputMode={field.type === "number" ? "numeric" : undefined}
      value={field.key === "containers" ? row.containers.join(" ") : row[field.key]}
      onChange={(ev) => review.editar(row.piktik, field.key, ev.target.value)}
      className={`input font-mono py-1.5 ${className}`}
    />
  );
}

// Diferencias con la hoja (revisiones) y avisos de la orden.
export function RowNotes({ row }) {
  return (
    <>
      {row.diffs.map((d) => (
        <p key={d.col} className="font-bold text-amber-700 dark:text-amber-300">
          {d.campo}: {d.antes || "—"} → {d.ahora}
        </p>
      ))}
      {row.warnings.map((w, i) => <p key={i} className="text-muted">⚠ {w}</p>)}
    </>
  );
}
