import { useState, useMemo, useRef } from 'react';
import { useAppSettings } from '../../app/AppSettings';
import { I18N } from './constants/i18n';
import { colorPorIndice } from './constants/palette';
import { LOGISTICS_DEFAULTS } from './constants/logisticsConfig';
import { parsePdfTicket, packOrder } from './services/palletApi';
import { agruparPallets, calculateCenteredOffsets, colorKey } from './utils/palletUtils';

import Sidebar from './components/ui/Sidebar';
import PdfReviewModal from './components/ui/PdfReviewModal';
import LayoutSelector from './components/ui/LayoutSelector';
import TrailerCard from './components/ui/TrailerCard';
import Viewport3D from './components/3d/Viewport3D';

export default function PalletizerPage() {
  // Idioma y tema vienen del shell (compartidos por todos los módulos).
  const { lang, isDarkMode } = useAppSettings();
  const t = I18N[lang];

  const [loading, setLoading] = useState(false);
  // En celular: 'data' (formulario) o '3d' (visor y resultados).
  const [vista, setVista] = useState("data");
  const fileInputRef = useRef(null);

  // Estados de PDF
  const [pdfLoading, setPdfLoading] = useState(false);
  const [showPdfModal, setShowPdfModal] = useState(false);
  const [pdfParsedData, setPdfParsedData] = useState(null);

  // Estados de Palletizing y Formularios
  const [gruposPallets, setGruposPallets] = useState([]);
  const [grupoSeleccionadoIdx, setGrupoSeleccionadoIdx] = useState(0);

  const [orderInfo, setOrderInfo] = useState({ po: "", piktik: "", company: "", custNo: "" });
  const [itemsForm, setItemsForm] = useState([{ width: 0, length: 0, height: 0, weight: 0, qty: 0, sku: "" }]);

  // Un color único por combinación PO + SKU: el mismo SKU en dos POs distintas
  // recibe colores distintos, y ningún color se repite entre POs.
  const skuColorMap = useMemo(() => {
    const map = {};
    itemsForm.forEach((item, idx) => {
      const key = colorKey(item.po, item.sku?.trim() || `ITEM-${idx + 1}`);
      if (!map[key]) {
        map[key] = colorPorIndice(Object.keys(map).length);
      }
    });
    return map;
  }, [itemsForm]);

  // Handlers del Formulario
  const agregarItem = () =>
    setItemsForm([...itemsForm, { width: 0, length: 0, height: 0, weight: 0, qty: 0, sku: "" }]);
  const actualizarItem = (idx, campo, valor) => {
    setItemsForm(itemsForm.map((item, i) => (i === idx ? { ...item, [campo]: valor } : item)));
  };
  const eliminarItem = (idx) => setItemsForm(itemsForm.filter((_, i) => i !== idx));

  // Handler de carga de PDF
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPdfLoading(true);

    try {
      const data = await parsePdfTicket(file);
      setPdfParsedData(data);
      setShowPdfModal(true);
    } catch (error) {
      alert(`${lang === "es" ? "Error leyendo el PDF:" : "Error parsing PDF:"} ${error.message}`);
    } finally {
      setPdfLoading(false);
      e.target.value = null;
    }
  };

  // Una línea del formulario por cada SKU de cada PikTik; conserva PO/PikTik/DC
  // para que el motor nunca mezcle órdenes distintas en un mismo pallet.
  const aplicarDatosPDF = () => {
    const orders = pdfParsedData.orders || [];
    setOrderInfo({
      po: orders.map((o) => o.po).join(", "),
      piktik: orders.map((o) => o.piktik).join(", "),
      company: pdfParsedData.company,
      custNo: pdfParsedData.cust_no,
    });
    setItemsForm(
      orders.flatMap((order) =>
        order.items.map((item, idx) => ({
          sku: item.sku || `ITEM-${idx + 1}`,
          qty: item.qty,
          length: item.l,
          width: item.w,
          height: item.h,
          weight: item.weight,
          po: order.po,
          piktik: order.piktik,
          dc: order.ship_to_dc,
        }))
      )
    );
    setGruposPallets([]);
    setShowPdfModal(false);
  };

  // Handler de cálculo de distribución
  const calcularArmado = async () => {
    setLoading(true);
    const payload = {
      order_id: orderInfo.po || "PO-ONLINE",
      pallet_config: {
        length_in: LOGISTICS_DEFAULTS.PALLET_LENGTH,
        width_in: LOGISTICS_DEFAULTS.PALLET_WIDTH,
        base_height_in: LOGISTICS_DEFAULTS.PALLET_BASE_HEIGHT,
        max_total_height_in: LOGISTICS_DEFAULTS.MAX_TOTAL_HEIGHT,
        // Sin max_weight_lbs: el límite de peso por pallet aún no es regla de negocio.
      },
      items: itemsForm
        .filter((i) => Number(i.qty) > 0)
        .map((i, idx) => ({
          sku: i.sku || `ITEM-${idx + 1}`,
          quantity: Number(i.qty),
          dimensions: {
            length_in: Number(i.length),
            width_in: Number(i.width),
            height_in: Number(i.height),
          },
          weight_lbs: Number(i.weight),
          po: i.po || null,
          piktik: i.piktik || null,
          ship_to_dc: i.dc || null,
        })),
    };

    try {
      const data = await packOrder(payload);
      if (data && data.pallets && data.pallets.length > 0) {
        setGruposPallets(agruparPallets(data.pallets));
        setGrupoSeleccionadoIdx(0);
        setVista("3d");
        if (data.unplaced_boxes > 0) {
          alert(
            lang === "es"
              ? `Atención: ${data.unplaced_boxes} cajas no pudieron colocarse (no caben en el pallet).`
              : `Warning: ${data.unplaced_boxes} boxes could not be placed (they do not fit on the pallet).`
          );
        }
      } else {
        alert(lang === "es" ? "No se pudieron generar pallets con estos parámetros." : "No pallets generated with these parameters.");
      }
    } catch (error) {
      alert(`${lang === "es" ? "Error:" : "Error:"} ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const grupoActivo = gruposPallets[grupoSeleccionadoIdx];
  const palletData = grupoActivo?.pallet; // Cambiado de 'data' a 'pallet' para que coincida con tu util
  const totalPalletsGenerados = gruposPallets.reduce((acc, curr) => acc + curr.count, 0); // Cambiado de 'cantidad' a 'count'

  const totalCubeFeet = totalPalletsGenerados * LOGISTICS_DEFAULTS.CFT_POR_PALLET;
  const numRTs = Math.ceil(totalCubeFeet / LOGISTICS_DEFAULTS.MAX_CFT_POR_RT);

  const totalNetWeight = itemsForm.reduce(
    (acc, curr) => acc + Number(curr.qty) * Number(curr.weight),
    0
  );
  const totalGrossWeight = totalNetWeight + totalPalletsGenerados * LOGISTICS_DEFAULTS.PESO_MADERA_LBS;

  const offsets = useMemo(
    () => calculateCenteredOffsets(palletData, LOGISTICS_DEFAULTS.PALLET_WIDTH, LOGISTICS_DEFAULTS.PALLET_LENGTH),
    [palletData]
  );

  const pestana = (id, texto) => (
    <button
      onClick={() => setVista(id)}
      className={`flex-1 py-2 rounded-lg text-sm font-extrabold transition ${
        vista === id ? "bg-brand text-on-brand shadow-sm" : "text-muted hover:text-ink"
      }`}
    >
      {texto}
    </button>
  );

  return (
    <div className="flex flex-col md:flex-row h-full w-full overflow-hidden">
      {/* Input oculto para carga de PDF */}
      <input type="file" accept=".pdf" ref={fileInputRef} onChange={handleFileUpload} className="hidden" />

      <PdfReviewModal
        show={showPdfModal}
        data={pdfParsedData}
        setData={setPdfParsedData}
        onClose={() => setShowPdfModal(false)}
        onConfirm={aplicarDatosPDF}
        t={t}
      />

      {/* Selector de vista (solo celular) */}
      <div className="md:hidden flex gap-1 p-1 m-2 mb-0 rounded-xl bg-surface border border-line shrink-0">
        {pestana("data", t.tabCargo)}
        {pestana("3d", `${t.tab3d}${totalPalletsGenerados ? ` · ${totalPalletsGenerados}` : ""}`)}
      </div>

      <Sidebar
        className={vista === "data" ? "flex flex-1 md:flex-none" : "hidden md:flex"}
        orderInfo={orderInfo}
        setOrderInfo={setOrderInfo}
        itemsForm={itemsForm}
        actualizarItem={actualizarItem}
        eliminarItem={eliminarItem}
        agregarItem={agregarItem}
        skuColorMap={skuColorMap}
        calcularArmado={calcularArmado}
        loading={loading}
        pdfLoading={pdfLoading}
        triggerPdfUpload={() => fileInputRef.current.click()}
        t={t}
      />

      {/* Visor 3D + resultados */}
      <div className={`${vista === "3d" ? "flex" : "hidden md:flex"} flex-1 flex-col relative min-h-0 overflow-y-auto md:overflow-hidden`}>
        <Viewport3D
          palletData={palletData}
          isDarkMode={isDarkMode}
          t={t}
          grupoSeleccionadoIdx={grupoSeleccionadoIdx}
          skuColorMap={skuColorMap}
          offsets={offsets}
        />

        {/* Paneles: flotantes a la derecha en escritorio, debajo del visor en celular */}
        {gruposPallets.length > 0 && (
          <div className="p-3 md:p-0 md:absolute md:top-4 md:right-4 z-20 flex flex-col gap-2.5 md:w-80 md:max-h-[calc(100%-2rem)] md:overflow-y-auto">
            <LayoutSelector
              gruposPallets={gruposPallets}
              grupoSeleccionadoIdx={grupoSeleccionadoIdx}
              setGrupoSeleccionadoIdx={setGrupoSeleccionadoIdx}
              t={t}
            />
            <TrailerCard
              totalPalletsGenerados={totalPalletsGenerados}
              numRTs={numRTs}
              totalCubeFeet={totalCubeFeet}
              totalGrossWeight={totalGrossWeight}
              maxCft={LOGISTICS_DEFAULTS.MAX_CFT_POR_RT}
              t={t}
            />
          </div>
        )}
      </div>
    </div>
  );
}
