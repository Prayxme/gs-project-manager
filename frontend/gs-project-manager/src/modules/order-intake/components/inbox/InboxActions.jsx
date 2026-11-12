import { inboxPdfUrl } from "../../services/orderIntakeApi";

const BTN = "px-3 py-1 text-xs";

// Acciones de un PDF de la bandeja: revisar, ver el PDF, descartar o restaurar.
export default function InboxActions({ item, acciones, busy, t }) {
  const resuelto = item.status === "APPLIED" || item.status === "NO_CHANGES";
  return (
    <span className="flex flex-wrap items-center gap-1.5">
      {item.status !== "ERROR" && (
        <button className={`btn-primary ${BTN}`} disabled={!!busy} onClick={() => acciones.revisar(item)}>
          {t.inbox.review}
        </button>
      )}
      <a className={`btn-secondary ${BTN}`} href={inboxPdfUrl(item.id)} target="_blank" rel="noreferrer">
        {t.inbox.viewPdf}
      </a>
      {item.status === "DISMISSED" ? (
        <button className={`btn-secondary ${BTN}`} disabled={!!busy} onClick={() => acciones.restaurar(item.id)}>
          {t.inbox.restore}
        </button>
      ) : !resuelto && (
        <button className={`btn-secondary ${BTN}`} disabled={!!busy} onClick={() => acciones.descartar(item.id)}>
          {t.inbox.dismiss}
        </button>
      )}
    </span>
  );
}
