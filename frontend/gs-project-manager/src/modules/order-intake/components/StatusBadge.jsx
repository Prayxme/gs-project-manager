import { Badge } from "../../../shared/components";
import { STATUS_STYLE } from "../constants";

// Estado de un PikTik (NEW / REVISION / REGISTERED) con su color.
export default function StatusBadge({ status, t, children }) {
  return <Badge className={STATUS_STYLE[status]}>{children ?? t.status[status]}</Badge>;
}
