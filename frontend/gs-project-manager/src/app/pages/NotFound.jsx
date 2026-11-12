import { Link } from "react-router-dom";
import { useTranslations } from "../../shared/settings";
import { APP_I18N } from "../i18n";

// Cualquier URL que no esté declarada en registry/warehouses.js.
export default function NotFound() {
  const t = useTranslations(APP_I18N);
  return (
    <div className="h-full flex flex-col items-center justify-center gap-2 px-4 text-center">
      <p className="text-5xl font-black text-ink">404</p>
      <p className="font-bold text-ink">{t.notFound}</p>
      <p className="text-sm text-muted">{t.notFoundHint}</p>
      <Link to="/" className="font-bold text-brand mt-2">{t.backHome}</Link>
    </div>
  );
}
