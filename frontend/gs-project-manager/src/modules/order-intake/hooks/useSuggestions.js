import { useState } from "react";
import { getSuggestions } from "../services/orderIntakeApi";

// Filas con Received = "No" cuyos contenedores ya llegaron (solo se sugieren).
export function useSuggestions({ t, task }) {
  const [suggestions, setSuggestions] = useState(null);
  const cargar = () => task.run(t.reading, async () => setSuggestions((await getSuggestions()).suggestions));
  return { suggestions, cargar };
}
