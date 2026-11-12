import { useCallback, useEffect, useState } from "react";
import { fmt } from "../../../shared/i18n/format";
import { AUTO_REFRESH_POLL_MS } from "../constants";
import {
  getClosed, getEvents, getOrders, getSummary, importCompletedCsv, refreshNow, setAutoRefresh,
} from "../services/openOrdersApi";

/**
 * Datos del monitor y acciones sobre el backend.
 * La actualización automática del portal corre en el backend; aquí solo se relee la base.
 */
export function useOpenOrdersData(tab, t) {
  const [orders, setOrders] = useState([]);
  const [summary, setSummary] = useState(null);
  const [events, setEvents] = useState([]);
  const [closed, setClosed] = useState([]);
  const [refrescando, setRefrescando] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");

  // El estado solo se actualiza al llegar la respuesta (nunca de forma síncrona dentro de un efecto).
  const cargarActivas = useCallback(
    () =>
      Promise.all([getOrders(), getSummary()])
        .then(([o, s]) => {
          setOrders(o.orders);
          setSummary(s);
          setError("");
        })
        .catch((e) => setError(e.message)),
    []
  );

  const cargarTab = useCallback((cual) => {
    const peticion =
      cual === "events" ? getEvents(1000).then((r) => setEvents(r.events))
      : cual === "closed" ? getClosed().then((r) => setClosed(r.closed))
      : Promise.resolve();
    return peticion.catch((e) => setError(e.message));
  }, []);

  // Carga inicial y relectura periódica.
  useEffect(() => {
    const id = setInterval(cargarActivas, AUTO_REFRESH_POLL_MS);
    const primera = setTimeout(cargarActivas, 0);
    return () => {
      clearInterval(id);
      clearTimeout(primera);
    };
  }, [cargarActivas]);

  useEffect(() => {
    const id = setTimeout(() => cargarTab(tab), 0);
    return () => clearTimeout(id);
  }, [tab, cargarTab]);

  const actualizarAhora = async () => {
    setRefrescando(true);
    setAviso("");
    try {
      const r = await refreshNow();
      setAviso(
        r.new || r.changed || r.removed
          ? fmt(t.refreshDone, { total: r.total, n: r.new, c: r.changed, r: r.removed })
          : fmt(t.refreshNoChanges, { total: r.total })
      );
      await cargarActivas();
      await cargarTab(tab);
    } catch (e) {
      setError(e.message);
    } finally {
      setRefrescando(false);
    }
  };

  const alternarAuto = async () => {
    try {
      await setAutoRefresh(!summary?.auto_refresh);
      await cargarActivas();
    } catch (e) {
      setError(e.message);
    }
  };

  const importarCsv = async (file) => {
    try {
      const r = await importCompletedCsv(file);
      setAviso(fmt(t.importDone, { i: r.inserted, d: r.duplicates, x: r.invalid, r: r.reclassified ?? 0 }));
      await cargarTab("closed");
      await cargarActivas();
    } catch (e) {
      setError(e.message);
    }
  };

  return {
    orders, summary, events, closed, refrescando,
    error, setError, aviso, setAviso,
    actualizarAhora, alternarAuto, importarCsv,
  };
}
