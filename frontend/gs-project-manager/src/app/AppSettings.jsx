import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { buildTheme } from "../shared/theme";

// Preferencias globales (idioma y tema) compartidas por el shell y los módulos.
const AppSettingsContext = createContext(null);

function leer(clave, porDefecto) {
  try {
    const v = localStorage.getItem(clave);
    return v === null ? porDefecto : JSON.parse(v);
  } catch {
    return porDefecto;
  }
}

function guardar(clave, valor) {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch {
    // Sin almacenamiento disponible: la preferencia solo dura la sesión.
  }
}

export function AppSettingsProvider({ children }) {
  const [lang, setLang] = useState(() => leer("gs.lang", "en"));
  const [isDarkMode, setIsDarkMode] = useState(() => leer("gs.dark", false));

  useEffect(() => guardar("gs.lang", lang), [lang]);
  useEffect(() => {
    guardar("gs.dark", isDarkMode);
    // Los tokens de color de index.css cambian con esta clase.
    document.documentElement.classList.toggle("dark", isDarkMode);
  }, [isDarkMode]);
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const value = useMemo(
    () => ({ lang, setLang, isDarkMode, setIsDarkMode, theme: buildTheme(isDarkMode) }),
    [lang, isDarkMode]
  );
  return <AppSettingsContext.Provider value={value}>{children}</AppSettingsContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAppSettings() {
  const ctx = useContext(AppSettingsContext);
  if (!ctx) throw new Error("useAppSettings debe usarse dentro de <AppSettingsProvider>");
  return ctx;
}
