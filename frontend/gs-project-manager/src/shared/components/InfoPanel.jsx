import { useState } from "react";
import { guardarPreferencia, leerPreferencia } from "../utils/storage";

/**
 * Explicación y reglas de un módulo, ordenadas por temas y plegables.
 *   sections = [{ title, items: [[etiqueta, texto], ...] }]
 * Recuerda por módulo (`id`) si el usuario lo dejó abierto o cerrado.
 */
export default function InfoPanel({ id, title, sections }) {
  const clave = `gs.info.${id}`;
  const [abierto, setAbierto] = useState(() => leerPreferencia(clave, true));

  const alternar = () => {
    guardarPreferencia(clave, !abierto);
    setAbierto(!abierto);
  };

  return (
    <section className="rounded-xl border border-line bg-surface-2/60">
      <button
        type="button"
        onClick={alternar}
        aria-expanded={abierto}
        className="w-full flex items-center justify-between gap-3 px-3 sm:px-4 py-2 text-left"
      >
        <span className="text-xs font-extrabold uppercase tracking-wide text-ink-2">ⓘ {title}</span>
        <span className="text-xs font-bold text-muted">{abierto ? "▲" : "▼"}</span>
      </button>

      {abierto && (
        <div className="grid gap-x-8 gap-y-4 px-3 sm:px-4 pb-3 pt-1 sm:grid-cols-2 xl:grid-cols-4 border-t border-line">
          {sections.map((s) => (
            <div key={s.title} className="pt-2 min-w-0">
              <h4 className="text-[11px] font-extrabold uppercase tracking-wider text-brand mb-1.5">{s.title}</h4>
              <dl className="grid grid-cols-[auto_1fr] gap-x-2.5 gap-y-1 text-xs leading-snug">
                {s.items.map(([etiqueta, texto]) => (
                  <div key={etiqueta} className="contents">
                    <dt className="font-extrabold text-ink max-w-[9.5rem]">{etiqueta}</dt>
                    <dd className="text-ink-2 min-w-0">{texto}</dd>
                  </div>
                ))}
              </dl>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
