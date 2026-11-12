import { useNavigate } from "react-router-dom";
import { margenPorPo } from "../../utils/margin";

// Encabezado de una carga enviada por otro módulo (un RTS de Routing): pallets armados, margen
// y total a enrutar por PO, con el botón para regresar al módulo de origen.
export default function PreviewCard({ vista, gruposPallets, t }) {
  const navigate = useNavigate();
  const filas = margenPorPo(gruposPallets, vista.pos);
  const total = (campo) => filas.reduce((s, f) => s + f[campo], 0);
  const calculado = gruposPallets.length > 0;

  return (
    <div className="card p-3.5 w-full bg-surface/95 backdrop-blur-md space-y-2.5">
      <button
        type="button"
        className="btn-primary w-full text-xs py-2"
        onClick={() => navigate(vista.returnTo, { state: { restore: true } })}
      >
        ← {vista.returnLabel}
      </button>
      <div>
        <h3 className="text-sm font-black text-ink">{vista.title}</h3>
        {vista.subtitle && <p className="text-[11px] text-muted leading-snug">{vista.subtitle}</p>}
      </div>

      {calculado && (
        <>
          <table className="w-full text-xs">
            <thead>
              <tr className="text-[10px] uppercase tracking-wide text-muted">
                <th className="text-left font-extrabold pb-1">PO</th>
                <th className="text-right font-extrabold pb-1">{t.previewBuilt}</th>
                <th className="text-right font-extrabold pb-1">{t.previewMargin}</th>
                <th className="text-right font-extrabold pb-1">{t.previewRoute}</th>
              </tr>
            </thead>
            <tbody>
              {filas.map((f) => (
                <tr key={f.po} className="border-t border-line">
                  <td className="py-1 font-mono font-bold text-ink">{f.po}</td>
                  <td className="py-1 text-right font-mono text-ink-2">{f.built}</td>
                  <td className="py-1 text-right font-mono text-amber-700 dark:text-amber-300">+{f.margin}</td>
                  <td className="py-1 text-right font-mono font-extrabold text-brand-ink">{f.pallets}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="border-t-2 border-line-strong font-extrabold">
                <td className="pt-1 uppercase text-[10px] text-muted">{t.previewTotal}</td>
                <td className="pt-1 text-right font-mono text-ink">{total("built")}</td>
                <td className="pt-1 text-right font-mono text-amber-700 dark:text-amber-300">+{total("margin")}</td>
                <td className="pt-1 text-right font-mono text-brand-ink">{total("pallets")}</td>
              </tr>
            </tfoot>
          </table>
          <p className="text-[11px] font-bold text-ink-2">
            {vista.totals.weight.toLocaleString()} {t.lbs} · {vista.totals.cft.toLocaleString()} CFT
          </p>
          <p className="text-[11px] text-muted leading-snug">{t.previewHint}</p>
        </>
      )}
    </div>
  );
}
