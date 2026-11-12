import { useMemo, useState } from "react";

const CAMPOS_BUSQUEDA = ["pick_ticket", "po", "cust", "cfrm_number", "notes", "ship_to"];

// Filtros de la tabla de órdenes activas: texto, estados (KPIs), cliente y "solo sin enrutar".
export function useOrderFilters(orders) {
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState([]);
  const [cliente, setCliente] = useState("");
  const [soloPendientes, setSoloPendientes] = useState(false);

  const clientes = useMemo(() => [...new Set(orders.map((o) => o.customer_code))].sort(), [orders]);

  const filtradas = useMemo(() => {
    const texto = q.trim().toLowerCase();
    return orders.filter((o) => {
      if (statusFilter.length && !statusFilter.includes(o.status)) return false;
      if (cliente && o.customer_code !== cliente) return false;
      if (soloPendientes && o.status === "ROUTED") return false;
      if (!texto) return true;
      return CAMPOS_BUSQUEDA.some((k) => (o[k] || "").toLowerCase().includes(texto));
    });
  }, [orders, q, statusFilter, cliente, soloPendientes]);

  const alternarEstado = (s) =>
    setStatusFilter((prev) => (prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]));

  const limpiar = () => {
    setQ("");
    setCliente("");
    setSoloPendientes(false);
    setStatusFilter([]);
  };

  return {
    q, setQ, cliente, setCliente, soloPendientes, setSoloPendientes, statusFilter,
    clientes, filtradas, alternarEstado, limpiar,
    hayFiltros: Boolean(q || cliente || soloPendientes || statusFilter.length > 0),
  };
}
