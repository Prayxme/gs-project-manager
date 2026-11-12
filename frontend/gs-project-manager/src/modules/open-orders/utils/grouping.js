import { STATUSES } from "../constants/status";

const cartones = (o) => Number(String(o.ctns || "").replace(/,/g, "")) || 0;
const SIN_FECHA = 1e9;

// Órdenes divididas por estado y, dentro de cada estado, por Customer No completo (BURL120,
// BURL240...: son divisiones de la misma tienda que se enrutan por separado).
// -> [{ status, orders, groups: [{ cust, orders, ctns, deadline, days }] }] (solo estados con órdenes)
export function seccionesPorEstado(orders) {
  return STATUSES.map((status) => {
    const delEstado = orders.filter((o) => o.status === status);
    const porCliente = new Map();
    delEstado.forEach((o) => porCliente.set(o.cust, [...(porCliente.get(o.cust) || []), o]));

    const groups = [...porCliente.entries()]
      .map(([cust, lista]) => {
        // La orden más urgente del grupo marca su fecha límite.
        const primera = lista.reduce((a, b) => ((b.days_remaining ?? SIN_FECHA) < (a.days_remaining ?? SIN_FECHA) ? b : a));
        return {
          cust,
          orders: lista,
          ctns: lista.reduce((s, o) => s + cartones(o), 0),
          deadline: primera.routing_deadline,
          days: primera.days_remaining,
        };
      })
      .sort((a, b) => (a.days ?? SIN_FECHA) - (b.days ?? SIN_FECHA) || a.cust.localeCompare(b.cust));

    return { status, orders: delEstado, groups };
  }).filter((s) => s.orders.length > 0);
}
