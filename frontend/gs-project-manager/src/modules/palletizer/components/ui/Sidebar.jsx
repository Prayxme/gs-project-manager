import { FileButton } from '../../../../shared/components';
import { SKU_PALETTE } from '../../constants/palette';
import { colorKey, skuDeLinea } from '../../utils/palletUtils';
import OrderInfoSection from './OrderInfoSection';
import SkuItemCard from './SkuItemCard';

// Panel izquierdo: importar PDF, datos de la orden, líneas de carga y botón de cálculo.
export default function Sidebar({ form, pdf, packing, onCalculate, t, className = "" }) {
  const { orderInfo, setOrderInfo, itemsForm, skuColorMap, actualizarItem, eliminarItem, agregarItem } = form;
  return (
    <aside className={`w-full md:w-[400px] lg:w-[420px] md:border-r border-line bg-surface flex-col shrink-0 min-h-0 ${className}`}>
      {/* Encabezado */}
      <div className="px-4 py-3 border-b border-line flex justify-between items-center gap-2">
        <h2 className="text-sm font-extrabold tracking-wide uppercase text-ink">{t.cargoSpecsTitle}</h2>
        <FileButton
          accept=".pdf"
          onFiles={([file]) => pdf.leerPdf(file)}
          disabled={pdf.pdfLoading}
          className="btn-primary text-xs px-3 py-1.5"
        >
          {pdf.pdfLoading ? t.scanningPdf : t.importPdfBtn}
        </FileButton>
      </div>

      {/* Formularios */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <OrderInfoSection orderInfo={orderInfo} setOrderInfo={setOrderInfo} t={t} />

        {itemsForm.map((item, idx) => (
          <SkuItemCard
            key={idx}
            item={item}
            idx={idx}
            color={skuColorMap[colorKey(item.po, skuDeLinea(item, idx))] || SKU_PALETTE[0]}
            canRemove={itemsForm.length > 1}
            onChange={actualizarItem}
            onRemove={eliminarItem}
            t={t}
          />
        ))}

        <button
          onClick={agregarItem}
          className="w-full py-2.5 border border-dashed border-line-strong rounded-xl text-xs font-extrabold uppercase tracking-wider text-muted hover:text-brand hover:border-brand transition"
        >
          {t.addSkuBtn}
        </button>
      </div>

      {/* Acción principal */}
      <div className="p-4 border-t border-line bg-surface-2">
        <button onClick={onCalculate} disabled={packing.loading} className="btn-primary w-full py-3 uppercase tracking-wider">
          {packing.loading ? t.processingBtn : t.generateLayoutBtn}
        </button>
      </div>
    </aside>
  );
}
