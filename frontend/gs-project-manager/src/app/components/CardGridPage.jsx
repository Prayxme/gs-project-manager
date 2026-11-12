// Página de selección: título, subtítulo y una cuadrícula de tarjetas.
export default function CardGridPage({ title, subtitle, children }) {
  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-10">
        <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-ink">{title}</h2>
        {subtitle && <p className="text-sm mt-1 text-muted">{subtitle}</p>}
        <div className="grid gap-4 mt-6 sm:mt-8 sm:grid-cols-2 lg:grid-cols-3">{children}</div>
      </div>
    </div>
  );
}
