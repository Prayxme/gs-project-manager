export default function LayoutSelector({ gruposPallets, grupoSeleccionadoIdx, setGrupoSeleccionadoIdx, t }) {
  if (!gruposPallets || gruposPallets.length === 0) return null;

  return (
    <div className="card p-3.5 w-full bg-surface/95 backdrop-blur-md">
      <div className="flex justify-between items-center mb-2">
        <span className="text-[11px] uppercase tracking-wider font-extrabold text-muted">{t.detectedLayouts}</span>
        <span className="text-[11px] font-mono font-bold bg-brand-soft text-brand-ink px-2 py-0.5 rounded-full">
          {gruposPallets.length}
        </span>
      </div>

      <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-4 gap-1.5 max-h-36 overflow-y-auto pr-1">
        {gruposPallets.map((grupo, idx) => (
          <button
            key={idx}
            onClick={() => setGrupoSeleccionadoIdx(idx)}
            title={grupo.po ? `PO ${grupo.po}${grupo.dc ? ` · DC ${grupo.dc}` : ""}` : undefined}
            className={`px-1.5 py-1.5 rounded-xl text-[11px] font-extrabold transition flex flex-col items-center justify-center border ${
              grupoSeleccionadoIdx === idx
                ? "bg-brand text-on-brand border-transparent shadow-md"
                : "bg-surface-2 border-line text-ink-2 hover:bg-surface-3"
            }`}
          >
            <span>
              {t.layoutLabel} {String.fromCharCode(65 + idx)}
            </span>
            <span className="text-[10px] opacity-80 font-mono">x{grupo.cantidad}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
