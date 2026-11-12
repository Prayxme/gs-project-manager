// Almacenes -> clientes -> módulos habilitados. Es la ÚNICA fuente de las rutas de la app:
//   /<almacén>                     clientes del almacén (o "Próximamente")
//   /<almacén>/<cliente>           módulos del cliente
//   /<almacén>/<cliente>/<módulo>  la herramienta
// Cualquier URL que no salga de aquí muestra "Página no encontrada".
//
// Para habilitar un cliente nuevo: agregarlo en `clients` de su almacén con los ids de módulos
// (registry/modules.js) y su descripción en app/i18n.js -> clients.<id>.
// Para abrir un almacén: status "active" y al menos un cliente.
export const WAREHOUSES = [
  {
    id: "bonnie",
    name: "Bonnie",
    icon: "🏭",
    status: "active",
    clients: [
      { id: "wiesner", name: "Wiesner", icon: "🧦", modules: ["palletizer", "open-orders", "order-intake"] },
    ],
  },
  { id: "perris", name: "Perris", icon: "🏭", status: "soon", clients: [] },
  { id: "vernon", name: "Vernon", icon: "🏭", status: "soon", clients: [] },
];

// Rutas anteriores a la organización por almacén/cliente: redirigen a su lugar actual.
export const LEGACY_REDIRECTS = {
  "/palletizer": "/bonnie/wiesner/palletizer",
  "/open-orders": "/bonnie/wiesner/open-orders",
  "/order-intake": "/bonnie/wiesner/order-intake",
};
