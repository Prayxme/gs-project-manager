const ITEM_FIELDS = [
  { key: "qty", title: "quantity", bold: true },
  { key: "l", title: "length" },
  { key: "w", title: "width" },
  { key: "h", title: "height" },
  { key: "weight", title: "weight" },
];

export default function PdfReviewModal({ show, data, setData, onClose, onConfirm, t }) {
  if (!show || !data) return null;

  const orders = data.orders || [];
  const totalItems = orders.reduce((acc, o) => acc + o.items.length, 0);
  const totalBoxes = orders.reduce((acc, o) => acc + o.items.reduce((a, i) => a + Number(i.qty || 0), 0), 0);

  // Actualizaciones inmutables del estado anidado orders -> items
  const updateOrder = (oi, field, value) =>
    setData({ ...data, orders: orders.map((o, i) => (i === oi ? { ...o, [field]: value } : o)) });

  const updateItem = (oi, ii, field, value) =>
    setData({
      ...data,
      orders: orders.map((o, i) =>
        i === oi ? { ...o, items: o.items.map((it, j) => (j === ii ? { ...it, [field]: value } : it)) } : o
      ),
    });

  return (
    <div className="fixed inset-0 z-50 flex items-stretch sm:items-center justify-center bg-[#06141B]/70 backdrop-blur-sm sm:p-4">
      <div className="bg-surface w-full sm:max-w-3xl sm:max-h-[90vh] sm:rounded-2xl shadow-2xl flex flex-col border border-line overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-line">
          <h2 className="text-lg sm:text-xl font-extrabold tracking-tight text-ink">{t.modalTitle}</h2>
          <p className="text-xs text-muted mt-0.5">{t.modalSubtitle}</p>
          <p className="text-xs font-mono font-bold text-brand mt-2">
            {orders.length} PikTik · {totalItems} SKU · {totalBoxes.toLocaleString()} {t.modalBoxes}
          </p>
        </div>

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <label>
              <span className="label">{t.modalCompany}</span>
              <input type="text" value={data.company} onChange={(e) => setData({ ...data, company: e.target.value })} className="input" />
            </label>
            <label>
              <span className="label">{t.modalCustNo}</span>
              <input type="text" value={data.cust_no} onChange={(e) => setData({ ...data, cust_no: e.target.value })} className="input" />
            </label>
          </div>

          {data.warnings && data.warnings.length > 0 && (
            <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-xs text-amber-800 dark:text-amber-300 space-y-0.5">
              <p className="font-extrabold uppercase tracking-wider">{t.modalWarnings}</p>
              {data.warnings.map((w, i) => <p key={i}>• {w}</p>)}
            </div>
          )}

          <div className="space-y-3">
            {orders.map((order, oi) => (
              <div key={order.piktik} className="rounded-xl border border-line bg-surface-2 p-3 space-y-2.5">
                <div className="flex flex-wrap items-center gap-x-3 gap-y-2 text-xs font-mono">
                  <span className="font-extrabold text-brand">PikTik {order.piktik}</span>
                  <label className="flex items-center gap-1 text-muted">
                    PO
                    <input type="text" value={order.po} onChange={(e) => updateOrder(oi, "po", e.target.value)} className="input w-28 py-1 font-bold" />
                  </label>
                  <label className="flex items-center gap-1 text-muted">
                    {t.destinationDc}
                    <input type="text" value={order.ship_to_dc} onChange={(e) => updateOrder(oi, "ship_to_dc", e.target.value)} className="input w-16 py-1 font-bold" />
                  </label>
                  <span className="text-muted">{order.destination}</span>
                  {order.pages > 1 && <span className="text-muted">· {order.pages} {t.modalPages}</span>}
                </div>

                {order.items.map((item, ii) => (
                  <div key={ii} className="grid grid-cols-5 sm:flex gap-1.5 sm:gap-2 items-center">
                    <input
                      type="text"
                      value={item.sku}
                      onChange={(e) => updateItem(oi, ii, "sku", e.target.value)}
                      className="input col-span-5 sm:flex-1 sm:min-w-0 font-mono font-bold py-1.5"
                      title={item.variant ? `${t.skuName}: ${item.variant}` : t.skuName}
                    />
                    {ITEM_FIELDS.map((f) => (
                      <input
                        key={f.key}
                        type="number"
                        inputMode="decimal"
                        value={item[f.key]}
                        onChange={(e) => updateItem(oi, ii, f.key, e.target.value)}
                        className={`input sm:w-16 text-center font-mono px-1 py-1.5 ${f.bold ? "font-bold" : ""}`}
                        title={t[f.title]}
                        aria-label={t[f.title]}
                      />
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className="p-3 sm:p-4 border-t border-line bg-surface-2 flex justify-end gap-2.5">
          <button onClick={onClose} className="btn-secondary flex-1 sm:flex-none">{t.modalCancel}</button>
          <button onClick={onConfirm} className="btn-primary flex-1 sm:flex-none">{t.modalImport}</button>
        </div>
      </div>
    </div>
  );
}
