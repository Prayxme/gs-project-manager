import { FileButton } from "../../../shared/components";
import { STATUS_ORDER } from "../constants";
import StatusBadge from "./StatusBadge";

// Botón de subida + archivos cargados y conteo por estado.
export default function UploadPanel({ review, busy, t }) {
  const { rows, files, subir, conteo } = review;
  return (
    <div className="card p-4 flex flex-col sm:flex-row sm:items-center gap-3">
      <FileButton accept=".pdf" multiple onFiles={subir} disabled={!!busy} className="btn-primary w-full sm:w-auto">
        {t.upload}
      </FileButton>
      <div className="text-sm min-w-0">
        {busy ? (
          <span className="font-bold text-muted animate-pulse">{busy}</span>
        ) : rows.length > 0 ? (
          <>
            <p className="font-bold text-ink truncate">{files.join(", ")}</p>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {STATUS_ORDER.map((st) => (
                <StatusBadge key={st} status={st} t={t}>{conteo(st)} {t.status[st]}</StatusBadge>
              ))}
            </div>
          </>
        ) : (
          <span className="text-muted">{t.empty}</span>
        )}
      </div>
    </div>
  );
}
