import { useRef, useState } from "react";
import { useAppSettings } from "../../app/AppSettings";
import DataTable from "../../shared/components/DataTable";
import { I18N, STATUS_STYLE, fmt } from "./constants";
import {
  aOrden, analyzePdf, applyOrders, checkOrders, getLog, getSuggestions,
} from "./services/orderIntakeApi";

const EDITABLES = [
  { key: "company", w: "w-36" },
  { key: "store", w: "w-24" },
  { key: "po", w: "w-28" },
  { key: "containers", w: "w-56" },
  { key: "ship_date", w: "w-28", col: "ship" },
  { key: "cancel_date", w: "w-28", col: "cancel" },
  { key: "ctns", w: "w-20", type: "number" },
];

const seleccionInicial = (orders) => new Set(orders.filter((o) => o.status !== "REGISTERED").map((o) => o.piktik));

export default function OrderIntakePage() {
  const { lang, theme, isDarkMode } = useAppSettings();
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

  const borde = isDarkMode ? "border-[#1E2235]" : "border-slate-200";
  const boton = `text-sm font-bold px-3.5 py-2 rounded-lg border transition disabled:opacity-50 ${
    isDarkMode ? "border-slate-700 hover:bg-slate-800" : "border-slate-300 bg-white hover:bg-slate-50 shadow-sm"
  }`;

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
  const badge = (st) => (
    <span className={`inline-block px-2 py-0.5 rounded-md text-xs font-extrabold whitespace-nowrap ${STATUS_STYLE[st]}`}>
      {t.status[st]}
    </span>
  );

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1800px] mx-auto px-5 py-5 space-y-4">
        <div>
          <h2 className={`text-2xl font-black tracking-tight ${theme.textTitle}`}>{t.title}</h2>
          <p className={`text-sm max-w-3xl ${theme.textMuted}`}>{t.subtitle}</p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-2 text-sm text-red-600 flex justify-between gap-3">
            <span>{error}</span>
            <button onClick={() => setError("")} className="font-bold">✕</button>
          </div>
        )}
        {notice && (
          <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-700 flex justify-between">
            <span>{notice}</span>
            <button onClick={() => setNotice("")} className="font-bold">✕</button>
          </div>
        )}

        <div className={`flex gap-1 border-b ${borde}`}>
          {Object.entries(t.tabs).map(([id, label]) => (
            <button
              key={id}
              onClick={() => abrirTab(id)}
              className={`px-4 py-2 text-sm font-extrabold border-b-2 -mb-px transition ${
                tab === id ? `border-[#0284C7] ${theme.textSubtitle}` : `border-transparent ${theme.textMuted}`
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {tab === "review" && (
          <>
            <div className="flex flex-wrap items-center gap-3">
              <input ref={inputRef} type="file" accept=".pdf" multiple className="hidden" onChange={subir} />
              <button
                onClick={() => inputRef.current?.click()}
                disabled={!!busy}
                className="text-sm font-extrabold px-4 py-2 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-60 shadow-md"
              >
                {t.upload}
              </button>
              {busy && <span className={`text-sm font-bold ${theme.textMuted}`}>{busy}</span>}
              {rows.length > 0 && (
                <span className={`text-sm ${theme.textMuted}`}>
                  {files.join(", ")} · {fmt(t.summary, { n: conteo("NEW"), r: conteo("REVISION"), g: conteo("REGISTERED") })}
                </span>
              )}
            </div>

            {pdfWarnings.length > 0 && (
              <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-700">
                <p className="font-extrabold">{t.pdfWarn}</p>
                {pdfWarnings.map((w, i) => <p key={i}>• {w}</p>)}
              </div>
            )}

            {rows.length === 0 ? (
              <p className={`text-sm py-10 text-center ${theme.textMuted}`}>{t.empty}</p>
            ) : (
              <>
                <div className={`overflow-auto rounded-xl border ${borde}`}>
                  <table className="w-full text-sm">
                    <thead className={isDarkMode ? "bg-[#171A29] text-slate-300" : "bg-slate-100 text-slate-600"}>
                      <tr>
                        {["sel", "status", "piktik", ...EDITABLES.map((e) => e.col || e.key), "received", "changes"].map((c) => (
                          <th key={c} className="px-2 py-2 text-left text-xs font-extrabold uppercase whitespace-nowrap">
                            {t.cols[c] ?? t.cols[c === "ship_date" ? "ship" : c]}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((r) => {
                        const bloqueada = r.status === "REGISTERED";
                        return (
                          <tr key={r.piktik} className={`border-t ${borde} ${bloqueada ? "opacity-60" : ""}`}>
                            <td className="px-2 py-1.5">
                              <input
                                type="checkbox"
                                className="w-4 h-4 accent-[#0284C7]"
                                disabled={bloqueada}
                                checked={selected.has(r.piktik)}
                                onChange={() => alternar(r.piktik)}
                              />
                            </td>
                            <td className="px-2 py-1.5">{badge(r.status)}</td>
                            <td className={`px-2 py-1.5 font-mono font-bold ${theme.textTitle}`}>
                              {r.piktik}
                              {r.sheet_row && <span className={`block text-[11px] font-normal ${theme.textMuted}`}>{t.cols.row} {r.sheet_row}</span>}
                            </td>
                            {EDITABLES.map((e) => (
                              <td key={e.key} className="px-1 py-1">
                                <input
                                  type={e.type || "text"}
                                  value={e.key === "containers" ? r.containers.join(" ") : r[e.key]}
                                  onChange={(ev) => editar(r.piktik, e.key, ev.target.value)}
                                  className={`${e.w} text-sm font-mono px-2 py-1 rounded border ${theme.inputBg}`}
                                />
                              </td>
                            ))}
                            <td className={`px-2 py-1.5 font-bold ${r.received === "Yes" ? "text-emerald-600" : theme.textTitle}`}>
                              {r.received}
                            </td>
                            <td className={`px-2 py-1.5 text-xs min-w-[14rem] ${theme.textTitle}`}>
                              {r.diffs.map((d) => (
                                <p key={d.col} className="font-bold text-amber-600">
                                  {d.campo}: {d.antes || "—"} → {d.ahora}
                                </p>
                              ))}
                              {r.warnings.map((w, i) => (
                                <p key={i} className={theme.textMuted}>⚠ {w}</p>
                              ))}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  {dirty && (
                    <>
                      <span className="text-sm font-bold text-amber-600">{t.edited}</span>
                      <button className={boton} disabled={!!busy} onClick={verificar}>{t.recheck}</button>
                    </>
                  )}
                  <button
                    onClick={escribir}
                    disabled={!!busy || dirty || aEscribir.length === 0}
                    className="text-sm font-extrabold px-4 py-2 rounded-lg bg-[#0284C7] text-white hover:bg-[#0369A1] disabled:opacity-50 shadow-md"
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
            <p className={`text-sm max-w-3xl ${theme.textMuted}`}>{t.sugIntro}</p>
            <button className={boton} disabled={!!busy} onClick={cargarSugerencias}>{busy || t.sugLoad}</button>
            {suggestions && (suggestions.length === 0 ? (
              <p className={`text-sm ${theme.textMuted}`}>{t.sugNone}</p>
            ) : (
              <DataTable
                columns={[
                  { key: "row", label: t.cols.row },
                  { key: "piktik", label: t.cols.piktik, render: (s) => <span className="font-mono font-bold">{s.piktik}</span> },
                  { key: "containers", label: t.cols.containers, render: (s) => s.containers.join(" ") },
                ]}
                rows={suggestions}
                rowKey={(s) => s.row}
                theme={theme}
                isDarkMode={isDarkMode}
              />
            ))}
          </div>
        )}

        {tab === "log" && (log && log.length ? (
          <DataTable
            columns={[
              { key: "ts", label: t.cols.when, render: (l) => new Date(l.ts).toLocaleString() },
              { key: "action", label: t.cols.action, render: (l) => badge(l.action) },
              { key: "piktik", label: t.cols.piktik, render: (l) => <span className="font-mono">{l.piktik}</span> },
              { key: "po", label: t.cols.po },
              { key: "store", label: t.cols.store },
              { key: "sheet_row", label: t.cols.row },
              { key: "source_ref", label: t.cols.source, className: "min-w-[12rem]" },
            ]}
            rows={log}
            rowKey={(l) => l.id}
            theme={theme}
            isDarkMode={isDarkMode}
          />
        ) : (
          <p className={`text-sm py-10 text-center ${theme.textMuted}`}>{log === null ? t.reading : t.noLog}</p>
        ))}
      </div>
    </div>
  );
}
