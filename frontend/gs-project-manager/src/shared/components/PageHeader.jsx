// Título y subtítulo de una página, con acciones a la derecha (children).
export default function PageHeader({ title, subtitle, children }) {
  return (
    <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
      <div className="min-w-0">
        <h2 className="text-xl sm:text-2xl font-black tracking-tight text-ink">{title}</h2>
        {subtitle && <p className="text-sm text-muted mt-0.5 max-w-3xl">{subtitle}</p>}
      </div>
      {children && <div className="flex flex-wrap items-center gap-2 sm:gap-3">{children}</div>}
    </div>
  );
}
