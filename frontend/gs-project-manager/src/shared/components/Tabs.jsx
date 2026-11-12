// Pestañas: tabs = [[id, etiqueta, contador?], ...]
export default function Tabs({ tabs, active, onChange }) {
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
