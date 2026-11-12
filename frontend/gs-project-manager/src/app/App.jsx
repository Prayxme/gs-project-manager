import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { MODULES } from "./modules";
import Home from "./pages/Home";
import NotFound from "./pages/NotFound";

// Rutas de la plataforma: inicio + una ruta por módulo registrado en modules.js.
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
