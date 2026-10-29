export default function Navbar({ lang, setLang, isDarkMode, setIsDarkMode, t, theme }) {
  return (
    <header className={`h-14 border-b flex justify-between items-center px-6 shrink-0 ${theme.bgHeader}`}>
      <div className="flex items-center gap-3">
        <h1 className={`text-base font-extrabold tracking-tight ${theme.textSubtitle}`}>
          {t.appTitle}
        </h1>
        <span className="text-slate-400/50">|</span>
        <p className="text-[11px] font-semibold text-slate-400 tracking-wider uppercase hidden sm:block">
          {t.appSubtitle}
        </p>
      </div>

      <div className="flex items-center gap-3">
        <div className="flex items-center border rounded-full overflow-hidden p-0.5 border-slate-300 dark:border-slate-700 text-[11px] font-extrabold">
          <button
            onClick={() => setLang("en")}
            className={`px-2.5 py-0.5 rounded-full transition ${
              lang === "en" ? "bg-[#0284C7] text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setLang("es")}
            className={`px-2.5 py-0.5 rounded-full transition ${
              lang === "es" ? "bg-[#0284C7] text-white shadow-sm" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            ES
          </button>
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