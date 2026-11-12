import { STATUS_ORDER } from "../../constants";
import StatusBadge from "../StatusBadge";

// Resultado de comparar un PDF de la bandeja con la hoja (o el motivo del error).
export default function InboxResult({ item, t }) {
  if (item.status === "ERROR") return <span className="text-xs text-red-600 dark:text-red-300">{item.error}</span>;
  if (!item.summary) return "—";
  return (
    <span className="flex flex-wrap gap-1">
      {STATUS_ORDER.filter((st) => item.summary[st]).map((st) => (
        <StatusBadge key={st} status={st} t={t}>{item.summary[st]} {t.status[st]}</StatusBadge>
      ))}
    </span>
  );
}
