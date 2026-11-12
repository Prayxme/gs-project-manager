// Piezas de interfaz compartidas por todos los módulos (mismo aspecto en toda la app).

export function PageHeader({ title, subtitle, children }) {
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

export function Tabs({ tabs, active, onChange }) {
  return (
    <div className="border-b border-line overflow-x-auto">
      <div className="flex gap-1 min-w-max">
        {tabs.map(([id, label, count]) => (
          <button
            key={id}
            onClick={() => onChange(id)}
            className={`px-3 sm:px-4 py-2.5 text-sm font-extrabold border-b-2 -mb-px transition whitespace-nowrap ${
              active === id ? "border-brand text-brand" : "border-transparent text-muted hover:text-ink"
            }`}
          >
            {label}
            {count !== undefined && (
              <span className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-full ${active === id ? "bg-brand-soft text-brand-ink" : "bg-surface-3 text-muted"}`}>
                {count}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

const ALERT_STYLE = {
  error: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
  success: "border-brand/40 bg-brand-soft text-brand-ink",
  warning: "border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-300",
};

export function Alert({ kind = "error", children, onClose }) {
  if (!children) return null;
  return (
    <div className={`rounded-xl border px-4 py-2.5 text-sm flex items-start justify-between gap-3 ${ALERT_STYLE[kind]}`}>
      <div className="min-w-0 break-words">{children}</div>
      {onClose && (
        <button onClick={onClose} aria-label="Cerrar" className="font-bold opacity-70 hover:opacity-100 shrink-0">
          ✕
        </button>
      )}
    </div>
  );
}

export function Badge({ className = "", children }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-md text-xs font-extrabold whitespace-nowrap ${className}`}>
      {children}
    </span>
  );
}
