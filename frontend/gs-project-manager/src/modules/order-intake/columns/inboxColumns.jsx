import { Badge } from "../../../shared/components";
import { formatShortDateTime } from "../../../shared/utils/dates";
import InboxActions from "../components/inbox/InboxActions";
import InboxResult from "../components/inbox/InboxResult";
import { INBOX_STYLE } from "../constants";
import { clienteDelAsunto } from "../utils/subject";

// Columnas de la bandeja de Gmail. acciones: { revisar, descartar, restaurar }.
export const inboxColumns = (t, acciones, busy) => [
  {
    key: "status", label: t.inbox.cols.status, mobile: "title",
    render: (i) => <Badge className={INBOX_STYLE[i.status] || ""}>{t.inbox.status[i.status] || i.status}</Badge>,
  },
  {
    key: "subject", label: t.cols.store, mobile: "title",
    sortValue: (i) => clienteDelAsunto(i.subject),
    render: (i) => <span className="font-mono font-bold">{clienteDelAsunto(i.subject) || "—"}</span>,
  },
  { key: "received_at", label: t.inbox.cols.received, render: (i) => formatShortDateTime(i.received_at) },
  {
    key: "filename", label: t.inbox.cols.file, className: "min-w-[14rem]",
    render: (i) => <span className="font-mono text-xs break-all">{i.filename}</span>,
  },
  {
    key: "summary", label: t.inbox.cols.result, sortValue: (i) => i.summary?.NEW ?? -1,
    render: (i) => <InboxResult item={i} t={t} />,
  },
  {
    key: "actions", label: t.inbox.cols.actions,
    render: (i) => <InboxActions item={i} acciones={acciones} busy={busy} t={t} />,
  },
];
