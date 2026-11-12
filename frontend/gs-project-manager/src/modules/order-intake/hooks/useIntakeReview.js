import { useState } from "react";
import { fmt } from "../../../shared/i18n/format";
import { aOrden, analyzePdf, applyOrders, checkOrders } from "../services/orderIntakeApi";

// Por defecto quedan marcadas las órdenes nuevas y con revisión.
const seleccionInicial = (orders) => new Set(orders.filter((o) => o.status !== "REGISTERED").map((o) => o.piktik));

// "ABCU1234567, XYZU7654321" -> ["ABCU1234567", "XYZU7654321"]
const separarContenedores = (texto) => texto.split(/[\s,]+/).filter(Boolean);

/**
 * Revisión de PDFs: leer, corregir en pantalla, volver a verificar y escribir en la hoja.
 * task: useBusyTask() de la página · onNotice: mensaje de éxito · onWritten: tras escribir.
 */
export function useIntakeReview({ t, task, onNotice, onWritten }) {
  const { run, setError } = task;
  const [rows, setRows] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [files, setFiles] = useState([]);
  const [pdfWarnings, setPdfWarnings] = useState([]);
  const [dirty, setDirty] = useState(false);

  const mostrar = (orders) => {
    setRows(orders);
    setSelected(seleccionInicial(orders));
    setDirty(false);
  };

  const subir = (lista) => {
    onNotice("");
    return run(t.reading, async () => {
      const porPiktik = new Map();
      const avisos = [];
      for (const f of lista) {
        const r = await analyzePdf(f);
        r.orders.forEach((o) => porPiktik.set(o.piktik, o));
        r.pdf_warnings.forEach((w) => avisos.push(`${f.name}: ${w}`));
      }
      mostrar([...porPiktik.values()]);
      setFiles(lista.map((f) => f.name));
      setPdfWarnings(avisos);
    });
  };

  const editar = (piktik, key, valor) => {
    setRows((prev) =>
      prev.map((r) =>
        r.piktik === piktik ? { ...r, [key]: key === "containers" ? separarContenedores(valor) : valor } : r
      )
    );
    setDirty(true);
  };

  const verificar = () => run(t.reading, async () => mostrar((await checkOrders(rows.map(aOrden))).orders));

  const aEscribir = rows.filter((r) => selected.has(r.piktik) && r.status !== "REGISTERED");
  const nNuevas = aEscribir.filter((r) => r.status === "NEW").length;
  const nRev = aEscribir.length - nNuevas;

  const escribir = async () => {
    if (!aEscribir.length) {
      setError(t.nothing);
      return;
    }
    if (!window.confirm(fmt(t.confirm, { n: nNuevas, r: nRev }))) return;
    await run(t.writing, async () => {
      const r = await applyOrders(aEscribir.map(aOrden), files.join(", "));
      onNotice(fmt(t.done, { n: r.written.length, r: r.revised.length, u: r.unchanged.length }));
      const again = await checkOrders(rows.map(aOrden));
      setRows(again.orders);
      setSelected(seleccionInicial(again.orders));
      onWritten();
    });
  };

  const alternar = (pt) =>
    setSelected((prev) => {
      const s = new Set(prev);
      if (s.has(pt)) s.delete(pt);
      else s.add(pt);
      return s;
    });

  const conteo = (st) => rows.filter((r) => r.status === st).length;

  return {
    rows, selected, files, pdfWarnings, dirty, aEscribir,
    subir, editar, verificar, escribir, alternar, conteo,
  };
}
