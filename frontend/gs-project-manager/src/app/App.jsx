import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import ClientPage from "./pages/ClientPage";
import ComingSoonPage from "./pages/ComingSoonPage";
import NotFound from "./pages/NotFound";
import WarehousePage from "./pages/WarehousePage";
import WarehousesPage from "./pages/WarehousesPage";
import { LEGACY_REDIRECTS, WAREHOUSES } from "./registry/warehouses";
import { clientModules } from "./routing/paths";

// Rutas generadas SOLO desde el registro (almacén -> cliente -> módulo). Lo que no esté
// declarado cae en NotFound: así no existen URLs inválidas.
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<WarehousesPage />} />

        {WAREHOUSES.map((w) => (
          <Route key={w.id} path={w.id}>
            <Route
              index
              element={w.status === "active" && w.clients.length ? <WarehousePage warehouse={w} /> : <ComingSoonPage warehouse={w} />}
            />
            {w.clients.map((c) => (
              <Route key={c.id} path={c.id}>
                <Route index element={<ClientPage warehouse={w} client={c} />} />
                {clientModules(c).map(({ id, slug, component: Page }) => (
                  <Route key={id} path={slug} element={<Page />} />
                ))}
              </Route>
            ))}
          </Route>
        ))}

        {Object.entries(LEGACY_REDIRECTS).map(([viejo, nuevo]) => (
          <Route key={viejo} path={viejo} element={<Navigate to={nuevo} replace />} />
        ))}

        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
