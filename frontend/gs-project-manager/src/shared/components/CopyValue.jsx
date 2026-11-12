import { useEffect, useState } from "react";

const CONFIRMACION_MS = 1200;

// Valor que se copia al portapapeles con un clic (muestra ✓ un instante).
// `copy` permite copiar un texto distinto al mostrado (p. ej. sin formato).
export default function CopyValue({ value, copy, className = "", title = "Copiar" }) {
  const [copiado, setCopiado] = useState(false);
  useEffect(() => {
    if (!copiado) return undefined;
    const id = setTimeout(() => setCopiado(false), CONFIRMACION_MS);
    return () => clearTimeout(id);
  }, [copiado]);

  if (value === null || value === undefined || value === "") return <span className="text-muted">—</span>;

  const copiar = async () => {
    try {
      await navigator.clipboard.writeText(String(copy ?? value));
      setCopiado(true);
    } catch {
      setCopiado(false);
    }
  };

  return (
    <button
      type="button"
      onClick={copiar}
      title={title}
      className={`group inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 font-bold tabular-nums
        hover:bg-brand-soft hover:text-brand-ink focus-visible:outline-2 focus-visible:outline-brand
        ${copiado ? "bg-brand-soft text-brand-ink" : ""} ${className}`}
    >
      <span>{value}</span>
      <span aria-hidden className={`text-[10px] ${copiado ? "" : "opacity-0 group-hover:opacity-60"}`}>
        {copiado ? "✓" : "⧉"}
      </span>
    </button>
  );
}
