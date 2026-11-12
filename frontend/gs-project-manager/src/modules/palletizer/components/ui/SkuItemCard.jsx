const DIMENSIONES = ["length", "width", "height", "weight"];

// Una línea de carga (SKU): nombre, cantidad, medidas y peso. El punto de color es el del visor 3D.
export default function SkuItemCard({ item, idx, color, canRemove, onChange, onRemove, t }) {
  return (
    <section className="relative rounded-xl border border-line bg-surface-2 p-3.5 space-y-2.5">
      <div className="flex items-center gap-2 pr-6">
        <span className="w-3 h-3 rounded-full shrink-0 ring-2 ring-surface" style={{ backgroundColor: color }} />
        <h3 className="text-xs font-extrabold uppercase tracking-wider text-brand">
          {t.skuTitle} #{idx + 1}
        </h3>
        {item.po && (
          <span className="ml-auto text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-brand-soft text-brand-ink truncate">
            PO {item.po}{item.dc ? ` · DC ${item.dc}` : ""}
          </span>
        )}
      </div>
      {canRemove && (
        <button
          onClick={() => onRemove(idx)}
          aria-label="Eliminar"
          className="absolute top-2.5 right-2.5 w-6 h-6 grid place-items-center rounded-md text-muted hover:text-red-600 hover:bg-red-500/10"
        >
          ✕
        </button>
      )}
      <div className="grid grid-cols-3 gap-2">
        <label className="col-span-2">
          <span className="label">{t.skuName}</span>
          <input
            type="text"
            value={item.sku}
            onChange={(e) => onChange(idx, "sku", e.target.value)}
            className="input font-mono font-bold py-1.5"
          />
        </label>
        <label>
          <span className="label">{t.quantity}</span>
          <input
            type="number"
            inputMode="numeric"
            value={item.qty}
            onChange={(e) => onChange(idx, "qty", e.target.value)}
            className="input font-mono font-bold text-center py-1.5"
          />
        </label>
      </div>
      <div className="grid grid-cols-4 gap-1.5">
        {DIMENSIONES.map((campo) => (
          <label key={campo}>
            <span className="label normal-case">{t[campo]}</span>
            <input
              type="number"
              inputMode="decimal"
              value={item[campo]}
              onChange={(e) => onChange(idx, campo, e.target.value)}
              className="input font-mono text-center px-1 py-1.5"
            />
          </label>
        ))}
      </div>
    </section>
  );
}
