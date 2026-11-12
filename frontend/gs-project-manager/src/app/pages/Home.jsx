import { useTranslations } from "../../shared/settings";
import ModuleCard from "../components/ModuleCard";
import { APP_I18N } from "../i18n";
import { MODULES } from "../modules";

export default function Home() {
  const t = useTranslations(APP_I18N);

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-ink">{t.homeTitle}</h2>
        <p className="text-sm mt-1 text-muted">{t.homeSubtitle}</p>

        <div className="grid gap-4 mt-6 sm:mt-8 sm:grid-cols-2 lg:grid-cols-3">
          {MODULES.map((m) => (
            <ModuleCard
              key={m.id}
              module={m}
              texts={t.modules[m.id]}
              comingSoonLabel={t.comingSoon}
              openLabel={t.open}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
