import { useContext } from "react";
import { AppSettingsContext } from "./context";

// { lang, setLang, isDarkMode, setIsDarkMode }
export function useAppSettings() {
  const ctx = useContext(AppSettingsContext);
  if (!ctx) throw new Error("useAppSettings debe usarse dentro de <AppSettingsProvider>");
  return ctx;
}

// Textos del idioma activo: const t = useTranslations(I18N);
export function useTranslations(diccionario) {
  const { lang } = useAppSettings();
  return diccionario[lang];
}
