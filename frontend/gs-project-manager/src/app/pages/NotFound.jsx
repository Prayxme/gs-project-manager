import { Link } from "react-router-dom";
import { useTranslations } from "../../shared/settings";
import { APP_I18N } from "../i18n";

export default function NotFound() {
  const t = useTranslations(APP_I18N);
  return (
    <div className="h-full flex flex-col items-center justify-center gap-3">
      <p className="text-muted">{t.notFound}</p>
      <Link to="/" className="font-bold text-brand">{t.backHome}</Link>
    </div>
  );
}
