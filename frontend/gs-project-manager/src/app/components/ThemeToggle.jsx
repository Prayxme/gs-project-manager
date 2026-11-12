import { useAppSettings, useTranslations } from "../../shared/settings";
import { APP_I18N } from "../i18n";

export default function ThemeToggle() {
  const { isDarkMode, setIsDarkMode } = useAppSettings();
  const t = useTranslations(APP_I18N);
  return (
    <button
      onClick={() => setIsDarkMode(!isDarkMode)}
      aria-label={isDarkMode ? "Light mode" : "Dark mode"}
      className="w-9 h-9 grid place-items-center rounded-full bg-black/20 hover:bg-black/30 transition"
    >
      {isDarkMode ? t.lightMode : t.darkMode}
    </button>
  );
}
