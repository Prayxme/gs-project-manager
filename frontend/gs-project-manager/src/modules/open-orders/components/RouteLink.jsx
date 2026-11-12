import { Link } from "react-router-dom";

// Enlace al módulo de Routing con una selección de órdenes: estados y, opcionalmente, un Customer No.
// Routing calcula esas órdenes con los Pick Tickets ya recibidos y permite subir los PDFs que falten.
// La ruta es relativa: Routing vive junto a este módulo, bajo el mismo almacén y cliente.
export default function RouteLink({ statuses, cust, className = "btn-secondary", children }) {
  const query = new URLSearchParams(statuses.map((s) => ["status", s]));
  if (cust) query.set("cust", cust);
  return (
    <Link to={`../routing?${query}`} relative="path" className={`inline-flex items-center gap-1.5 ${className}`}>
      {children}
    </Link>
  );
}
