import { Link, useLocation } from "react-router-dom";
import { useTranslations } from "../../shared/settings";
import { APP_I18N } from "../i18n";
import { breadcrumbs } from "../routing/breadcrumbs";
import Breadcrumbs from "./Breadcrumbs";
import LanguageSwitch from "./LanguageSwitch";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const t = useTranslations(APP_I18N);
  const { pathname } = useLocation();
  const { items, parent } = breadcrumbs(pathname, t);
  const dentro = items.length > 0;

  return (
    <header className="bg-header text-on-header shrink-0 shadow-md">
      <div className="h-14 flex items-center justify-between gap-3 px-3 sm:px-6">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          {dentro && (
            <Link
              to={parent}
              aria-label={t.back}
              className="sm:hidden -ml-1 w-9 h-9 grid place-items-center rounded-lg hover:bg-white/10 text-lg"
            >
              ←
            </Link>
          )}
          <Link to="/" className="flex items-center gap-2 min-w-0 shrink-0">
            <span className="w-8 h-8 shrink-0 rounded-lg bg-[#4C956C] text-white grid place-items-center font-black text-sm">
              GS
            </span>
            <span className={`font-extrabold tracking-tight truncate ${dentro ? "hidden lg:inline" : ""}`}>
              {t.appTitle}
            </span>
          </Link>
          {dentro && <Breadcrumbs items={items} />}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {dentro && (
            <Link
              to={parent}
              className="hidden sm:inline-flex text-xs font-bold px-3 py-1.5 rounded-full border border-white/20 hover:bg-white/10 transition"
            >
              ← {t.back}
            </Link>
          )}
          <LanguageSwitch />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
