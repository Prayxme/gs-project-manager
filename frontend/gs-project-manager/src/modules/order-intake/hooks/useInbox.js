import { useCallback, useEffect, useState } from "react";
import { fmt } from "../../../shared/i18n/format";
import { INBOX_REFRESH_MS } from "../constants";
import { checkGmailNow, dismissInboxItem, getInbox, restoreInboxItem } from "../services/orderIntakeApi";

/**
 * Bandeja de Gmail: PDFs recibidos y su estado. La revisión automática corre en el backend;
 * aquí se relee la lista cada 2 minutos y se puede pedir una revisión inmediata.
 */
export function useInbox({ t, task, onNotice }) {
  const { setError } = task;
  const [items, setItems] = useState([]);
  const [pending, setPending] = useState(0);
  const [lastCheck, setLastCheck] = useState(null);
  const [showAll, setShowAll] = useState(false);

  // El estado solo cambia al llegar la respuesta (nunca de forma síncrona dentro de un efecto).
  const cargar = useCallback(
    () =>
      getInbox(showAll)
        .then((r) => {
          setItems(r.items);
          setPending(r.pending);
          setLastCheck(r.last_check);
        })
        .catch((e) => setError(e.message)),
    [showAll, setError]
  );

  useEffect(() => {
    const primera = setTimeout(cargar, 0);
    const id = setInterval(cargar, INBOX_REFRESH_MS);
    return () => {
      clearTimeout(primera);
      clearInterval(id);
    };
  }, [cargar]);

  const revisarAhora = () =>
    task.run(t.inbox.checking, async () => {
      const r = await checkGmailNow();
      onNotice(fmt(t.inbox.checkDone, { n: r.new, p: r.pending }));
      await cargar();
    });

  const cambiar = (accion) => (id) => task.run("", async () => {
    await accion(id);
    await cargar();
  });

  return {
    items, pending, lastCheck, showAll, setShowAll, cargar, revisarAhora,
    descartar: cambiar(dismissInboxItem),
    restaurar: cambiar(restoreInboxItem),
  };
}
