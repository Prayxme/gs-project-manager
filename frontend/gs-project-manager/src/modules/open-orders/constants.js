// Estados del monitor y sus estilos (equivalentes a los colores del Google Sheet).
export const STATUSES = ["OVERDUE", "LAST DAY", "ATTENTION", "SAFE", "TOO EARLY", "ROUTED"];

export const STATUS_STYLE = {
  OVERDUE: { row: "bg-red-500/[0.07]", badge: "bg-red-600 text-white", kpi: "bg-red-500" },
  "LAST DAY": { row: "bg-orange-500/[0.07]", badge: "bg-orange-500 text-white", kpi: "bg-orange-500" },
  ATTENTION: { row: "bg-amber-400/[0.08]", badge: "bg-amber-400 text-slate-900", kpi: "bg-amber-400" },
  SAFE: { row: "", badge: "bg-surface-3 text-ink-2", kpi: "bg-[#4A5C6A]" },
  "TOO EARLY": { row: "opacity-70", badge: "bg-[#9BA8AB] text-[#06141B]", kpi: "bg-[#9BA8AB]" },
  ROUTED: { row: "bg-brand/[0.05]", badge: "bg-brand text-on-brand", kpi: "bg-brand" },
};

export const CLOSED_STYLE = {
  COMPLETED: "bg-brand text-on-brand",
  REMOVED: "bg-amber-400 text-slate-900",
  CANCELLED: "bg-red-600 text-white",
};

export const AUTO_REFRESH_POLL_MS = 60_000; // la vista relee la base cada minuto

export const I18N = {
  es: {
    title: "Monitor de Routing Wiesner",
    caTime: "Hora California",
    lastUpdate: "Última actualización",
    never: "nunca",
    updateNow: "Actualizar ahora",
    updating: "Consultando portal...",
    auto: "Auto cada {n} min",
    tabs: { active: "Órdenes activas", events: "Historial de cambios", closed: "Cerradas" },
    kpis: {
      total: "Activas", OVERDUE: "Vencidas", "LAST DAY": "Último día", ATTENTION: "Atención",
      SAFE: "A tiempo", "TOO EARLY": "Muy pronto", ROUTED: "Enrutadas",
      newToday: "Nuevas hoy", apptsToday: "Citas hoy", completedToday: "Completadas hoy",
    },
    search: "Buscar PO, pick ticket, cliente, confirmación, notas...",
    allCustomers: "Todos los clientes",
    pendingOnly: "Solo sin enrutar",
    clearFilters: "Limpiar filtros",
    showing: "Mostrando {n} de {t}",
    cols: {
      status: "Estado", days: "Días", deadline: "Límite routing", pickTicket: "Pick Ticket", po: "PO#",
      customer: "Cliente", shipDate: "Ship Date", cancelDate: "Cancel Date", cfrm: "Cfrm Number",
      appt: "Cita", notes: "Notas", ctns: "Ctns", lastChange: "Último cambio",
      when: "Cuándo", event: "Evento", old: "Antes", new: "Ahora",
      dateRemoved: "Fecha salida", finalStatus: "Estado final", reason: "Motivo", source: "Origen",
    },
    cfrmType: { APPOINTMENT: "cita", ROUTING: "routing", OTHER: "otro" },
    importCsv: "Importar histórico (CSV)",
    importDone: "Importadas: {i} · repetidas: {d} · inválidas: {x}",
    refreshDone: "✔ Actualizado: {total} órdenes activas · {n} nuevas · {c} con cambios · {r} salieron del portal",
    refreshNoChanges: "✔ Actualizado: {total} órdenes activas · sin cambios desde la última consulta",
    noData: "Sin datos todavía. Pulsa “Actualizar ahora”.",
    errorPrefix: "Error",
    window: "Ventana abre",
  },
  en: {
    title: "Wiesner Routing Monitor",
    caTime: "California time",
    lastUpdate: "Last update",
    never: "never",
    updateNow: "Update now",
    updating: "Querying portal...",
    auto: "Auto every {n} min",
    tabs: { active: "Active orders", events: "Change history", closed: "Closed" },
    kpis: {
      total: "Active", OVERDUE: "Overdue", "LAST DAY": "Last day", ATTENTION: "Attention",
      SAFE: "Safe", "TOO EARLY": "Too early", ROUTED: "Routed",
      newToday: "New today", apptsToday: "Appts today", completedToday: "Completed today",
    },
    search: "Search PO, pick ticket, customer, confirmation, notes...",
    allCustomers: "All customers",
    pendingOnly: "Not routed only",
    clearFilters: "Clear filters",
    showing: "Showing {n} of {t}",
    cols: {
      status: "Status", days: "Days", deadline: "Routing deadline", pickTicket: "Pick Ticket", po: "PO#",
      customer: "Customer", shipDate: "Ship Date", cancelDate: "Cancel Date", cfrm: "Cfrm Number",
      appt: "Appt", notes: "Notes", ctns: "Ctns", lastChange: "Last change",
      when: "When", event: "Event", old: "Before", new: "Now",
      dateRemoved: "Date removed", finalStatus: "Final status", reason: "Reason", source: "Source",
    },
    cfrmType: { APPOINTMENT: "appt", ROUTING: "routing", OTHER: "other" },
    importCsv: "Import history (CSV)",
    importDone: "Imported: {i} · duplicates: {d} · invalid: {x}",
    refreshDone: "✔ Updated: {total} active orders · {n} new · {c} changed · {r} left the portal",
    refreshNoChanges: "✔ Updated: {total} active orders · no changes since the last check",
    noData: "No data yet. Click “Update now”.",
    errorPrefix: "Error",
    window: "Window opens",
  },
};

export const fmt = (s, vars) => s.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");
