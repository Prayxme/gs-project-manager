import { DataTable } from "../../../shared/components";
import { formatShortDateTime } from "../../../shared/utils/dates";
import { inboxColumns } from "../columns/inboxColumns";

// Pestaña "Bandeja Gmail": PDFs de Pick Tickets recibidos, pendientes de aprobación.
export default function InboxTab({ inbox, onReview, busy, t }) {
  const { items, lastCheck, showAll, setShowAll, revisarAhora, descartar, restaurar } = inbox;
  const ultima = lastCheck?.at ? formatShortDateTime(lastCheck.at) : t.inbox.never;

  return (
    <div className="space-y-3">
      <p className="text-sm max-w-3xl text-muted">{t.inbox.intro}</p>
      <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-4">
        <button className="btn-primary" disabled={!!busy} onClick={revisarAhora}>
          {busy === t.inbox.checking ? t.inbox.checking : t.inbox.checkNow}
        </button>
        <span className="text-sm text-muted">
          {t.inbox.lastCheck}: {ultima}
          {lastCheck?.ok === false && <span className="text-red-600 dark:text-red-300"> · {lastCheck.error}</span>}
        </span>
        <label className="flex items-center gap-2 text-sm font-bold text-ink select-none sm:ml-auto">
          <input type="checkbox" className="w-4 h-4 accent-[var(--brand)]" checked={showAll}
            onChange={(e) => setShowAll(e.target.checked)} />
          {t.inbox.showAll}
        </label>
      </div>
      <DataTable
        columns={inboxColumns(t, { revisar: onReview, descartar, restaurar }, busy)}
        rows={items}
        rowKey={(i) => i.id}
        emptyText={t.inbox.empty}
      />
    </div>
  );
}
