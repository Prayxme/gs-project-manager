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

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm p-4">
      <div className={`${theme.bgSidebar} max-w-3xl w-full max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl flex flex-col border border-slate-700/30`}>
        <div className={`p-6 border-b ${isDarkMode ? "border-[#1E2235]" : "border-slate-200"}`}>
          <h2 className={`text-xl font-extrabold tracking-tight ${theme.textTitle}`}>{t.modalTitle}</h2>
          <p className="text-xs text-slate-500 mt-0.5">{t.modalSubtitle}</p>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                {t.modalCompany}
              </label>
              <input
                type="text"
                value={data.company}
                onChange={(e) => setData({ ...data, company: e.target.value })}
                className={`w-full text-xs font-semibold px-3 py-2 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
            <div>
              <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                {t.modalCustNo}
              </label>
              <input
                type="text"
                value={data.cust_no}
                onChange={(e) => setData({ ...data, cust_no: e.target.value })}
                className={`w-full text-xs font-semibold px-3 py-2 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
            <div>
              <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                {t.poNumber}
              </label>
              <input
                type="text"
                value={data.po}
                onChange={(e) => setData({ ...data, po: e.target.value })}
                className={`w-full text-xs font-semibold px-3 py-2 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
            <div>
              <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                {t.pikTik}
              </label>
              <input
                type="text"
                value={data.piktik}
                onChange={(e) => setData({ ...data, piktik: e.target.value })}
                className={`w-full text-xs font-semibold px-3 py-2 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
          </div>

          <div>
            <h3 className={`text-xs font-extrabold tracking-wider uppercase mb-3 ${theme.textTitle}`}>
              {t.modalDetectedSkus} ({data.items.length})
            </h3>
            <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
              {data.items.map((item, idx) => (
                <div
                  key={idx}
                  className={`p-2.5 border rounded-xl flex gap-2 items-center ${
                    isDarkMode ? "border-[#1E2235] bg-black/20" : "border-slate-200 bg-slate-50"
                  }`}
                >
                  <input
                    type="text"
                    value={item.sku}
                    onChange={(e) => {
                      const newItems = [...data.items];
                      newItems[idx].sku = e.target.value;
                      setData({ ...data, items: newItems });
                    }}
                    className={`flex-1 text-xs font-mono font-bold px-2 py-1.5 rounded border ${theme.inputBg}`}
                    title={t.skuName}
                  />
                  <input
                    type="number"
                    value={item.qty}
                    onChange={(e) => {
                      const newItems = [...data.items];
                      newItems[idx].qty = e.target.value;
                      setData({ ...data, items: newItems });
                    }}
                    className={`w-16 text-xs font-mono text-center font-bold px-1 py-1.5 rounded border ${theme.inputBg}`}
                    title={t.quantity}
                  />
                  <input
                    type="number"
                    value={item.l}
                    onChange={(e) => {
                      const newItems = [...data.items];
                      newItems[idx].l = e.target.value;
                      setData({ ...data, items: newItems });
                    }}
                    className={`w-14 text-xs font-mono text-center px-1 py-1.5 rounded border ${theme.inputBg}`}
                    title={t.length}
                  />
                  <span className="text-slate-400 text-xs">×</span>
                  <input
                    type="number"
                    value={item.w}
                    onChange={(e) => {
                      const newItems = [...data.items];
                      newItems[idx].w = e.target.value;
                      setData({ ...data, items: newItems });
                    }}
                    className={`w-14 text-xs font-mono text-center px-1 py-1.5 rounded border ${theme.inputBg}`}
                    title={t.width}
                  />
                  <span className="text-slate-400 text-xs">×</span>
                  <input
                    type="number"
                    value={item.h}
                    onChange={(e) => {
                      const newItems = [...data.items];
                      newItems[idx].h = e.target.value;
                      setData({ ...data, items: newItems });
                    }}
                    className={`w-14 text-xs font-mono text-center px-1 py-1.5 rounded border ${theme.inputBg}`}
                    title={t.height}
                  />
                  <input
                    type="number"
                    value={item.weight}
                    onChange={(e) => {
                      const newItems = [...data.items];
                      newItems[idx].weight = e.target.value;
                      setData({ ...data, items: newItems });
                    }}
                    className={`w-16 text-xs font-mono text-center px-1 py-1.5 rounded border ${theme.inputBg}`}
                    title={t.weight}
                  />
                </div>
              ))}
            </div>
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