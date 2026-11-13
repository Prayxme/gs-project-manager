import { useCallback, useState } from "react";
import { fmt } from "../../../shared/i18n/format";
import { contextoLocal } from "../../../shared/utils/dates";
import { guardarSesion, leerSesion } from "../../../shared/utils/storage";
import { parsePreRoute, preRoutePlan } from "../services/routingApi";
import { lineasParaEnviar, nuevaLinea } from "../utils/preroute";

const CLAVE = "gs.routing.preroute";

/**
 * Líneas de Pre Routing (importadas de un Excel o escritas a mano) y su cálculo.
 * Las líneas se guardan en la sesión para no perderlas al cambiar de módulo.
 * `onPlan(plan, archivos)` recibe el plan calculado (lo muestra la página de Routing).
 */
export function usePreRoute({ t, task, onPlan }) {
  const [estado, setEstado] = useState(() => leerSesion(CLAVE, { lines: [], file: "", warnings: [] }));
  const { run } = task;

  const guardar = useCallback((cambio) => {
    setEstado((previo) => {
      const nuevo = { ...previo, ...cambio(previo) };
      guardarSesion(CLAVE, nuevo);
      return nuevo;
    });
  }, []);

  const importar = useCallback(
    async ([archivo]) => {
      const r = await run(t.pre.reading, () => parsePreRoute(archivo));
      if (r) guardar(() => ({ lines: r.lines.map((l) => nuevaLinea(l)), file: r.filename, warnings: r.warnings }));
    },
    [t.pre.reading, run, guardar],
  );

  const agregar = () => guardar((p) => ({ lines: [...p.lines, nuevaLinea(copiaDeCabecera(p.lines))] }));
  const editar = (id, campo, valor) =>
    guardar((p) => ({ lines: p.lines.map((l) => (l.id === id ? { ...l, [campo]: valor } : l)) }));
  const quitar = (id) => guardar((p) => ({ lines: p.lines.filter((l) => l.id !== id) }));
  const vaciar = () => guardar(() => ({ lines: [], file: "", warnings: [] }));

  const calcular = async () => {
    const lineas = lineasParaEnviar(estado.lines);
    if (!lineas.length) {
      task.setError(t.pre.noLines);
      return;
    }
    const plan = await run(fmt(t.pre.working, { n: lineas.length }), () => preRoutePlan(lineas, contextoLocal().today));
    if (plan) onPlan(plan, estado.file ? [estado.file] : []);
  };

  return { ...estado, importar, agregar, editar, quitar, vaciar, calcular };
}

// Al agregar una línea a mano se repiten cliente y fechas de la anterior (suelen ser los mismos).
function copiaDeCabecera(lineas) {
  const ultima = lineas[lineas.length - 1];
  return ultima ? { cust: ultima.cust, ship_date: ultima.ship_date, cancel_date: ultima.cancel_date } : {};
}
