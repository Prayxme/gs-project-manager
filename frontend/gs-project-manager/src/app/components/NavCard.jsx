import { Link } from "react-router-dom";

// Tarjeta de navegación (almacén, cliente o módulo).
export default function NavCard({ to, icon, title, description, badge, actionLabel }) {
  return (
    <Link to={to} className="group card p-5 flex flex-col transition hover:-translate-y-0.5 hover:border-brand/60">
      <div className="flex items-start justify-between gap-3">
        <span className="w-12 h-12 rounded-xl bg-brand-soft grid place-items-center text-2xl" aria-hidden="true">
          {icon}
        </span>
        {badge && (
          <span className="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-300">
            {badge}
          </span>
        )}
      </div>
      <h3 className="text-lg font-extrabold mt-4 text-ink">{title}</h3>
      <p className="text-sm mt-1 leading-relaxed text-muted flex-1">{description}</p>
      <span className="inline-flex items-center gap-1 text-sm font-bold mt-4 text-brand">
        {actionLabel} <span className="transition group-hover:translate-x-0.5">→</span>
      </span>
    </Link>
  );
}
