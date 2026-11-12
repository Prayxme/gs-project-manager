import { fmt } from "../../shared/i18n/format";
import { useTranslations } from "../../shared/settings";
import CardGridPage from "../components/CardGridPage";
import NavCard from "../components/NavCard";
import { APP_I18N } from "../i18n";
import { WAREHOUSES } from "../registry/warehouses";
import { warehousePath } from "../routing/paths";

// Raíz (/): almacenes. Provisional hasta que exista el Home definitivo.
export default function WarehousesPage() {
  const t = useTranslations(APP_I18N);
  return (
    <CardGridPage title={t.warehousesTitle} subtitle={t.warehousesSubtitle}>
      {WAREHOUSES.map((w) => (
        <NavCard
          key={w.id}
          to={warehousePath(w)}
          icon={w.icon}
          title={w.name}
          description={`${t.warehouses[w.id] || ""} ${w.status === "active" ? fmt(t.clientsCount, { n: w.clients.length }) : ""}`}
          badge={w.status === "active" ? null : t.comingSoon}
          actionLabel={t.open}
        />
      ))}
    </CardGridPage>
  );
}
