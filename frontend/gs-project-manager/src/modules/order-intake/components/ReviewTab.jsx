import { Alert } from "../../../shared/components";
import ReviewActions from "./review/ReviewActions";
import ReviewCards from "./review/ReviewCards";
import ReviewTable from "./review/ReviewTable";
import UploadPanel from "./UploadPanel";

// Pestaña "Revisar PDF": subir, revisar/corregir y escribir en la hoja.
export default function ReviewTab({ review, busy, t }) {
  return (
    <>
      <UploadPanel review={review} busy={busy} t={t} />

      {review.pdfWarnings.length > 0 && (
        <Alert kind="warning">
          <p className="font-extrabold">{t.pdfWarn}</p>
          {review.pdfWarnings.map((w, i) => <p key={i}>• {w}</p>)}
        </Alert>
      )}

      {review.rows.length > 0 && (
        <>
          <ReviewTable review={review} t={t} />
          <ReviewCards review={review} t={t} />
          <ReviewActions review={review} busy={busy} t={t} />
        </>
      )}
    </>
  );
}
