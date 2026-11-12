import { fmt } from "../../../shared/i18n/format";

// Barra de filtros de las órdenes activas (estado en useOrderFilters).
export default function OrderFiltersBar({ filters, total, t }) {
  const { q, setQ, cliente, setCliente, clientes, soloPendientes, setSoloPendientes, hayFiltros, limpiar, filtradas } = filters;
  return (
    <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-3">
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t.search} className="input sm:flex-1 sm:min-w-[16rem]" />
      <div className="flex gap-2">
        <select value={cliente} onChange={(e) => setCliente(e.target.value)} className="input w-auto flex-1 sm:flex-none">
          <option value="">{t.allCustomers}</option>
          {clientes.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>
        {hayFiltros && (
          <button className="btn-secondary" onClick={limpiar}>
            {t.clearFilters}
          </button>
        )}
      </div>
      <label className="flex items-center gap-2 text-sm font-bold text-ink select-none">
        <input type="checkbox" className="w-4 h-4 accent-[var(--brand)]" checked={soloPendientes}
          onChange={(e) => setSoloPendientes(e.target.checked)} />
        {t.pendingOnly}
      </label>
      <span className="text-sm text-muted sm:ml-auto">{fmt(t.showing, { n: filtradas.length, t: total })}</span>
    </div>
  );
}
