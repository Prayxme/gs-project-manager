import { EDITABLE_FIELDS, FULL_WIDTH_MOBILE } from "../../constants";
import StatusBadge from "../StatusBadge";
import { EditableField, RowNotes, SelectCheckbox } from "./RowParts";

// Celular: una tarjeta por PikTik.
export default function ReviewCards({ review, t }) {
  return (
    <div className="md:hidden space-y-3">
      {review.rows.map((r) => (
        <div key={r.piktik} className={`card p-3.5 space-y-3 ${r.status === "REGISTERED" ? "opacity-70" : ""}`}>
          <div className="flex items-center gap-2.5">
            <SelectCheckbox row={r} review={review} />
            <span className="font-mono font-black text-ink">PT {r.piktik}</span>
            <StatusBadge status={r.status} t={t} />
            <span className={`ml-auto text-sm font-bold ${r.received === "Yes" ? "text-brand" : "text-muted"}`}>
              {t.cols.received}: {r.received}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {EDITABLE_FIELDS.map((e) => (
              <label key={e.key} className={FULL_WIDTH_MOBILE.has(e.key) ? "col-span-2" : ""}>
                <span className="label">{t.cols[e.col]}</span>
                <EditableField row={r} field={e} review={review} />
              </label>
            ))}
          </div>
          {(r.diffs.length > 0 || r.warnings.length > 0) && (
            <div className="text-xs space-y-0.5"><RowNotes row={r} /></div>
          )}
        </div>
      ))}
    </div>
  );
}
