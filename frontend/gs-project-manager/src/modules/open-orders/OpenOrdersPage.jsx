import { useState } from "react";
import { Alert, DataTable, FileButton, InfoPanel, PageHeader, Tabs } from "../../shared/components";
import { useTranslations } from "../../shared/settings";
import { formatShortDateTime } from "../../shared/utils/dates";
import { activeColumns } from "./columns/activeColumns";
import { closedColumns } from "./columns/closedColumns";
import { eventColumns } from "./columns/eventColumns";
import CaliforniaClock from "./components/CaliforniaClock";
import KpiBar from "./components/KpiBar";
import OrderFiltersBar from "./components/OrderFiltersBar";
import RefreshControls from "./components/RefreshControls";
import RouteUrgentLink from "./components/RouteUrgentLink";
import StatusSections from "./components/StatusSections";
import { I18N, rowStyle } from "./constants";
import { useOpenOrdersData } from "./hooks/useOpenOrdersData";
import { useOrderFilters } from "./hooks/useOrderFilters";

export default function OpenOrdersPage() {
  const t = useTranslations(I18N);
  const [tab, setTab] = useState("groups");
  const data = useOpenOrdersData(tab, t);
  const filters = useOrderFilters(data.orders);
  const { summary, error, setError } = data;

  // Al pulsar un KPI de estado se filtran las órdenes activas (por secciones o en lista).
  const alternarEstado = (s) => {
    if (tab !== "groups") setTab("active");
    filters.alternarEstado(s);
  };

  const ultima = summary?.last_success_at;
  const ultimaFallo = summary?.last_run && !summary.last_run.ok ? summary.last_run.error : "";

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1800px] mx-auto px-3 sm:px-5 py-4 sm:py-5 space-y-4">
        <PageHeader title={t.title} subtitle={`${t.lastUpdate}: ${ultima ? formatShortDateTime(ultima) : t.never}`}>
          <CaliforniaClock label={t.caTime} />
          <RouteUrgentLink summary={summary} t={t} />
          <RefreshControls
            summary={summary}
            refrescando={data.refrescando}
            onToggleAuto={data.alternarAuto}
            onRefresh={data.actualizarAhora}
            t={t}
          />
        </PageHeader>

        <Alert onClose={error ? () => setError("") : undefined}>
          {(error || ultimaFallo) && `${t.errorPrefix}: ${error || ultimaFallo}`}
        </Alert>
        <Alert kind="success" onClose={() => data.setAviso("")}>{data.aviso}</Alert>

        <InfoPanel id="open-orders" title={t.info.title} sections={t.info.sections} />

        <KpiBar summary={summary} t={t} statusFilter={filters.statusFilter} onToggleStatus={alternarEstado} />

        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            ["groups", t.tabs.groups, data.orders.length], ["active", t.tabs.active],
            ["events", t.tabs.events], ["closed", t.tabs.closed],
          ]}
        />

        {tab === "groups" && (
          <>
            <OrderFiltersBar filters={filters} total={data.orders.length} t={t} />
            <StatusSections orders={filters.filtradas} t={t} />
          </>
        )}

        {tab === "active" && (
          <>
            <OrderFiltersBar filters={filters} total={data.orders.length} t={t} />
            <DataTable
              columns={activeColumns(t)}
              rows={filters.filtradas}
              rowKey={(o) => o.pick_ticket}
              rowClassName={rowStyle}
              emptyText={t.noData}
            />
          </>
        )}

        {tab === "events" && (
          <DataTable columns={eventColumns(t)} rows={data.events} rowKey={(e) => e.id} emptyText="—" />
        )}

        {tab === "closed" && (
          <>
            <div className="flex justify-end">
              <FileButton accept=".csv" onFiles={([file]) => data.importarCsv(file)}>📥 {t.importCsv}</FileButton>
            </div>
            <DataTable columns={closedColumns(t)} rows={data.closed} rowKey={(c) => c.pick_ticket} emptyText="—" />
          </>
        )}
      </div>
    </div>
  );
}
