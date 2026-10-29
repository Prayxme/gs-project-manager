import { SKU_PALETTE } from '../../constants/palette';

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
  isDarkMode,
  t,
  theme,
}) {
  return (
    <div className={`w-[390px] border-r flex flex-col shrink-0 ${theme.bgSidebar}`}>
      {/* Header Sidebar */}
      <div className="p-4 border-b border-inherit flex justify-between items-center">
        <h2 className={`text-sm font-extrabold tracking-wide uppercase ${theme.textTitle}`}>
          {t.cargoSpecsTitle}
        </h2>
        <button
          onClick={triggerPdfUpload}
          disabled={pdfLoading}
          className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold px-3 py-1.5 rounded-lg transition shadow-sm flex items-center gap-1.5"
        >
          {pdfLoading ? t.scanningPdf : t.importPdfBtn}
        </button>
      </div>

      {/* Formularios */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        <div className="space-y-2">
          <h3 className={`text-[10px] font-extrabold uppercase tracking-widest ${theme.textSubtitle}`}>
            {t.orderInfoTitle}
          </h3>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[10px] text-slate-400 font-bold block mb-0.5">{t.poNumber}</label>
              <input
                type="text"
                value={orderInfo.po}
                onChange={(e) => setOrderInfo({ ...orderInfo, po: e.target.value })}
                className={`w-full text-xs font-mono px-2.5 py-1.5 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-400 font-bold block mb-0.5">{t.pikTik}</label>
              <input
                type="text"
                value={orderInfo.piktik}
                onChange={(e) => setOrderInfo({ ...orderInfo, piktik: e.target.value })}
                className={`w-full text-xs font-mono px-2.5 py-1.5 rounded-lg border outline-none ${theme.inputBg}`}
              />
            </div>
          </div>
        </div>

        {itemsForm.map((item, idx) => {
          const skuColor = skuColorMap[item.sku?.trim()] || SKU_PALETTE[0];
          return (
            <div
              key={idx}
              className={`space-y-2.5 relative border p-3.5 rounded-xl ${
                isDarkMode ? "border-[#1E2235] bg-black/20" : "border-slate-200 bg-slate-50 shadow-sm"
              }`}
            >
              {itemsForm.length > 1 && (
                <button
                  onClick={() => eliminarItem(idx)}
                  className="absolute top-2 right-2 text-slate-400 hover:text-red-500 text-xs font-bold w-5 h-5"
                >
                  ✕
                </button>
              )}
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full shadow-sm" style={{ backgroundColor: skuColor }} />
                <h3 className={`text-[10px] font-extrabold uppercase tracking-wider ${theme.textSubtitle}`}>
                  {t.skuTitle} #{idx + 1}
                </h3>
              </div>
              <div className="flex gap-2">
                <div className="flex-[2]">
                  <label className="text-[9px] text-slate-400 font-bold block mb-0.5">{t.skuName}</label>
                  <input
                    type="text"
                    value={item.sku}
                    onChange={(e) => actualizarItem(idx, "sku", e.target.value)}
                    className={`w-full text-xs font-mono font-bold px-2 py-1 rounded border outline-none ${theme.inputBg}`}
                  />
                </div>
                <div className="flex-1">
                  <label className="text-[9px] text-slate-400 font-bold block mb-0.5">{t.quantity}</label>
                  <input
                    type="number"
                    value={item.qty}
                    onChange={(e) => actualizarItem(idx, "qty", e.target.value)}
                    className={`w-full text-xs font-mono text-center font-bold px-2 py-1 rounded border outline-none ${theme.inputBg}`}
                  />
                </div>
              </div>
              <div className="grid grid-cols-4 gap-1.5">
                <div>
                  <label className="text-[9px] text-slate-400 font-bold block mb-0.5">{t.length}</label>
                  <input
                    type="number"
                    value={item.length}
                    onChange={(e) => actualizarItem(idx, "length", e.target.value)}
                    className={`w-full text-xs font-mono text-center px-1.5 py-1 rounded border ${theme.inputBg}`}
                  />
                </div>
                <div>
                  <label className="text-[9px] text-slate-400 font-bold block mb-0.5">{t.width}</label>
                  <input
                    type="number"
                    value={item.width}
                    onChange={(e) => actualizarItem(idx, "width", e.target.value)}
                    className={`w-full text-xs font-mono text-center px-1.5 py-1 rounded border ${theme.inputBg}`}
                  />
                </div>
                <div>
                  <label className="text-[9px] text-slate-400 font-bold block mb-0.5">{t.height}</label>
                  <input
                    type="number"
                    value={item.height}
                    onChange={(e) => actualizarItem(idx, "height", e.target.value)}
                    className={`w-full text-xs font-mono text-center px-1.5 py-1 rounded border ${theme.inputBg}`}
                  />
                </div>
                <div>
                  <label className="text-[9px] text-slate-400 font-bold block mb-0.5">{t.weight}</label>
                  <input
                    type="number"
                    value={item.weight}
                    onChange={(e) => actualizarItem(idx, "weight", e.target.value)}
                    className={`w-full text-xs font-mono text-center px-1.5 py-1 rounded border ${theme.inputBg}`}
                  />
                </div>
              </div>
            </div>
          );
        })}

        <button
          onClick={agregarItem}
          className={`w-full py-2.5 border border-dashed rounded-xl text-xs font-extrabold transition uppercase tracking-wider ${
            isDarkMode
              ? "border-slate-700 text-slate-400 hover:text-white hover:border-slate-500"
              : "border-slate-300 text-slate-600 hover:text-[#0284C7] hover:border-[#0284C7]"
          }`}
        >
          {t.addSkuBtn}
        </button>
      </div>

      {/* Botón Acción Principal */}
      <div className={`p-4 border-t ${theme.bgSidebarFooter}`}>
        <button
          onClick={calcularArmado}
          disabled={loading}
          className={`w-full py-3 text-xs font-extrabold rounded-xl transition shadow-md uppercase tracking-wider ${
            isDarkMode
              ? "bg-[#38BDF8] hover:bg-[#0284C7] text-slate-950 font-black"
              : "bg-[#0284C7] hover:bg-[#0369A1] text-white"
          }`}
        >
          {loading ? t.processingBtn : t.generateLayoutBtn}
        </button>
      </div>
    </div>
  );
}