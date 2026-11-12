import { useEffect, useMemo, useState } from "react";
import { guardarPreferencia, leerPreferencia } from "../utils/storage";
import { AppSettingsContext } from "./context";

export default function AppSettingsProvider({ children }) {
  const [lang, setLang] = useState(() => leerPreferencia("gs.lang", "en"));
  const [isDarkMode, setIsDarkMode] = useState(() => leerPreferencia("gs.dark", false));

  useEffect(() => guardarPreferencia("gs.lang", lang), [lang]);
  useEffect(() => {
    guardarPreferencia("gs.dark", isDarkMode);
    // Los tokens de color de index.css cambian con esta clase.
    document.documentElement.classList.toggle("dark", isDarkMode);
  }, [isDarkMode]);
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo(() => ({ lang, setLang, isDarkMode, setIsDarkMode }), [lang, isDarkMode]);
  return <AppSettingsContext.Provider value={value}>{children}</AppSettingsContext.Provider>;
}
