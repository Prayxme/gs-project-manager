import { Badge } from "../../../shared/components";
import { fmt } from "../../../shared/i18n/format";
import { urgency } from "../constants";
import { usDate } from "../utils/format";

// Fecha límite de routing con su urgencia (vencido / hoy / pronto).
export default function DeadlineBadge({ deadline, daysLeft, t }) {
  const u = urgency(daysLeft);
  return (
    <span className="inline-flex items-center gap-1.5 text-xs">
      <span className="text-muted font-bold">{t.deadline}</span>
      <span className="font-extrabold text-ink">{usDate(deadline)}</span>
      {u.key && <Badge className={u.style}>{fmt(t.days[u.key], { n: Math.abs(daysLeft) })}</Badge>}
    </span>
  );
}
