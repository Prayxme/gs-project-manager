import { Link } from "react-router-dom";

// Tarjeta de un módulo en la página de inicio.
export default function ModuleCard({ module, texts, comingSoonLabel, openLabel }) {
  const activo = module.status === "active";
  return (
    <Link
      to={module.path}
      className="group card p-5 flex flex-col transition hover:-translate-y-0.5 hover:border-brand/60"
    >
      <div className="flex items-start justify-between gap-3">
        <span className="w-12 h-12 rounded-xl bg-brand-soft grid place-items-center text-2xl" aria-hidden="true">
          {module.icon}
        </span>
        {!activo && (
          <span className="text-[11px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-300">
            {comingSoonLabel}
          </span>
        )}
      </div>
      <h3 className="text-lg font-extrabold mt-4 text-ink">{texts.name}</h3>
      <p className="text-sm mt-1 leading-relaxed text-muted flex-1">{texts.description}</p>
      <span className="inline-flex items-center gap-1 text-sm font-bold mt-4 text-brand">
        {openLabel} <span className="transition group-hover:translate-x-0.5">→</span>
      </span>
    </Link>
  );
}
