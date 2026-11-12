import { useCallback, useState } from "react";

/**
 * Tarea asíncrona con indicador de ocupado y error:
 *   const { busy, error, setError, run } = useBusyTask();
 *   await run("Leyendo...", () => api());   // busy = "Leyendo..." mientras dura
 * Si la tarea falla, el mensaje queda en error y run devuelve undefined.
 */
export function useBusyTask() {
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");

  const run = useCallback(async (label, tarea) => {
    setBusy(label);
    setError("");
    try {
      return await tarea();
    } catch (e) {
      setError(e.message);
      return undefined;
    } finally {
      setBusy("");
    }
  }, []);

  return { busy, error, setError, run };
}
