import { Link } from "react-router-dom";

const URGENTES = ["OVERDUE", "LAST DAY", "ATTENTION"];

// Acceso directo a Routing con las órdenes urgentes ya calculadas (vencidas, último día y atención).
// La ruta es relativa: el módulo de Routing vive junto a este, bajo el mismo almacén y cliente.
export default function RouteUrgentLink({ summary, t }) {
  const n = URGENTES.reduce((s, k) => s + (summary?.by_status?.[k] ?? 0), 0);
  return (
    <Link to="../routing?scope=urgent" relative="path" className="btn-secondary inline-flex items-center gap-2">
      🚚 {t.routeUrgent}
      {n > 0 && (
        <span className="rounded-full bg-orange-500 text-white text-xs font-extrabold px-2 py-0.5">{n}</span>
      )}
    </Link>
  );
}
