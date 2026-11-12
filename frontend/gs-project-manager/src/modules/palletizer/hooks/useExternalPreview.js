import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { PREVIEW_SOURCE, leerVistaPallets } from "../../../shared/handoff";

// Carga enviada por otro módulo para verla en 3D (p. ej. un RTS de Routing): llega con
// ?source=preview y los datos en shared/handoff. Se calcula sola al abrir.
export function useExternalPreview(calcular, onGenerated) {
  const [params] = useSearchParams();
  const esVista = params.get("source") === PREVIEW_SOURCE;
  const [vista] = useState(() => (esVista ? leerVistaPallets() : null));

  // Formulario inicial: las mismas líneas (por PO) con las que se estimó en el módulo de origen.
  const inicial = useMemo(() => {
    if (!vista?.items?.length) return null;
    const pos = vista.pos.map((p) => p.po);
    const piktiks = [...new Set(vista.items.map((i) => i.piktik).filter(Boolean))];
    return {
      orderInfo: { po: pos.join(", "), piktik: piktiks.join(", "), company: "", custNo: "" },
      items: vista.items.map((i) => ({ ...i, dc: "" })),
    };
  }, [vista]);

  useEffect(() => {
    if (!inicial) return undefined;
    // En un temporizador: el cálculo no arranca dos veces con el doble montaje de React en desarrollo.
    const id = setTimeout(() => calcular(inicial.orderInfo, inicial.items, onGenerated), 0);
    return () => clearTimeout(id);
  }, [inicial, calcular, onGenerated]);

  return { vista: inicial ? vista : null, inicial };
}
