import { Link, useLocation } from "react-router-dom";
import { useAppSettings } from "../../app/AppSettings";
import { APP_I18N } from "../../app/i18n";
import { MODULES } from "../../app/modules";

export default function Navbar() {
  const { lang, setLang, isDarkMode, setIsDarkMode } = useAppSettings();
  const t = APP_I18N[lang];
  const { pathname } = useLocation();
  const moduloActual = MODULES.find((m) => pathname.startsWith(m.path));

  return (
    <header className="bg-header text-on-header shrink-0 shadow-md">
      <div className="h-14 flex items-center justify-between gap-3 px-3 sm:px-6">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          {moduloActual && (
            <Link
              to="/"
              aria-label={t.backHome}
              className="sm:hidden -ml-1 w-9 h-9 grid place-items-center rounded-lg hover:bg-white/10 text-lg"
            >
              ←
            </Link>
          )}
          <Link to="/" className="flex items-center gap-2 min-w-0">
            <span className="w-8 h-8 shrink-0 rounded-lg bg-[#4C956C] text-white grid place-items-center font-black text-sm">
              GS
            </span>
            <span className={`font-extrabold tracking-tight truncate ${moduloActual ? "hidden md:inline" : ""}`}>
              {t.appTitle}
            </span>
          </Link>
          <span className="hidden lg:inline text-xs font-bold tracking-widest text-on-header-muted">
            {t.appSubtitle}
          </span>
          {moduloActual && (
            <>
              <span className="hidden md:inline text-on-header-muted">›</span>
              <span className="font-bold truncate">{t.modules[moduloActual.id].name}</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {moduloActual && (
            <Link
              to="/"
              className="hidden sm:inline-flex text-xs font-bold px-3 py-1.5 rounded-full border border-white/20 hover:bg-white/10 transition"
            >
              ← {t.home}
            </Link>
          )}
          <div className="flex items-center rounded-full bg-black/20 p-0.5 text-[11px] font-extrabold">
            {["en", "es"].map((code) => (
              <button
                key={code}
                onClick={() => setLang(code)}
                className={`px-2.5 py-1 rounded-full transition ${
                  lang === code ? "bg-[#4C956C] text-white" : "text-on-header-muted hover:text-on-header"
                }`}
              >
                {code.toUpperCase()}
              </button>
            ))}
          </div>
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            aria-label={isDarkMode ? "Light mode" : "Dark mode"}
            className="w-9 h-9 grid place-items-center rounded-full bg-black/20 hover:bg-black/30 transition"
          >
            {isDarkMode ? t.lightMode : t.darkMode}
          </button>
        </div>
      </div>
    </header>
  );
}
