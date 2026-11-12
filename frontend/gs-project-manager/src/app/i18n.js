// Textos del shell (navegación, almacenes, clientes). Cada módulo tiene sus propios textos.
export const APP_I18N = {
  en: {
    appTitle: "Golden State Project Manager",
    lightMode: "☀️",
    darkMode: "🌙",
    home: "Home",
    back: "Back",
    open: "Open",
    comingSoon: "Coming soon",
    notFound: "Page not found.",
    notFoundHint: "The address does not match any warehouse, client or module.",
    backHome: "Back to home",
    warehousesTitle: "Warehouses",
    warehousesSubtitle: "Select a warehouse to start working.",
    clientsTitle: "{w} warehouse",
    clientsSubtitle: "Select a client.",
    modulesTitle: "{c} · {w}",
    modulesSubtitle: "Select a tool to start working.",
    soonTitle: "{w}: coming soon",
    soonText: "We are working on the {w} warehouse. Its clients and tools will appear here soon.",
    clientsCount: "{n} client(s)",
    modulesCount: "{n} module(s)",
    warehouses: {
      bonnie: "Bonnie warehouse.",
      perris: "Perris warehouse.",
      vernon: "Vernon warehouse.",
    },
    clients: {
      wiesner: "Wiesner Products: palletizing, open orders, order intake and routing.",
    },
    modules: {
      palletizer: {
        name: "3D Palletizer",
        description: "Read Pick Tickets (PDF), build optimized pallets per PO and view them in 3D.",
      },
      "open-orders": {
        name: "Open Orders Monitor",
        description: "Track open orders in the warehouse: filter, sort and monitor.",
      },
      "order-intake": {
        name: "Order Intake",
        description: "Read Pick Ticket PDFs and register new orders and revisions in the control sheet.",
      },
      routing: {
        name: "Routing (RTS)",
        description: "Estimate pallets per PO, reconcile with the Wiesner portal and group POs into RTS by destination.",
      },
    },
  },
  es: {
    appTitle: "Golden State Project Manager",
    lightMode: "☀️",
    darkMode: "🌙",
    home: "Inicio",
    back: "Volver",
    open: "Abrir",
    comingSoon: "Próximamente",
    notFound: "Página no encontrada.",
    notFoundHint: "La dirección no corresponde a ningún almacén, cliente o módulo.",
    backHome: "Volver al inicio",
    warehousesTitle: "Almacenes",
    warehousesSubtitle: "Selecciona un almacén para comenzar.",
    clientsTitle: "Almacén {w}",
    clientsSubtitle: "Selecciona un cliente.",
    modulesTitle: "{c} · {w}",
    modulesSubtitle: "Selecciona una herramienta para comenzar.",
    soonTitle: "{w}: próximamente",
    soonText: "Estamos trabajando en el almacén {w}. Pronto aparecerán aquí sus clientes y herramientas.",
    clientsCount: "{n} cliente(s)",
    modulesCount: "{n} módulo(s)",
    warehouses: {
      bonnie: "Almacén Bonnie.",
      perris: "Almacén Perris.",
      vernon: "Almacén Vernon.",
    },
    clients: {
      wiesner: "Wiesner Products: paletizado, órdenes abiertas, ingreso de órdenes y routing.",
    },
    modules: {
      palletizer: {
        name: "Paletizador 3D",
        description: "Lee Pick Tickets (PDF), arma pallets optimizados por PO y los muestra en 3D.",
      },
      "open-orders": {
        name: "Monitor de Órdenes Abiertas",
        description: "Seguimiento de las órdenes abiertas en bodega: filtra, ordena y monitorea.",
      },
      "order-intake": {
        name: "Ingreso de Órdenes",
        description: "Lee los PDF de Pick Tickets y registra órdenes nuevas y revisiones en la hoja de control.",
      },
      routing: {
        name: "Routing (RTS)",
        description: "Estima pallets por PO, concilia con el portal de Wiesner y agrupa las POs en RTS por destino.",
      },
    },
  },
};
