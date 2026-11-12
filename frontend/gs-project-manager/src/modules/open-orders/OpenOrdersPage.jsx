import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useAppSettings } from "../../app/AppSettings";
import DataTable from "../../shared/components/DataTable";
import { Alert, Badge, PageHeader, Tabs } from "../../shared/components/ui";
import CaliforniaClock from "./components/CaliforniaClock";
import KpiBar from "./components/KpiBar";
import { AUTO_REFRESH_POLL_MS, CLOSED_STYLE, I18N, STATUS_STYLE, fmt } from "./constants";
import {
  getClosed, getEvents, getOrders, getSummary, importCompletedCsv, refreshNow, setAutoRefresh,
} from "./services/openOrdersApi";

const isoAMdy = (iso) => (iso ? `${iso.slice(5, 7)}/${iso.slice(8, 10)}/${iso.slice(2, 4)}` : "");
const utcALocal = (ts) =>
  ts ? new Date(ts).toLocaleString(undefined, { dateStyle: "short", timeStyle: "short" }) : "";
const mdyOrdenable = (mdy) => (mdy && mdy !== "00/00/00" ? `${mdy.slice(6)}${mdy.slice(0, 2)}${mdy.slice(3, 5)}` : "");
const limpiarFecha = (mdy) => (mdy === "00/00/00" ? "" : mdy);

export default function OpenOrdersPage() {
  const { lang } = useAppSettings();
  const t = I18N[lang];

  const [tab, setTab] = useState("active");
  const [orders, setOrders] = useState([]);
  const [summary, setSummary] = useState(null);
  const [events, setEvents] = useState([]);
  const [closed, setClosed] = useState([]);
  const [refrescando, setRefrescando] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const [q, setQ] = useState("");
  const [statusFilter, setStatusFilter] = useState([]);
  const [cliente, setCliente] = useState("");
  const [soloPendientes, setSoloPendientes] = useState(false);
  const csvRef = useRef(null);

  // El estado solo se actualiza al llegar la respuesta (nunca de forma síncrona dentro de un efecto).
  const cargarActivas = useCallback(
    () =>
      Promise.all([getOrders(), getSummary()])
        .then(([o, s]) => {
          setOrders(o.orders);
          setSummary(s);
          setError("");
        })
        .catch((e) => setError(e.message)),
    []
  );

  const cargarTab = useCallback((cual) => {
    const peticion =
      cual === "events" ? getEvents(1000).then((r) => setEvents(r.events))
      : cual === "closed" ? getClosed().then((r) => setClosed(r.closed))
      : Promise.resolve();
    return peticion.catch((e) => setError(e.message));
  }, []);

  // Carga inicial y relectura periódica de la base (la actualización automática corre en el backend).
  useEffect(() => {
    const id = setInterval(cargarActivas, AUTO_REFRESH_POLL_MS);
    const primera = setTimeout(cargarActivas, 0);
    return () => {
      clearInterval(id);
      clearTimeout(primera);
    };
  }, [cargarActivas]);

  useEffect(() => {
    const id = setTimeout(() => cargarTab(tab), 0);
    return () => clearTimeout(id);
  }, [tab, cargarTab]);

  const actualizarAhora = async () => {
    setRefrescando(true);
    setAviso("");
    try {
      const r = await refreshNow();
      setAviso(
        r.new || r.changed || r.removed
          ? fmt(t.refreshDone, { total: r.total, n: r.new, c: r.changed, r: r.removed })
          : fmt(t.refreshNoChanges, { total: r.total })
      );
      await cargarActivas();
      await cargarTab(tab);
    } catch (e) {
      setError(e.message);
    } finally {
      setRefrescando(false);
    }
  };

  const alternarAuto = async () => {
    try {
      await setAutoRefresh(!summary?.auto_refresh);
      await cargarActivas();
    } catch (e) {
      setError(e.message);
    }
  };

  const importarCsv = async (ev) => {
    const file = ev.target.files?.[0];
    ev.target.value = null;
    if (!file) return;
    try {
      const r = await importCompletedCsv(file);
      setAviso(fmt(t.importDone, { i: r.inserted, d: r.duplicates, x: r.invalid }));
      await cargarTab("closed");
      await cargarActivas();
    } catch (e) {
      setError(e.message);
    }
  };

  const alternarEstado = (s) => {
    setTab("active");
    setStatusFilter((prev) => (prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]));
  };

  const clientes = useMemo(() => [...new Set(orders.map((o) => o.customer_code))].sort(), [orders]);

  const filtradas = useMemo(() => {
    const texto = q.trim().toLowerCase();
    return orders.filter((o) => {
      if (statusFilter.length && !statusFilter.includes(o.status)) return false;
      if (cliente && o.customer_code !== cliente) return false;
      if (soloPendientes && o.status === "ROUTED") return false;
      if (!texto) return true;
      return [o.pick_ticket, o.po, o.cust, o.cfrm_number, o.notes, o.ship_to]
        .some((v) => (v || "").toLowerCase().includes(texto));
    });
  }, [orders, q, statusFilter, cliente, soloPendientes]);

  const columnasActivas = [
    {
      key: "priority_rank", label: t.cols.status, mobile: "title",
      render: (o) => <Badge className={STATUS_STYLE[o.status]?.badge || ""}>{o.status || "—"}</Badge>,
    },
    {
      key: "days_remaining", label: t.cols.days, mobile: "title",
      render: (o) =>
        o.status === "ROUTED" ? <span className="text-brand font-bold">✔</span>
        : <span className="font-mono font-bold">{o.days_remaining} d</span>,
    },
    {
      key: "pick_ticket", label: t.cols.pickTicket, mobile: "title",
      render: (o) => <span className="font-mono font-bold">PT {o.pick_ticket}</span>,
    },
    {
      key: "routing_deadline", label: t.cols.deadline,
      render: (o) => (
        <span title={o.routing_earliest ? `${t.window}: ${isoAMdy(o.routing_earliest)}` : undefined}>
          {isoAMdy(o.routing_deadline)}
        </span>
      ),
    },
    { key: "po", label: t.cols.po, render: (o) => <span className="font-mono font-bold">{o.po}</span> },
    { key: "cust", label: t.cols.customer },
    { key: "ship_date", label: t.cols.shipDate, sortValue: (o) => mdyOrdenable(o.ship_date) },
    { key: "cancel_date", label: t.cols.cancelDate, sortValue: (o) => mdyOrdenable(o.cancel_date) },
    {
      key: "cfrm_number", label: t.cols.cfrm,
      render: (o) =>
        o.cfrm_number ? (
          <span>
            <span className="font-mono">{o.cfrm_number}</span>
            <span className="ml-1.5 text-[11px] text-muted">({t.cfrmType[o.cfrm_type] || ""})</span>
          </span>
        ) : "",
    },
    {
      key: "appt_date", label: t.cols.appt, sortValue: (o) => mdyOrdenable(o.appt_date),
      render: (o) => `${limpiarFecha(o.appt_date)} ${o.appt_time || ""}`.trim(),
    },
    { key: "ctns", label: t.cols.ctns, sortValue: (o) => Number(o.ctns) || 0 },
    { key: "notes", label: t.cols.notes, className: "min-w-[12rem]" },
    {
      key: "last_change_at", label: t.cols.lastChange,
      render: (o) =>
        o.last_change ? (
          <span>
            <span className="font-bold">{o.last_change}</span>
            <span className="block text-[11px] text-muted">{utcALocal(o.last_change_at)}</span>
          </span>
        ) : "",
    },
  ];

  const columnasEventos = [
    { key: "event", label: t.cols.event, mobile: "title", render: (e) => <span className="font-bold">{e.event}</span> },
    { key: "ts", label: t.cols.when, render: (e) => utcALocal(e.ts) },
    { key: "pick_ticket", label: t.cols.pickTicket, render: (e) => <span className="font-mono">{e.pick_ticket}</span> },
    { key: "po", label: t.cols.po, render: (e) => <span className="font-mono">{e.po}</span> },
    { key: "cust", label: t.cols.customer },
    { key: "old_value", label: t.cols.old },
    { key: "new_value", label: t.cols.new },
  ];

  const columnasCerradas = [
    {
      key: "final_status", label: t.cols.finalStatus, mobile: "title",
      render: (c) => <Badge className={CLOSED_STYLE[c.final_status] || ""}>{c.final_status}</Badge>,
    },
    { key: "pick_ticket", label: t.cols.pickTicket, mobile: "title", render: (c) => <span className="font-mono font-bold">PT {c.pick_ticket}</span> },
    { key: "date_removed", label: t.cols.dateRemoved },
    { key: "reason", label: t.cols.reason },
    { key: "po", label: t.cols.po, render: (c) => <span className="font-mono font-bold">{c.po}</span> },
    { key: "cust", label: t.cols.customer },
    { key: "ship_date", label: t.cols.shipDate, sortValue: (c) => mdyOrdenable(c.ship_date) },
    { key: "cancel_date", label: t.cols.cancelDate, sortValue: (c) => mdyOrdenable(c.cancel_date) },
    { key: "cfrm_number", label: t.cols.cfrm, render: (c) => <span className="font-mono">{c.cfrm_number}</span> },
    { key: "appt_date", label: t.cols.appt, render: (c) => limpiarFecha(c.appt_date) },
    { key: "notes", label: t.cols.notes, className: "min-w-[10rem]" },
    { key: "source", label: t.cols.source, mobile: "hidden" },
  ];

  const ultima = summary?.last_success_at;
  const ultimaFallo = summary?.last_run && !summary.last_run.ok ? summary.last_run.error : "";
  const hayFiltros = q || cliente || soloPendientes || statusFilter.length > 0;

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1800px] mx-auto px-3 sm:px-5 py-4 sm:py-5 space-y-4">
        <PageHeader
          title={t.title}
          subtitle={`${t.lastUpdate}: ${ultima ? utcALocal(ultima) : t.never}`}
        >
          <CaliforniaClock label={t.caTime} />
          <label className="flex items-center gap-2 text-sm font-bold text-ink cursor-pointer select-none">
            <input
              type="checkbox"
              className="w-4 h-4 accent-[var(--brand)]"
              checked={!!summary?.auto_refresh}
              onChange={alternarAuto}
            />
            {fmt(t.auto, { n: summary?.auto_refresh_minutes ?? 5 })}
          </label>
          <button onClick={actualizarAhora} disabled={refrescando} className="btn-primary">
            {refrescando ? t.updating : `🔄 ${t.updateNow}`}
          </button>
        </PageHeader>

        <Alert onClose={error ? () => setError("") : undefined}>
          {(error || ultimaFallo) && `${t.errorPrefix}: ${error || ultimaFallo}`}
        </Alert>
        <Alert kind="success" onClose={() => setAviso("")}>{aviso}</Alert>

        <KpiBar summary={summary} t={t} statusFilter={statusFilter} onToggleStatus={alternarEstado} />

        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[["active", t.tabs.active, orders.length], ["events", t.tabs.events], ["closed", t.tabs.closed]]}
        />

        {tab === "active" && (
          <>
            <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-2 sm:gap-3">
              <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={t.search} className="input sm:flex-1 sm:min-w-[16rem]" />
              <div className="flex gap-2">
                <select value={cliente} onChange={(e) => setCliente(e.target.value)} className="input w-auto flex-1 sm:flex-none">
                  <option value="">{t.allCustomers}</option>
                  {clientes.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
                {hayFiltros && (
                  <button
                    className="btn-secondary"
                    onClick={() => { setQ(""); setCliente(""); setSoloPendientes(false); setStatusFilter([]); }}
                  >
                    {t.clearFilters}
                  </button>
                )}
              </div>
              <label className="flex items-center gap-2 text-sm font-bold text-ink select-none">
                <input type="checkbox" className="w-4 h-4 accent-[var(--brand)]" checked={soloPendientes}
                  onChange={(e) => setSoloPendientes(e.target.checked)} />
                {t.pendingOnly}
              </label>
              <span className="text-sm text-muted sm:ml-auto">{fmt(t.showing, { n: filtradas.length, t: orders.length })}</span>
            </div>
            <DataTable
              columns={columnasActivas}
              rows={filtradas}
              rowKey={(o) => o.pick_ticket}
              rowClassName={(o) =>
                o.customer_code === "BURL" && o.status === "SAFE" ? "bg-sky-500/[0.07]" : STATUS_STYLE[o.status]?.row || ""
              }
              emptyText={t.noData}
            />
          </>
        )}

        {tab === "events" && (
          <DataTable columns={columnasEventos} rows={events} rowKey={(e) => e.id} emptyText="—" />
        )}

        {tab === "closed" && (
          <>
            <div className="flex justify-end">
              <input ref={csvRef} type="file" accept=".csv" className="hidden" onChange={importarCsv} />
              <button className="btn-secondary" onClick={() => csvRef.current?.click()}>📥 {t.importCsv}</button>
            </div>
            <DataTable columns={columnasCerradas} rows={closed} rowKey={(c) => c.pick_ticket} emptyText="—" />
          </>
        )}
      </div>
    </div>
  );
}
