import { Link, useLocation } from "react-router-dom";
import { useAppSettings } from "../../app/AppSettings";
import { APP_I18N } from "../../app/i18n";
import { MODULES } from "../../app/modules";

export default function Navbar() {
  const { lang, setLang, isDarkMode, setIsDarkMode, theme } = useAppSettings();
  const t = APP_I18N[lang];
  const { pathname } = useLocation();
  const moduloActual = MODULES.find((m) => pathname.startsWith(m.path));

  return (
    <header className={`h-14 border-b flex justify-between items-center px-6 shrink-0 ${theme.bgHeader}`}>
      <div className="flex items-center gap-3 min-w-0">
        <Link to="/" className={`text-base font-extrabold tracking-tight whitespace-nowrap ${theme.textSubtitle}`}>
          {t.appTitle}
        </Link>
        <span className="text-slate-400/50">|</span>
        <p className="text-xs font-semibold text-slate-400 tracking-wider uppercase hidden sm:block">
          {t.appSubtitle}
        </p>
        {moduloActual && (
          <>
            <span className="text-slate-400/50">›</span>
            <span className={`text-sm font-bold truncate ${theme.textTitle}`}>
              {t.modules[moduloActual.id].name}
            </span>
          </>
        )}
      </div>

      <div className="flex items-center gap-3">
        {moduloActual && (
          <Link
            to="/"
            className={`text-xs font-bold px-3 py-1 rounded-full border transition ${
              isDarkMode ? "border-slate-700 text-slate-300 hover:text-white" : "border-slate-300 text-slate-600 hover:text-slate-900"
            }`}
          >
            ← {t.home}
          </Link>
        )}
        <div className="flex items-center border rounded-full overflow-hidden p-0.5 border-slate-300 dark:border-slate-700 text-[11px] font-extrabold">
          {["en", "es"].map((code) => (
            <button
              key={code}
              onClick={() => setLang(code)}
              className={`px-2.5 py-0.5 rounded-full transition ${
                lang === code ? "bg-[#0284C7] text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {code.toUpperCase()}
            </button>
          ))}
        </div>

        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className={`border px-3.5 py-1 rounded-full transition font-bold text-xs ${
            isDarkMode
              ? "border-slate-700 text-white bg-slate-800/50"
              : "border-slate-300 text-slate-700 bg-white shadow-sm"
          }`}
        >
          {isDarkMode ? t.lightMode : t.darkMode}
        </button>
      </div>
    </header>
  );
}
