import { useCallback, useMemo, useState } from 'react';
import { useAppSettings, useTranslations } from '../../shared/settings';
import { I18N } from './constants/i18n';
import { LOGISTICS_DEFAULTS } from './constants/logisticsConfig';
import { useCargoForm } from './hooks/useCargoForm';
import { useExternalPreview } from './hooks/useExternalPreview';
import { usePacking } from './hooks/usePacking';
import { usePdfImport } from './hooks/usePdfImport';
import { calculateCenteredOffsets, conPalletsDeMargen, trailerMetrics } from './utils/palletUtils';

import Viewport3D from './components/3d/Viewport3D';
import LayoutSelector from './components/ui/LayoutSelector';
import MobileViewSwitch from './components/ui/MobileViewSwitch';
import PdfReviewModal from './components/ui/PdfReviewModal';
import PreviewCard from './components/ui/PreviewCard';
import Sidebar from './components/ui/Sidebar';
import TrailerCard from './components/ui/TrailerCard';

export default function PalletizerPage() {
  // Idioma y tema vienen del shell (compartidos por todos los módulos).
  const { isDarkMode } = useAppSettings();
  const t = useTranslations(I18N);
  // En celular: 'data' (formulario) o '3d' (visor y resultados).
  const [vista, setVista] = useState("data");

  const pdf = usePdfImport(t);
  const packing = usePacking(t);
  // Carga enviada por otro módulo (un RTS de Routing): se calcula sola y muestra sus pallets de margen.
  const verEn3d = useCallback(() => setVista("3d"), []);
  const { vista: vistaExterna, inicial } = useExternalPreview(packing.calcular, verEn3d);
  const form = useCargoForm(inicial);

  const aplicarDatosPDF = () => {
    form.cargarDesdePdf(pdf.pdfParsedData);
    packing.limpiar();
    pdf.cerrarModal();
  };

  const calcularArmado = () => packing.calcular(form.orderInfo, form.itemsForm, verEn3d);

  const { grupoSeleccionadoIdx, setGrupoSeleccionadoIdx } = packing;
  const gruposPallets = useMemo(
    () => (vistaExterna ? conPalletsDeMargen(packing.gruposPallets, vistaExterna.pos) : packing.gruposPallets),
    [packing.gruposPallets, vistaExterna]
  );
  const palletData = gruposPallets[grupoSeleccionadoIdx]?.pallet;
  const metricas = trailerMetrics(gruposPallets, form.itemsForm);

  const offsets = useMemo(
    () => calculateCenteredOffsets(palletData, LOGISTICS_DEFAULTS.PALLET_WIDTH, LOGISTICS_DEFAULTS.PALLET_LENGTH),
    [palletData]
  );

  return (
    <div className="flex flex-col md:flex-row h-full w-full overflow-hidden">
      <PdfReviewModal
        show={pdf.showPdfModal}
        data={pdf.pdfParsedData}
        setData={pdf.setPdfParsedData}
        onClose={pdf.cerrarModal}
        onConfirm={aplicarDatosPDF}
        t={t}
      />

      <MobileViewSwitch vista={vista} setVista={setVista} totalPallets={metricas.totalPallets} t={t} />

      <Sidebar
        className={vista === "data" ? "flex flex-1 md:flex-none" : "hidden md:flex"}
        form={form}
        pdf={pdf}
        packing={packing}
        onCalculate={calcularArmado}
        t={t}
      />

      {/* Visor 3D + resultados */}
      <div className={`${vista === "3d" ? "flex" : "hidden md:flex"} flex-1 flex-col relative min-h-0 overflow-y-auto md:overflow-hidden`}>
        <Viewport3D
          palletData={palletData}
          isDarkMode={isDarkMode}
          t={t}
          grupoSeleccionadoIdx={grupoSeleccionadoIdx}
          skuColorMap={form.skuColorMap}
          offsets={offsets}
        />

        {/* Paneles: flotantes a la derecha en escritorio, debajo del visor en celular */}
        {(gruposPallets.length > 0 || vistaExterna) && (
          <div className="p-3 md:p-0 md:absolute md:top-4 md:right-4 z-20 flex flex-col gap-2.5 md:w-80 md:max-h-[calc(100%-2rem)] md:overflow-y-auto">
            {vistaExterna && <PreviewCard vista={vistaExterna} gruposPallets={gruposPallets} t={t} />}
            <LayoutSelector
              gruposPallets={gruposPallets}
              grupoSeleccionadoIdx={grupoSeleccionadoIdx}
              setGrupoSeleccionadoIdx={setGrupoSeleccionadoIdx}
              showPo={Boolean(vistaExterna)}
              t={t}
            />
            {!vistaExterna && <TrailerCard
              totalPalletsGenerados={metricas.totalPallets}
              numRTs={metricas.numRTs}
              totalCubeFeet={metricas.totalCubeFeet}
              totalGrossWeight={metricas.totalGrossWeight}
              maxCft={LOGISTICS_DEFAULTS.MAX_CFT_POR_RT}
              t={t}
            />}
          </div>
        )}
      </div>
    </div>
  );
}
