import { Link } from "react-router-dom";
import { useAppSettings } from "./AppSettings";
import { APP_I18N } from "./i18n";
import { MODULES } from "./modules";

export default function Home() {
  const { lang, theme } = useAppSettings();
  const t = APP_I18N[lang];

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <h2 className={`text-2xl font-black tracking-tight ${theme.textTitle}`}>{t.homeTitle}</h2>
        <p className={`text-sm mt-1 ${theme.textMuted}`}>{t.homeSubtitle}</p>

        <div className="grid gap-4 mt-8 sm:grid-cols-2">
          {MODULES.map((m) => {
            const textos = t.modules[m.id];
            const activo = m.status === "active";
            return (
              <Link
                key={m.id}
                to={m.path}
                className={`block rounded-2xl border p-5 transition ${theme.bgCard}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="text-3xl" aria-hidden="true">{m.icon}</span>
                  {!activo && (
                    <span className="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-600">
                      {t.comingSoon}
                    </span>
                  )}
                </div>
                <h3 className={`text-lg font-extrabold mt-3 ${theme.textTitle}`}>{textos.name}</h3>
                <p className={`text-sm mt-1 leading-relaxed ${theme.textMuted}`}>{textos.description}</p>
                <span className={`inline-block text-sm font-bold mt-4 ${theme.textSubtitle}`}>{t.open} →</span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
