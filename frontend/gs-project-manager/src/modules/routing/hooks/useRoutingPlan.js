import { useCallback, useState } from "react";
import { contextoLocal } from "../../../shared/utils/dates";
import { planRouting, urgentPlan } from "../services/routingApi";

// Plan de RTS desde PDFs subidos o desde las órdenes urgentes del portal.
// "Hoy" es la fecha del navegador (como en el Monitor).
export function useRoutingPlan({ t, task }) {
  const [plan, setPlan] = useState(null);
  const [files, setFiles] = useState([]);
  const { run } = task;

  const subir = useCallback(
    async (lista) => {
      const r = await run(t.working, () => planRouting(lista, contextoLocal().today));
      if (r) {
        setPlan(r);
        setFiles(lista.map((f) => f.name));
      }
    },
    [t.working, run],
  );

  const cargarUrgentes = useCallback(async () => {
    const r = await run(t.workingUrgent, () => urgentPlan(contextoLocal().today));
    if (r) {
      setPlan(r);
      setFiles([]);
    }
  }, [t.workingUrgent, run]);

  return { plan, files, subir, cargarUrgentes };
}
