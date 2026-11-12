import { useState } from "react";
import { Alert, PageHeader, Tabs } from "../../shared/components";
import { useBusyTask } from "../../shared/hooks/useBusyTask";
import { useTranslations } from "../../shared/settings";
import LogTab from "./components/LogTab";
import ReviewTab from "./components/ReviewTab";
import SuggestionsTab from "./components/SuggestionsTab";
import { I18N } from "./constants";
import { useIntakeLog } from "./hooks/useIntakeLog";
import { useIntakeReview } from "./hooks/useIntakeReview";
import { useSuggestions } from "./hooks/useSuggestions";

export default function OrderIntakePage() {
  const t = useTranslations(I18N);
  const [tab, setTab] = useState("review");
  const [notice, setNotice] = useState("");
  const task = useBusyTask();
  const log = useIntakeLog(task.setError);
  const review = useIntakeReview({ t, task, onNotice: setNotice, onWritten: log.invalidar });
  const sug = useSuggestions({ t, task });

  const abrirTab = (id) => {
    setTab(id);
    if (id === "log") log.cargarSiHaceFalta();
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1800px] mx-auto px-3 sm:px-5 py-4 sm:py-5 space-y-4 pb-28 md:pb-5">
        <PageHeader title={t.title} subtitle={t.subtitle} />

        <Alert onClose={() => task.setError("")}>{task.error}</Alert>
        <Alert kind="success" onClose={() => setNotice("")}>{notice}</Alert>

        <Tabs
          active={tab}
          onChange={abrirTab}
          tabs={[["review", t.tabs.review], ["suggestions", t.tabs.suggestions], ["log", t.tabs.log]]}
        />

        {tab === "review" && <ReviewTab review={review} busy={task.busy} t={t} />}
        {tab === "suggestions" && (
          <SuggestionsTab suggestions={sug.suggestions} onLoad={sug.cargar} busy={task.busy} t={t} />
        )}
        {tab === "log" && <LogTab log={log.log} t={t} />}
      </div>
    </div>
  );
}
