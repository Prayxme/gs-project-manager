import { useCallback, useState } from "react";
import { contextoLocal } from "../../../shared/utils/dates";
import { planRouting } from "../services/routingApi";

// PDFs elegidos -> plan de RTS. "Hoy" es la fecha del navegador (como en el Monitor).
export function useRoutingPlan({ t, task }) {
  const [plan, setPlan] = useState(null);
  const [files, setFiles] = useState([]);

  const subir = useCallback(
    async (lista) => {
      const r = await task.run(t.working, () => planRouting(lista, contextoLocal().today));
      if (r) {
        setPlan(r);
        setFiles(lista.map((f) => f.name));
      }
    },
    [t.working, task],
  );

  return { plan, files, subir };
}
