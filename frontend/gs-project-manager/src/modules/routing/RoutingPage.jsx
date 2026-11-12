import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { Alert, FileButton, PageHeader } from "../../shared/components";
import { useBusyTask } from "../../shared/hooks/useBusyTask";
import { useTranslations } from "../../shared/settings";
import AlreadyRoutedList from "./components/AlreadyRoutedList";
import ExcludedList from "./components/ExcludedList";
import MissingList from "./components/MissingList";
import PlanSummary from "./components/PlanSummary";
import RtsCard from "./components/RtsCard";
import { I18N } from "./constants";
import { useRoutingPlan } from "./hooks/useRoutingPlan";

export default function RoutingPage() {
  const t = useTranslations(I18N);
  const task = useBusyTask();
  const { plan, files, subir, cargarUrgentes } = useRoutingPlan({ t, task });

  // Desde el Monitor se llega con ?scope=urgent: se calculan de una vez las órdenes urgentes.
  const [params] = useSearchParams();
  const urgente = params.get("scope") === "urgent";
  useEffect(() => {
    if (urgente) cargarUrgentes();
  }, [urgente, cargarUrgentes]);

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1400px] mx-auto px-3 sm:px-5 py-4 sm:py-5 space-y-4 pb-28 md:pb-5">
        <PageHeader title={t.title} subtitle={t.subtitle}>
          <button type="button" className="btn-secondary w-full sm:w-auto" disabled={!!task.busy} onClick={cargarUrgentes}>
            {t.urgentButton}
          </button>
          <FileButton accept=".pdf" multiple onFiles={subir} disabled={!!task.busy} className="btn-primary w-full sm:w-auto">
            {t.upload}
          </FileButton>
        </PageHeader>

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
