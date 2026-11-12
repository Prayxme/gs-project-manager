import { Suspense } from "react";
import { Outlet } from "react-router-dom";
import CanonicalPath from "../routing/CanonicalPath";
import Navbar from "./Navbar";

// Marco de la plataforma: barra superior + página del almacén/cliente/módulo activo.
export default function Layout() {
  return (
    <CanonicalPath>
      <div className="flex flex-col h-dvh w-full overflow-hidden bg-canvas text-ink transition-colors duration-200">
        <Navbar />
        <main className="flex-1 overflow-hidden">
          <Suspense fallback={null}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </CanonicalPath>
  );
}
