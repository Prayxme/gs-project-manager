import { useMemo, useState } from "react";
import { useLocation, useNavigationType, useSearchParams } from "react-router-dom";
import { Alert, FileButton, InfoPanel, PageHeader, Tabs } from "../../shared/components";
import { useBusyTask } from "../../shared/hooks/useBusyTask";
import { useTranslations } from "../../shared/settings";
import AlreadyRoutedList from "./components/AlreadyRoutedList";
import ExcludedList from "./components/ExcludedList";
import MissingList from "./components/MissingList";
import PlanSummary from "./components/PlanSummary";
import PreRoutePanel from "./components/PreRoutePanel";
import RtsCard from "./components/RtsCard";
import SelectionBar from "./components/SelectionBar";
import { I18N } from "./constants";
import { usePreRoute } from "./hooks/usePreRoute";
import { useRoutingPlan } from "./hooks/useRoutingPlan";
import { URGENT_QUERY, seleccionDesdeUrl } from "./utils/selection";

export default function RoutingPage() {
  const t = useTranslations(I18N);
  const task = useBusyTask();

  // Desde el Monitor se llega con una selección en la URL (estados y Customer No).
  const [params, setParams] = useSearchParams();
  const consulta = params.toString();
  const seleccion = useMemo(() => seleccionDesdeUrl(new URLSearchParams(consulta)), [consulta]);

  // Al regresar (botón atrás o "Volver a Routing" del Paletizador) se conserva el plan ya calculado.
  const navegacion = useNavigationType();
  const { state } = useLocation();
  const restaurar = navegacion === "POP" || Boolean(state?.restore);
  const { plan, files, subir, cargarSeleccion, limpiar, mostrar } = useRoutingPlan({ t, task, seleccion, restaurar });

  // Dos formas de dar los datos: Pick Tickets (PDF / Monitor) o Pre Routing (Excel o a mano, por cubo).
  const pre = usePreRoute({ t, task, onPlan: mostrar });
  const [modoElegido, setModo] = useState(() => (plan?.source === "preroute" ? "preroute" : "pdf"));
  const modo = seleccion.key ? "pdf" : modoElegido;

  const urgentes = () => (params.get("scope") === "urgent" ? cargarSeleccion() : setParams(URGENT_QUERY));
  const quitarSeleccion = () => {
    limpiar();
    setParams({});
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1400px] mx-auto px-3 sm:px-5 py-4 sm:py-5 space-y-4 pb-28 md:pb-5">
        <PageHeader title={t.title} subtitle={t.subtitle}>
          {plan && !seleccion.key && (
            <button type="button" className="btn-secondary w-full sm:w-auto" disabled={!!task.busy} onClick={limpiar}>
              {t.clear}
            </button>
          )}
          <button type="button" className="btn-secondary w-full sm:w-auto" disabled={!!task.busy} onClick={urgentes}>
            {t.urgentButton}
          </button>
          <FileButton accept=".pdf" multiple onFiles={subir} disabled={!!task.busy} className="btn-primary w-full sm:w-auto">
            {t.upload}
          </FileButton>
        </PageHeader>

        <InfoPanel id="routing" title={t.info.title} sections={t.info.sections} />

        {!seleccion.key && (
          <Tabs
            active={modo}
            onChange={setModo}
            tabs={[["pdf", t.modes.pdf], ["preroute", t.modes.preroute, pre.lines.length || undefined]]}
          />
        )}
        {modo === "preroute" && <PreRoutePanel pre={pre} busy={!!task.busy} t={t} />}

        <SelectionBar
          seleccion={seleccion}
          plan={plan}
          busy={!!task.busy}
          onRecalc={cargarSeleccion}
          onClear={quitarSeleccion}
          t={t}
        />

        <Alert onClose={() => task.setError("")}>{task.error}</Alert>
        {task.busy && <p className="text-sm font-bold text-muted animate-pulse">{task.busy}</p>}
        {!plan && !task.busy && modo === "pdf" && <p className="card p-4 text-sm text-muted">{t.empty}</p>}

        {plan && (
          <>
            <PlanSummary plan={plan} files={files} t={t} />
            <MissingList orders={plan.missing} t={t} />
            <ExcludedList pos={plan.excluded} t={t} />
            {plan.rts.map((r) => <RtsCard key={r.number} rts={r} t={t} />)}
            <AlreadyRoutedList pos={plan.already_routed} t={t} />
          </>
        )}
      </div>
    </div>
  );
}
