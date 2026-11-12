import { lazy } from "react";

// Catálogo de módulos (herramientas). Un módulo se escribe una vez y se habilita para uno o
// varios clientes en registry/warehouses.js. `slug` es su segmento en la URL.
// Textos (nombre y descripción): app/i18n.js -> modules.<id>.
export const MODULES = [
  {
    id: "palletizer",
    slug: "palletizer",
    icon: "📦",
    status: "active",
    component: lazy(() => import("../../modules/palletizer/PalletizerPage")),
  },
  {
    id: "open-orders",
    slug: "open-orders",
    icon: "📋",
    status: "active",
    component: lazy(() => import("../../modules/open-orders/OpenOrdersPage")),
  },
  {
    id: "order-intake",
    slug: "order-intake",
    icon: "📥",
    status: "active",
    component: lazy(() => import("../../modules/order-intake/OrderIntakePage")),
  },
  {
    id: "routing",
    slug: "routing",
    icon: "🚚",
    status: "active",
    component: lazy(() => import("../../modules/routing/RoutingPage")),
  },
];

export const MODULE_BY_ID = Object.fromEntries(MODULES.map((m) => [m.id, m]));
