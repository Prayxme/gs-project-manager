import { Link } from "react-router-dom";
import { useAppSettings } from "./AppSettings";
import { APP_I18N } from "./i18n";
import { MODULES } from "./modules";

export default function Home() {
  const { lang } = useAppSettings();
  const t = APP_I18N[lang];

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-ink">{t.homeTitle}</h2>
        <p className="text-sm mt-1 text-muted">{t.homeSubtitle}</p>

        <div className="grid gap-4 mt-6 sm:mt-8 sm:grid-cols-2 lg:grid-cols-3">
          {MODULES.map((m) => {
            const textos = t.modules[m.id];
            const activo = m.status === "active";
            return (
              <Link
                key={m.id}
                to={m.path}
                className="group card p-5 flex flex-col transition hover:-translate-y-0.5 hover:border-brand/60"
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="w-12 h-12 rounded-xl bg-brand-soft grid place-items-center text-2xl" aria-hidden="true">
                    {m.icon}
                  </span>
                  {!activo && (
                    <span className="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-300">
                      {t.comingSoon}
                    </span>
                  )}
                </div>
                <h3 className="text-lg font-extrabold mt-4 text-ink">{textos.name}</h3>
                <p className="text-sm mt-1 leading-relaxed text-muted flex-1">{textos.description}</p>
                <span className="inline-flex items-center gap-1 text-sm font-bold mt-4 text-brand">
                  {t.open} <span className="transition group-hover:translate-x-0.5">→</span>
                </span>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
