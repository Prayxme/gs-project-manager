import { fmt } from "../../shared/i18n/format";
import { useTranslations } from "../../shared/settings";
import CardGridPage from "../components/CardGridPage";
import NavCard from "../components/NavCard";
import { APP_I18N } from "../i18n";
import { clientModules, clientPath } from "../routing/paths";

// /<almacén>: clientes del almacén.
export default function WarehousePage({ warehouse }) {
  const t = useTranslations(APP_I18N);
  return (
    <CardGridPage title={fmt(t.clientsTitle, { w: warehouse.name })} subtitle={t.clientsSubtitle}>
      {warehouse.clients.map((c) => (
        <NavCard
          key={c.id}
          to={clientPath(warehouse, c)}
          icon={c.icon}
          title={c.name}
          description={`${t.clients[c.id] || ""} ${fmt(t.modulesCount, { n: clientModules(c).length })}`}
          actionLabel={t.open}
        />
      ))}
    </CardGridPage>
  );
}
