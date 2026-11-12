import { useMemo, useState } from "react";
import { buildSkuColorMap, formDesdePdf, lineaVacia } from "../utils/palletUtils";

// Formulario de carga: datos de la orden + una línea por SKU (manual o importada del PDF).
export function useCargoForm() {
  const [orderInfo, setOrderInfo] = useState({ po: "", piktik: "", company: "", custNo: "" });
  const [itemsForm, setItemsForm] = useState([lineaVacia()]);

  const skuColorMap = useMemo(() => buildSkuColorMap(itemsForm), [itemsForm]);

  const agregarItem = () => setItemsForm([...itemsForm, lineaVacia()]);
  const actualizarItem = (idx, campo, valor) =>
    setItemsForm(itemsForm.map((item, i) => (i === idx ? { ...item, [campo]: valor } : item)));
  const eliminarItem = (idx) => setItemsForm(itemsForm.filter((_, i) => i !== idx));

  const cargarDesdePdf = (pdf) => {
    const { orderInfo: info, items } = formDesdePdf(pdf);
    setOrderInfo(info);
    setItemsForm(items);
  };

  return {
    orderInfo, setOrderInfo, itemsForm, skuColorMap,
    agregarItem, actualizarItem, eliminarItem, cargarDesdePdf,
  };
}
