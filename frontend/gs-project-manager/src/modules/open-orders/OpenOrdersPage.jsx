import { useAppSettings } from "../../app/AppSettings";
import { APP_I18N } from "../../app/i18n";

// Módulo en construcción: se implementará a partir del script de Google Apps Script.
export default function OpenOrdersPage() {
  const { lang, theme } = useAppSettings();
  const t = APP_I18N[lang];
  const textos = t.modules["open-orders"];
  return (
    <div className="h-full flex flex-col items-center justify-center gap-2 px-6 text-center">
      <span className="text-4xl" aria-hidden="true">📋</span>
      <h2 className={`text-xl font-black ${theme.textTitle}`}>{textos.name}</h2>
      <p className={`text-sm max-w-md ${theme.textMuted}`}>{textos.description}</p>
      <span className="mt-2 text-xs font-extrabold uppercase tracking-wider px-3 py-1 rounded-full bg-amber-500/15 text-amber-600">
        {t.comingSoon}
      </span>
    </div>
  );
}
