import { lazy } from "react";

// Registro central de módulos. Para agregar un módulo nuevo:
//   1. crear src/modules/<id>/ con su página principal;
//   2. añadir una entrada aquí y sus textos en app/i18n.js (modules.<id>).
// El shell genera automáticamente la ruta y la tarjeta del inicio.
export const MODULES = [
  {
    id: "palletizer",
    path: "/palletizer",
    icon: "📦",
    status: "active",
    component: lazy(() => import("../modules/palletizer/PalletizerPage")),
  },
  {
    id: "open-orders",
    path: "/open-orders",
    icon: "📋",
    status: "active",
    component: lazy(() => import("../modules/open-orders/OpenOrdersPage")),
  },
];
