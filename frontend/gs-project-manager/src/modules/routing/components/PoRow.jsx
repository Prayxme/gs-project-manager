import { CopyValue } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";

// Una PO dentro del RTS: cada valor se copia con un clic para transcribirlo al portal de routing.
export default function PoRow({ po, t }) {
  const ajustado = po.weight_adjusted_from !== undefined;
  return (
    <>
      <tr className="border-t border-line align-top">
        <td className="py-1.5 pr-2"><CopyValue value={po.po} /></td>
        <td className="py-1.5 pr-2">
          <div className="flex flex-col items-start">
            {po.piktiks.map((pk) => <CopyValue key={pk} value={pk} className="font-semibold text-ink-2" />)}
          </div>
        </td>
        <td className="py-1.5 pr-2 text-xs text-muted font-bold whitespace-nowrap">{po.cust}</td>
        <td className="py-1.5 pr-2 text-right"><CopyValue value={po.units} /></td>
        <td className="py-1.5 pr-2 text-right"><CopyValue value={po.cartons} /></td>
        <td className="py-1.5 pr-2 text-right">
          <CopyValue value={po.weight} />
          {ajustado && (
            <div className="text-[11px] text-amber-700 dark:text-amber-300 font-bold whitespace-nowrap">
              {fmt(t.weightAdjusted, { w: po.weight_adjusted_from })}
            </div>
          )}
        </td>
        <td className="py-1.5 pr-2 text-right"><CopyValue value={po.cft} /></td>
        <td className="py-1.5 text-right">
          <CopyValue value={po.pallets} className="text-brand-ink" />
          <div className="text-[11px] text-muted whitespace-nowrap">{fmt(t.cols.estimated, { n: po.estimated_pallets })}</div>
        </td>
      </tr>
      {po.issues.length > 0 && (
        <tr>
          <td colSpan={8} className="pb-1.5 text-xs text-amber-700 dark:text-amber-300">⚠ {po.issues.join(" · ")}</td>
        </tr>
      )}
    </>
  );
}
