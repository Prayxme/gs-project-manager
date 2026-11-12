import { useCallback, useState } from "react";
import { fmt } from "../../../shared/i18n/format";
import { packOrder } from "../services/palletApi";
import { agruparPallets, buildPackingPayload } from "../utils/palletUtils";

// Cálculo de pallets en el backend y selección del layout que se muestra en 3D.
export function usePacking(t) {
  const [loading, setLoading] = useState(false);
  const [gruposPallets, setGruposPallets] = useState([]);
  const [grupoSeleccionadoIdx, setGrupoSeleccionadoIdx] = useState(0);

  // onGenerated() se llama apenas hay pallets (antes de cualquier aviso).
  const calcular = useCallback(async (orderInfo, items, onGenerated) => {
    setLoading(true);
    try {
      const data = await packOrder(buildPackingPayload(orderInfo, items));
      if (data?.pallets?.length > 0) {
        setGruposPallets(agruparPallets(data.pallets));
        setGrupoSeleccionadoIdx(0);
        onGenerated?.();
        if (data.unplaced_boxes > 0) alert(fmt(t.unplacedWarn, { n: data.unplaced_boxes }));
      } else {
        alert(t.noPallets);
      }
    } catch (error) {
      alert(`${t.errorPrefix} ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, [t]);

  return {
    loading, gruposPallets, grupoSeleccionadoIdx, setGrupoSeleccionadoIdx, calcular,
    limpiar: () => setGruposPallets([]),
  };
}
