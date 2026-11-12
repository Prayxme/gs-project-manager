import { useMemo } from "react";
import { useLocation, useNavigationType, useSearchParams } from "react-router-dom";
import { Alert, FileButton, PageHeader } from "../../shared/components";
import { useBusyTask } from "../../shared/hooks/useBusyTask";
import { useTranslations } from "../../shared/settings";
import AlreadyRoutedList from "./components/AlreadyRoutedList";
import ExcludedList from "./components/ExcludedList";
import MissingList from "./components/MissingList";
import PlanSummary from "./components/PlanSummary";
import RtsCard from "./components/RtsCard";
import SelectionBar from "./components/SelectionBar";
import { I18N } from "./constants";
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
  const { plan, files, subir, cargarSeleccion, limpiar } = useRoutingPlan({ t, task, seleccion, restaurar });

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
        {!plan && !task.busy && <p className="card p-4 text-sm text-muted">{t.empty}</p>}

        {plan && (
          <>
            <PlanSummary plan={plan} files={files} t={t} />
            <MissingList orders={plan.missing} t={t} />
            <ExcludedList pos={plan.excluded} t={t} />
            {plan.rts.map((r) => <RtsCard key={r.number} rts={r} t={t} />)}
            <AlreadyRoutedList pos={plan.already_routed} t={t} />
          </>
        )}
        <p className="text-[11px] text-muted">{t.rules}</p>
      </div>
    </div>
  );
}
