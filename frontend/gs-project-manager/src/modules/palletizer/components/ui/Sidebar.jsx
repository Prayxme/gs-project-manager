import { SKU_PALETTE } from '../../constants/palette';
import { colorKey } from '../../utils/palletUtils';

const DIMENSIONES = [
  ["length", "length"],
  ["width", "width"],
  ["height", "height"],
  ["weight", "weight"],
];

export default function Sidebar({
  orderInfo,
  setOrderInfo,
  itemsForm,
  actualizarItem,
  eliminarItem,
  agregarItem,
  skuColorMap,
  calcularArmado,
  loading,
  pdfLoading,
  triggerPdfUpload,
  t,
  className = "",
}) {
  return (
    <aside className={`w-full md:w-[400px] lg:w-[420px] md:border-r border-line bg-surface flex-col shrink-0 min-h-0 ${className}`}>
      {/* Encabezado */}
      <div className="px-4 py-3 border-b border-line flex justify-between items-center gap-2">
        <h2 className="text-sm font-extrabold tracking-wide uppercase text-ink">{t.cargoSpecsTitle}</h2>
        <button onClick={triggerPdfUpload} disabled={pdfLoading} className="btn-primary text-xs px-3 py-1.5">
          {pdfLoading ? t.scanningPdf : t.importPdfBtn}
        </button>
      </div>

      {/* Formularios */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <section className="space-y-2">
          <h3 className="text-xs font-extrabold uppercase tracking-widest text-brand">{t.orderInfoTitle}</h3>
          <div className="grid grid-cols-2 gap-2">
            {[["po", t.poNumber], ["piktik", t.pikTik]].map(([campo, etiqueta]) => (
              <label key={campo}>
                <span className="label">{etiqueta}</span>
                <input
                  type="text"
                  value={orderInfo[campo]}
                  onChange={(e) => setOrderInfo({ ...orderInfo, [campo]: e.target.value })}
                  className="input font-mono py-1.5"
                />
              </label>
            ))}
          </div>
        </section>

        {itemsForm.map((item, idx) => {
          const skuColor = skuColorMap[colorKey(item.po, item.sku?.trim() || `ITEM-${idx + 1}`)] || SKU_PALETTE[0];
          return (
            <section key={idx} className="relative rounded-xl border border-line bg-surface-2 p-3.5 space-y-2.5">
              <div className="flex items-center gap-2 pr-6">
                <span className="w-3 h-3 rounded-full shrink-0 ring-2 ring-surface" style={{ backgroundColor: skuColor }} />
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-brand">
                  {t.skuTitle} #{idx + 1}
                </h3>
                {item.po && (
                  <span className="ml-auto text-xs font-mono font-bold px-2 py-0.5 rounded-md bg-brand-soft text-brand-ink truncate">
                    PO {item.po}{item.dc ? ` · DC ${item.dc}` : ""}
                  </span>
                )}
              </div>
              {itemsForm.length > 1 && (
                <button
                  onClick={() => eliminarItem(idx)}
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
                    onChange={(e) => actualizarItem(idx, "sku", e.target.value)}
                    className="input font-mono font-bold py-1.5"
                  />
                </label>
                <label>
                  <span className="label">{t.quantity}</span>
                  <input
                    type="number"
                    inputMode="numeric"
                    value={item.qty}
                    onChange={(e) => actualizarItem(idx, "qty", e.target.value)}
                    className="input font-mono font-bold text-center py-1.5"
                  />
                </label>
              </div>
              <div className="grid grid-cols-4 gap-1.5">
                {DIMENSIONES.map(([campo, etiqueta]) => (
                  <label key={campo}>
                    <span className="label normal-case">{t[etiqueta]}</span>
                    <input
                      type="number"
                      inputMode="decimal"
                      value={item[campo]}
                      onChange={(e) => actualizarItem(idx, campo, e.target.value)}
                      className="input font-mono text-center px-1 py-1.5"
                    />
                  </label>
                ))}
              </div>
            </section>
          );
        })}

        <button
          onClick={agregarItem}
          className="w-full py-2.5 border border-dashed border-line-strong rounded-xl text-xs font-extrabold uppercase tracking-wider text-muted hover:text-brand hover:border-brand transition"
        >
          {t.addSkuBtn}
        </button>
      </div>

      {/* Acción principal */}
      <div className="p-4 border-t border-line bg-surface-2">
        <button onClick={calcularArmado} disabled={loading} className="btn-primary w-full py-3 uppercase tracking-wider">
          {loading ? t.processingBtn : t.generateLayoutBtn}
        </button>
      </div>
    </aside>
  );
}
