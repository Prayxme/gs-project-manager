import { Link } from "react-router-dom";

// Almacén › Cliente › Módulo. En celular solo se ve el último nivel.
export default function Breadcrumbs({ items }) {
  return (
    <nav aria-label="breadcrumb" className="flex items-center gap-1.5 sm:gap-2 min-w-0 text-sm">
      {items.map((it, i) => {
        const ultimo = i === items.length - 1;
        return (
          <span key={it.to} className={`items-center gap-1.5 sm:gap-2 min-w-0 ${ultimo ? "flex" : "hidden md:flex"}`}>
            <span className="text-on-header-muted hidden md:inline">›</span>
            {ultimo ? (
              <span className="font-bold truncate" aria-current="page">{it.label}</span>
            ) : (
              <Link to={it.to} className="font-semibold text-on-header-muted hover:text-on-header truncate">
                {it.label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
