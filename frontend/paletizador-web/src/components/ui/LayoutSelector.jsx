export default function LayoutSelector({
  gruposPallets,
  grupoSeleccionadoIdx,
  setGrupoSeleccionadoIdx,
  isDarkMode,
  t,
  theme,
}) {
  if (!gruposPallets || gruposPallets.length === 0) return null;

  return (
    <div className={`p-3.5 rounded-2xl border backdrop-blur-md w-full shadow-lg ${theme.hudCard}`}>
      <div className="flex justify-between items-center mb-2">
        <span className="text-[10px] uppercase tracking-wider font-extrabold text-slate-400">
          {t.detectedLayouts}
        </span>
        <span className="text-[10px] font-mono font-bold bg-[#0284C7]/10 text-[#0284C7] px-2 py-0.5 rounded-full">
          {gruposPallets.length}
        </span>
      </div>

      <div className="grid grid-cols-4 gap-1.5 max-h-36 overflow-y-auto pr-1">
        {gruposPallets.map((grupo, idx) => (
          <button
            key={idx}
            onClick={() => setGrupoSeleccionadoIdx(idx)}
            title={grupo.po ? `PO ${grupo.po}${grupo.dc ? ` · DC ${grupo.dc}` : ""}` : undefined}
            className={`px-1.5 py-1.5 rounded-xl text-[11px] font-extrabold transition-all flex flex-col items-center justify-center border ${
              grupoSeleccionadoIdx === idx
                ? "bg-[#0284C7] text-white shadow-md border-transparent"
                : isDarkMode
                ? "bg-black/30 border-slate-800 text-slate-400 hover:text-white hover:bg-black/50"
                : "bg-slate-100 border-slate-200 text-slate-700 hover:bg-slate-200"
            }`}
          >
            <span>
              {t.layoutLabel} {String.fromCharCode(65 + idx)}
            </span>
            <span className="text-[9px] opacity-80 font-mono">x{grupo.cantidad}</span>
          </button>
        ))}
      </div>
    </div>
  );
}