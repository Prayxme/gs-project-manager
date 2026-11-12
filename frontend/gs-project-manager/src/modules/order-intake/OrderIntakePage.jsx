import { useRef, useState } from "react";
import { useAppSettings } from "../../app/AppSettings";
import DataTable from "../../shared/components/DataTable";
import { Alert, Badge, PageHeader, Tabs } from "../../shared/components/ui";
import { I18N, STATUS_STYLE, fmt } from "./constants";
import {
  aOrden, analyzePdf, applyOrders, checkOrders, getLog, getSuggestions,
} from "./services/orderIntakeApi";

const EDITABLES = [
  { key: "company", col: "company", w: "md:w-36" },
  { key: "store", col: "store", w: "md:w-24" },
  { key: "po", col: "po", w: "md:w-28" },
  { key: "containers", col: "containers", w: "md:w-56" },
  { key: "ship_date", col: "ship", w: "md:w-28" },
  { key: "cancel_date", col: "cancel", w: "md:w-28" },
  { key: "ctns", col: "ctns", w: "md:w-20", type: "number" },
];

const seleccionInicial = (orders) => new Set(orders.filter((o) => o.status !== "REGISTERED").map((o) => o.piktik));

export default function OrderIntakePage() {
  const { lang } = useAppSettings();
  const t = I18N[lang];

  const [tab, setTab] = useState("review");
  const [rows, setRows] = useState([]);
  const [selected, setSelected] = useState(new Set());
  const [files, setFiles] = useState([]);
  const [pdfWarnings, setPdfWarnings] = useState([]);
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [suggestions, setSuggestions] = useState(null);
  const [log, setLog] = useState(null);
  const inputRef = useRef(null);

  const subir = async (ev) => {
    const lista = Array.from(ev.target.files || []);
    ev.target.value = null;
    if (!lista.length) return;
    setBusy(t.reading);
    setError("");
    setNotice("");
    try {
      const porPiktik = new Map();
      const avisos = [];
      for (const f of lista) {
        const r = await analyzePdf(f);
        r.orders.forEach((o) => porPiktik.set(o.piktik, o));
        r.pdf_warnings.forEach((w) => avisos.push(`${f.name}: ${w}`));
      }
      const orders = [...porPiktik.values()];
      setRows(orders);
      setSelected(seleccionInicial(orders));
      setFiles(lista.map((f) => f.name));
      setPdfWarnings(avisos);
      setDirty(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  };

  const editar = (piktik, key, valor) => {
    setRows((prev) =>
      prev.map((r) =>
        r.piktik === piktik
          ? { ...r, [key]: key === "containers" ? valor.split(/[\s,]+/).filter(Boolean) : valor }
          : r
      )
    );
    setDirty(true);
  };

  const verificar = async () => {
    setBusy(t.reading);
    setError("");
    try {
      const r = await checkOrders(rows.map(aOrden));
      setRows(r.orders);
      setSelected(seleccionInicial(r.orders));
      setDirty(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  };

  const aEscribir = rows.filter((r) => selected.has(r.piktik) && r.status !== "REGISTERED");
  const nNuevas = aEscribir.filter((r) => r.status === "NEW").length;
  const nRev = aEscribir.length - nNuevas;

  const escribir = async () => {
    if (!aEscribir.length) {
      setError(t.nothing);
      return;
    }
    if (!window.confirm(fmt(t.confirm, { n: nNuevas, r: nRev }))) return;
    setBusy(t.writing);
    setError("");
    try {
      const r = await applyOrders(aEscribir.map(aOrden), files.join(", "));
      setNotice(fmt(t.done, { n: r.written.length, r: r.revised.length, u: r.unchanged.length }));
      const again = await checkOrders(rows.map(aOrden));
      setRows(again.orders);
      setSelected(seleccionInicial(again.orders));
      setLog(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  };

  const cargarSugerencias = async () => {
    setBusy(t.reading);
    setError("");
    try {
      setSuggestions((await getSuggestions()).suggestions);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  };

  const abrirTab = async (id) => {
    setTab(id);
    if (id === "log" && log === null) {
      try {
        setLog((await getLog()).log);
      } catch (e) {
        setError(e.message);
      }
    }
  };

  const alternar = (pt) =>
    setSelected((prev) => {
      const s = new Set(prev);
      if (s.has(pt)) s.delete(pt);
      else s.add(pt);
      return s;
    });

  const conteo = (st) => rows.filter((r) => r.status === st).length;
  const badge = (st) => <Badge className={STATUS_STYLE[st]}>{t.status[st]}</Badge>;

  const campo = (r, e, extra = "") => (
    <input
      type={e.type || "text"}
      inputMode={e.type === "number" ? "numeric" : undefined}
      value={e.key === "containers" ? r.containers.join(" ") : r[e.key]}
      onChange={(ev) => editar(r.piktik, e.key, ev.target.value)}
      className={`input font-mono py-1.5 ${extra}`}
    />
  );

  const notas = (r) => (
    <>
      {r.diffs.map((d) => (
        <p key={d.col} className="font-bold text-amber-700 dark:text-amber-300">
          {d.campo}: {d.antes || "—"} → {d.ahora}
        </p>
      ))}
      {r.warnings.map((w, i) => <p key={i} className="text-muted">⚠ {w}</p>)}
    </>
  );

  const casilla = (r) => (
    <input
      type="checkbox"
      className="w-5 h-5 md:w-4 md:h-4 accent-[var(--brand)]"
      disabled={r.status === "REGISTERED"}
      checked={selected.has(r.piktik)}
      onChange={() => alternar(r.piktik)}
      aria-label={`PikTik ${r.piktik}`}
    />
  );

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1800px] mx-auto px-3 sm:px-5 py-4 sm:py-5 space-y-4 pb-28 md:pb-5">
        <PageHeader title={t.title} subtitle={t.subtitle} />

        <Alert onClose={() => setError("")}>{error}</Alert>
        <Alert kind="success" onClose={() => setNotice("")}>{notice}</Alert>

        <Tabs
          active={tab}
          onChange={abrirTab}
          tabs={[["review", t.tabs.review], ["suggestions", t.tabs.suggestions], ["log", t.tabs.log]]}
        />

        {tab === "review" && (
          <>
            <div className="card p-4 flex flex-col sm:flex-row sm:items-center gap-3">
              <input ref={inputRef} type="file" accept=".pdf" multiple className="hidden" onChange={subir} />
              <button onClick={() => inputRef.current?.click()} disabled={!!busy} className="btn-primary w-full sm:w-auto">
                {t.upload}
              </button>
              <div className="text-sm min-w-0">
                {busy ? (
                  <span className="font-bold text-muted animate-pulse">{busy}</span>
                ) : rows.length > 0 ? (
                  <>
                    <p className="font-bold text-ink truncate">{files.join(", ")}</p>
                    <div className="flex flex-wrap gap-1.5 mt-1">
                      <Badge className={STATUS_STYLE.NEW}>{conteo("NEW")} {t.status.NEW}</Badge>
                      <Badge className={STATUS_STYLE.REVISION}>{conteo("REVISION")} {t.status.REVISION}</Badge>
                      <Badge className={STATUS_STYLE.REGISTERED}>{conteo("REGISTERED")} {t.status.REGISTERED}</Badge>
                    </div>
                  </>
                ) : (
                  <span className="text-muted">{t.empty}</span>
                )}
              </div>
            </div>

            {pdfWarnings.length > 0 && (
              <Alert kind="warning">
                <p className="font-extrabold">{t.pdfWarn}</p>
                {pdfWarnings.map((w, i) => <p key={i}>• {w}</p>)}
              </Alert>
            )}

            {rows.length > 0 && (
              <>
                {/* Escritorio: tabla editable */}
                <div className="hidden md:block overflow-auto rounded-xl border border-line bg-surface shadow-card max-h-[65vh]">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 z-10 bg-surface-2 text-muted">
                      <tr>
                        {["sel", "status", "piktik", ...EDITABLES.map((e) => e.col), "received", "changes"].map((c) => (
                          <th key={c} className="px-2 py-2.5 text-left text-xs font-extrabold uppercase whitespace-nowrap border-b border-line">
                            {t.cols[c]}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((r) => (
                        <tr key={r.piktik} className={`border-t border-line ${r.status === "REGISTERED" ? "opacity-60" : ""}`}>
                          <td className="px-2 py-1.5">{casilla(r)}</td>
                          <td className="px-2 py-1.5">{badge(r.status)}</td>
                          <td className="px-2 py-1.5 font-mono font-bold text-ink">
                            {r.piktik}
                            {r.sheet_row && <span className="block text-[11px] font-normal text-muted">{t.cols.row} {r.sheet_row}</span>}
                          </td>
                          {EDITABLES.map((e) => (
                            <td key={e.key} className="px-1 py-1">{campo(r, e, e.w)}</td>
                          ))}
                          <td className={`px-2 py-1.5 font-bold ${r.received === "Yes" ? "text-brand" : "text-ink"}`}>{r.received}</td>
                          <td className="px-2 py-1.5 text-xs min-w-[14rem]">{notas(r)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Celular: una tarjeta por PikTik */}
                <div className="md:hidden space-y-3">
                  {rows.map((r) => (
                    <div key={r.piktik} className={`card p-3.5 space-y-3 ${r.status === "REGISTERED" ? "opacity-70" : ""}`}>
                      <div className="flex items-center gap-2.5">
                        {casilla(r)}
                        <span className="font-mono font-black text-ink">PT {r.piktik}</span>
                        {badge(r.status)}
                        <span className={`ml-auto text-sm font-bold ${r.received === "Yes" ? "text-brand" : "text-muted"}`}>
                          {t.cols.received}: {r.received}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        {EDITABLES.map((e) => (
                          <label key={e.key} className={e.key === "containers" || e.key === "company" ? "col-span-2" : ""}>
                            <span className="label">{t.cols[e.col]}</span>
                            {campo(r, e)}
                          </label>
                        ))}
                      </div>
                      {(r.diffs.length > 0 || r.warnings.length > 0) && <div className="text-xs space-y-0.5">{notas(r)}</div>}
                    </div>
                  ))}
                </div>

                {/* Acciones (fijas abajo en celular) */}
                <div className="fixed md:static bottom-0 inset-x-0 z-20 bg-surface/95 md:bg-transparent backdrop-blur border-t md:border-0 border-line p-3 md:p-0 flex flex-wrap items-center gap-2 md:gap-3">
                  {dirty && (
                    <>
                      <span className="text-sm font-bold text-amber-700 dark:text-amber-300 w-full md:w-auto">{t.edited}</span>
                      <button className="btn-secondary flex-1 md:flex-none" disabled={!!busy} onClick={verificar}>{t.recheck}</button>
                    </>
                  )}
                  <button
                    onClick={escribir}
                    disabled={!!busy || dirty || aEscribir.length === 0}
                    className="btn-primary flex-1 md:flex-none"
                  >
                    {fmt(t.write, { n: aEscribir.length })}
                  </button>
                </div>
              </>
            )}
          </>
        )}

        {tab === "suggestions" && (
          <div className="space-y-3">
            <p className="text-sm max-w-3xl text-muted">{t.sugIntro}</p>
            <button className="btn-secondary" disabled={!!busy} onClick={cargarSugerencias}>{busy || t.sugLoad}</button>
            {suggestions && (
              <DataTable
                columns={[
                  { key: "piktik", label: t.cols.piktik, mobile: "title", render: (s) => <span className="font-mono font-bold">PT {s.piktik}</span> },
                  { key: "row", label: t.cols.row },
                  { key: "containers", label: t.cols.containers, render: (s) => s.containers.join(" ") },
                ]}
                rows={suggestions}
                rowKey={(s) => s.row}
                emptyText={t.sugNone}
              />
            )}
          </div>
        )}

        {tab === "log" && (
          log === null ? (
            <p className="text-sm py-10 text-center text-muted">{t.reading}</p>
          ) : (
            <DataTable
              columns={[
                { key: "action", label: t.cols.action, mobile: "title", render: (l) => badge(l.action) },
                { key: "piktik", label: t.cols.piktik, mobile: "title", render: (l) => <span className="font-mono font-bold">PT {l.piktik}</span> },
                { key: "ts", label: t.cols.when, render: (l) => new Date(l.ts).toLocaleString() },
                { key: "po", label: t.cols.po },
                { key: "store", label: t.cols.store },
                { key: "sheet_row", label: t.cols.row },
                { key: "source_ref", label: t.cols.source, className: "min-w-[12rem]" },
              ]}
              rows={log}
              rowKey={(l) => l.id}
              emptyText={t.noLog}
            />
          )
        )}
      </div>
    </div>
  );
}
