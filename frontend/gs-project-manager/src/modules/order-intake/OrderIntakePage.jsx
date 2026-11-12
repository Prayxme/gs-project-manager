import { useState } from "react";
import { Alert, InfoPanel, PageHeader, Tabs } from "../../shared/components";
import { useBusyTask } from "../../shared/hooks/useBusyTask";
import { useTranslations } from "../../shared/settings";
import InboxTab from "./components/InboxTab";
import LogTab from "./components/LogTab";
import ReviewTab from "./components/ReviewTab";
import SuggestionsTab from "./components/SuggestionsTab";
import { I18N } from "./constants";
import { useInbox } from "./hooks/useInbox";
import { useIntakeLog } from "./hooks/useIntakeLog";
import { useIntakeReview } from "./hooks/useIntakeReview";
import { useSuggestions } from "./hooks/useSuggestions";

export default function OrderIntakePage() {
  const t = useTranslations(I18N);
  const [tab, setTab] = useState("inbox");
  const [notice, setNotice] = useState("");
  const task = useBusyTask();
  const log = useIntakeLog(task.setError);
  const inbox = useInbox({ t, task, onNotice: setNotice });
  const review = useIntakeReview({
    t, task, onNotice: setNotice,
    onWritten: () => {
      log.invalidar();
      inbox.cargar();
    },
  });
  const sug = useSuggestions({ t, task });

  const abrirTab = (id) => {
    setTab(id);
    if (id === "log") log.cargarSiHaceFalta();
  };

  // "Revisar" en la bandeja: carga ese PDF en la pantalla de revisión.
  const revisarDeBandeja = async (item) => {
    if (await review.cargarDesdeBandeja(item)) setTab("review");
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-[1800px] mx-auto px-3 sm:px-5 py-4 sm:py-5 space-y-4 pb-28 md:pb-5">
        <PageHeader title={t.title} subtitle={t.subtitle} />
        <InfoPanel id="order-intake" title={t.info.title} sections={t.info.sections} />

        <Alert onClose={() => task.setError("")}>{task.error}</Alert>
        <Alert kind="success" onClose={() => setNotice("")}>{notice}</Alert>

        <Tabs
          active={tab}
          onChange={abrirTab}
          tabs={[
            ["inbox", t.tabs.inbox, inbox.pending],
            ["review", t.tabs.review],
            ["suggestions", t.tabs.suggestions],
            ["log", t.tabs.log],
          ]}
        />

        {tab === "inbox" && <InboxTab inbox={inbox} onReview={revisarDeBandeja} busy={task.busy} t={t} />}
        {tab === "review" && <ReviewTab review={review} busy={task.busy} t={t} />}
        {tab === "suggestions" && (
          <SuggestionsTab suggestions={sug.suggestions} onLoad={sug.cargar} busy={task.busy} t={t} />
        )}
        {tab === "log" && <LogTab log={log.log} t={t} />}
      </div>
    </div>
  );
}
