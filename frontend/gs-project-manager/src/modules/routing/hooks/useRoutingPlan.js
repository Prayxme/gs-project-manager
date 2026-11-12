import { useCallback, useEffect, useRef, useState } from "react";
import { contextoLocal } from "../../../shared/utils/dates";
import { guardarSesion, leerSesion } from "../../../shared/utils/storage";
import { planRouting, selectionPlan } from "../services/routingApi";

const CLAVE = "gs.routing.plan";
const VACIO = { plan: null, files: [], selKey: "" };

/**
 * Plan de RTS desde PDFs subidos o desde una selección de órdenes del Monitor.
 * "Hoy" es la fecha del navegador (como en el Monitor).
 * El plan se guarda en la sesión: al ir a ver los pallets en 3D y volver, sigue ahí.
 * `restaurar` = se está volviendo a esta página (atrás / "Volver a Routing"): la selección no se recalcula.
 */
export function useRoutingPlan({ t, task, seleccion, restaurar }) {
  const [estado, setEstado] = useState(() => leerSesion(CLAVE, VACIO));
  const { run } = task;

  const guardar = useCallback((nuevo) => {
    setEstado(nuevo);
    guardarSesion(CLAVE, nuevo);
  }, []);

  const subir = useCallback(
    async (lista) => {
      const r = await run(t.working, () => planRouting(lista, contextoLocal().today, seleccion));
      if (r) guardar({ plan: r, files: lista.map((f) => f.name), selKey: seleccion.key });
    },
    [t.working, run, seleccion, guardar],
  );

  const cargarSeleccion = useCallback(async () => {
    const r = await run(t.workingSelection, () => selectionPlan(seleccion, contextoLocal().today));
    if (r) guardar({ plan: r, files: [], selKey: seleccion.key });
  }, [t.workingSelection, run, seleccion, guardar]);

  // Al llegar con una selección se calcula una sola vez, salvo que se regrese a un plan ya guardado.
  const [yaCalculada] = useState(() =>
    restaurar && estado.plan && estado.selKey === seleccion.key ? seleccion.key : "");
  const calculada = useRef(yaCalculada);
  useEffect(() => {
    if (!seleccion.key || calculada.current === seleccion.key) return;
    calculada.current = seleccion.key;
    cargarSeleccion();
  }, [seleccion.key, cargarSeleccion]);

  const limpiar = useCallback(() => guardar(VACIO), [guardar]);

  return { plan: estado.plan, files: estado.files, subir, cargarSeleccion, limpiar };
}
