const ITEM_FIELDS = [
  { key: "qty", title: "quantity", width: "w-16", bold: true },
  { key: "l", title: "length", width: "w-14" },
  { key: "w", title: "width", width: "w-14" },
  { key: "h", title: "height", width: "w-14" },
  { key: "weight", title: "weight", width: "w-16" },
];

export default function PdfReviewModal({
  show,
  data,
  setData,
  onClose,
  onConfirm,
  isDarkMode,
  t,
  theme,
}) {
  if (!show || !data) return null;

  const orders = data.orders || [];
  const totalItems = orders.reduce((acc, o) => acc + o.items.length, 0);
  const totalBoxes = orders.reduce(
    (acc, o) => acc + o.items.reduce((a, i) => a + Number(i.qty || 0), 0),
    0
  );

  // Actualizaciones inmutables del estado anidado orders -> items
  const updateOrder = (oi, field, value) =>
    setData({
      ...data,
      orders: orders.map((o, i) => (i === oi ? { ...o, [field]: value } : o)),
    });

  const updateItem = (oi, ii, field, value) =>
    setData({
      ...data,
      orders: orders.map((o, i) =>
        i === oi
          ? { ...o, items: o.items.map((it, j) => (j === ii ? { ...it, [field]: value } : it)) }
          : o
      ),
    });

  const labelCls = "text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
      <div className={`${theme.bgSidebar} max-w-3xl w-full max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl flex flex-col border border-slate-700/30`}>
        <div className={`p-6 border-b ${isDarkMode ? "border-[#1E2235]" : "border-slate-200"}`}>
          <h2 className={`text-xl font-extrabold tracking-tight ${theme.textTitle}`}>{t.modalTitle}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{t.modalSubtitle}</p>
          <p className="text-[11px] font-mono text-slate-400 mt-2">
            {orders.length} PikTik · {totalItems} SKU · {totalBoxes.toLocaleString()} {t.modalBoxes}
          </p>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={labelCls}>{t.modalCompany}</label>
              <input
                type="text"
                value={data.company}
                onChange={(e) => setData({ ...data, company: e.target.value })}
                className={`w-full text-xs font-semibold px-3 py-2 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
            <div>
              <label className={labelCls}>{t.modalCustNo}</label>
              <input
                type="text"
                value={data.cust_no}
                onChange={(e) => setData({ ...data, cust_no: e.target.value })}
                className={`w-full text-xs font-semibold px-3 py-2 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
          </div>

          {data.warnings && data.warnings.length > 0 && (
            <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-[11px] text-amber-600 space-y-0.5">
              <p className="font-extrabold uppercase tracking-wider">{t.modalWarnings}</p>
              {data.warnings.map((w, i) => (
                <p key={i}>• {w}</p>
              ))}
            </div>
          )}

          <div className="space-y-4 max-h-[45vh] overflow-y-auto pr-1">
            {orders.map((order, oi) => (
              <div
                key={order.piktik}
                className={`border rounded-xl p-3 space-y-2.5 ${
                  isDarkMode ? "border-[#1E2235] bg-black/20" : "border-slate-200 bg-slate-50"
                }`}
              >
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] font-mono">
                  <span className={`font-extrabold ${theme.textSubtitle}`}>PikTik {order.piktik}</span>
                  <label className="flex items-center gap-1 text-slate-400">
                    PO
                    <input
                      type="text"
                      value={order.po}
                      onChange={(e) => updateOrder(oi, "po", e.target.value)}
                      className={`w-24 text-xs font-bold px-1.5 py-0.5 rounded border ${theme.inputBg}`}
                    />
                  </label>
                  <label className="flex items-center gap-1 text-slate-400">
                    {t.destinationDc}
                    <input
                      type="text"
                      value={order.ship_to_dc}
                      onChange={(e) => updateOrder(oi, "ship_to_dc", e.target.value)}
                      className={`w-14 text-xs font-bold px-1.5 py-0.5 rounded border ${theme.inputBg}`}
                    />
                  </label>
                  <span className="text-slate-400">{order.destination}</span>
                  {order.pages > 1 && (
                    <span className="text-slate-400">· {order.pages} {t.modalPages}</span>
                  )}
                </div>

                {order.items.map((item, ii) => (
                  <div key={ii} className="flex gap-2 items-center">
                    <input
                      type="text"
                      value={item.sku}
                      onChange={(e) => updateItem(oi, ii, "sku", e.target.value)}
                      className={`flex-1 min-w-0 text-xs font-mono font-bold px-2 py-1.5 rounded border ${theme.inputBg}`}
                      title={item.variant ? `${t.skuName}: ${item.variant}` : t.skuName}
                    />
                    {ITEM_FIELDS.map((f) => (
                      <input
                        key={f.key}
                        type="number"
                        value={item[f.key]}
                        onChange={(e) => updateItem(oi, ii, f.key, e.target.value)}
                        className={`${f.width} text-xs font-mono text-center px-1 py-1.5 rounded border ${f.bold ? "font-bold" : ""} ${theme.inputBg}`}
                        title={t[f.title]}
                      />
                    ))}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        <div className={`p-4 border-t flex justify-end gap-2.5 ${isDarkMode ? "border-[#1E2235] bg-[#11131F]" : "border-slate-200 bg-slate-100"}`}>
          <button onClick={onClose} className="px-4 py-2 rounded-lg text-xs font-bold border border-slate-300 text-slate-500 hover:bg-slate-200 transition">
            {t.modalCancel}
          </button>
          <button onClick={onConfirm} className="px-5 py-2 rounded-lg text-xs font-extrabold bg-[#0284C7] text-white hover:bg-[#0369A1] transition shadow-md">
            {t.modalImport}
          </button>
        </div>
      </div>
    </div>
  );
}
