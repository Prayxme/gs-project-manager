import { Link } from "react-router-dom";
import { fmt } from "../../shared/i18n/format";
import { useTranslations } from "../../shared/settings";
import { APP_I18N } from "../i18n";

// Almacén todavía sin clientes ni herramientas.
export default function ComingSoonPage({ warehouse }) {
  const t = useTranslations(APP_I18N);
  return (
    <div className="h-full grid place-items-center px-4">
      <div className="card max-w-lg w-full p-8 text-center">
        <span className="w-16 h-16 mx-auto rounded-2xl bg-brand-soft grid place-items-center text-3xl" aria-hidden="true">
          🚧
        </span>
        <span className="inline-block mt-5 text-[11px] font-extrabold uppercase tracking-wider px-2.5 py-1 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-300">
          {t.comingSoon}
        </span>
        <h2 className="text-2xl font-black tracking-tight text-ink mt-3">{fmt(t.soonTitle, { w: warehouse.name })}</h2>
        <p className="text-sm text-muted mt-2 leading-relaxed">{fmt(t.soonText, { w: warehouse.name })}</p>
        <Link to="/" className="btn-secondary inline-flex mt-6">← {t.backHome}</Link>
      </div>
    </div>
  );
}
