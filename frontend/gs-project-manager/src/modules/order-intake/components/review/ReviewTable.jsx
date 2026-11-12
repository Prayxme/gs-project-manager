import { EDITABLE_FIELDS } from "../../constants";
import StatusBadge from "../StatusBadge";
import { EditableField, RowNotes, SelectCheckbox } from "./RowParts";

const COLUMNAS = ["sel", "status", "piktik", ...EDITABLE_FIELDS.map((e) => e.col), "received", "changes"];

// Escritorio: tabla editable.
export default function ReviewTable({ review, t }) {
  return (
    <div className="hidden md:block overflow-auto rounded-xl border border-line bg-surface shadow-card max-h-[65vh]">
      <table className="w-full text-sm">
        <thead className="sticky top-0 z-10 bg-surface-2 text-muted">
          <tr>
            {COLUMNAS.map((c) => (
              <th key={c} className="px-2 py-2.5 text-left text-xs font-extrabold uppercase whitespace-nowrap border-b border-line">
                {t.cols[c]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {review.rows.map((r) => (
            <tr key={r.piktik} className={`border-t border-line ${r.status === "REGISTERED" ? "opacity-60" : ""}`}>
              <td className="px-2 py-1.5"><SelectCheckbox row={r} review={review} /></td>
              <td className="px-2 py-1.5"><StatusBadge status={r.status} t={t} /></td>
              <td className="px-2 py-1.5 font-mono font-bold text-ink">
                {r.piktik}
                {r.sheet_row && <span className="block text-[11px] font-normal text-muted">{t.cols.row} {r.sheet_row}</span>}
              </td>
              {EDITABLE_FIELDS.map((e) => (
                <td key={e.key} className="px-1 py-1">
                  <EditableField row={r} field={e} review={review} className={e.w} />
                </td>
              ))}
              <td className={`px-2 py-1.5 font-bold ${r.received === "Yes" ? "text-brand" : "text-ink"}`}>{r.received}</td>
              <td className="px-2 py-1.5 text-xs min-w-[14rem]"><RowNotes row={r} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
