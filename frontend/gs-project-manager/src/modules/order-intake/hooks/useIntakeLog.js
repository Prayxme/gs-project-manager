import { useState } from "react";
import { getLog } from "../services/orderIntakeApi";

// Historial de escrituras: se carga al abrir la pestaña y se invalida después de escribir.
export function useIntakeLog(setError) {
  const [log, setLog] = useState(null);

  const cargarSiHaceFalta = async () => {
    if (log !== null) return;
    try {
      setLog((await getLog()).log);
    } catch (e) {
      setError(e.message);
    }
  };

  return { log, cargarSiHaceFalta, invalidar: () => setLog(null) };
}
