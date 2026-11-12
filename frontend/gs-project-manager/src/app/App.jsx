import { Suspense } from "react";
import { Link, Outlet, Route, Routes } from "react-router-dom";
import Navbar from "../shared/components/Navbar";
import { useAppSettings } from "./AppSettings";
import Home from "./Home";
import { APP_I18N } from "./i18n";
import { MODULES } from "./modules";

function Layout() {
  return (
    <div className="flex flex-col h-dvh w-full overflow-hidden bg-canvas text-ink transition-colors duration-200">
      <Navbar />
      <main className="flex-1 overflow-hidden">
        <Suspense fallback={null}>
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
}

function NotFound() {
  const { lang } = useAppSettings();
  const t = APP_I18N[lang];
  return (
    <div className="h-full flex flex-col items-center justify-center gap-3">
      <p className="text-muted">{t.notFound}</p>
      <Link to="/" className="font-bold text-brand">{t.backHome}</Link>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        {MODULES.map(({ id, path, component: Page }) => (
          <Route key={id} path={path} element={<Page />} />
        ))}
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
