import { useEffect, useState } from "react";

const FORMATO = new Intl.DateTimeFormat("en-US", {
  timeZone: "America/Los_Angeles",
  weekday: "short",
  month: "short",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});

// Reloj en vivo con la hora de California (independiente de dónde se abra la app).
export default function CaliforniaClock({ label, theme }) {
  const [ahora, setAhora] = useState(() => new Date());
  useEffect(() => {
    const id = setInterval(() => setAhora(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return (
    <div className="flex flex-col leading-tight">
      <span className={`text-[11px] font-bold uppercase tracking-wider ${theme.textMuted}`}>{label}</span>
      <span className={`font-mono text-sm font-bold tabular-nums ${theme.textTitle}`}>{FORMATO.format(ahora)}</span>
    </div>
  );
}
