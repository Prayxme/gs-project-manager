import { fmt } from "../../shared/i18n/format";
import { useTranslations } from "../../shared/settings";
import CardGridPage from "../components/CardGridPage";
import NavCard from "../components/NavCard";
import { APP_I18N } from "../i18n";
import { clientModules, modulePath } from "../routing/paths";

// /<almacén>/<cliente>: herramientas habilitadas para el cliente.
export default function ClientPage({ warehouse, client }) {
  const t = useTranslations(APP_I18N);
  return (
    <CardGridPage title={fmt(t.modulesTitle, { c: client.name, w: warehouse.name })} subtitle={t.modulesSubtitle}>
      {clientModules(client).map((m) => (
        <NavCard
          key={m.id}
          to={modulePath(warehouse, client, m)}
          icon={m.icon}
          title={t.modules[m.id].name}
          description={t.modules[m.id].description}
          badge={m.status === "active" ? null : t.comingSoon}
          actionLabel={t.open}
        />
      ))}
    </CardGridPage>
  );
}
