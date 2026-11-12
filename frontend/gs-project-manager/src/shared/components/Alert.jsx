const ALERT_STYLE = {
  error: "border-red-500/40 bg-red-500/10 text-red-700 dark:text-red-300",
  success: "border-brand/40 bg-brand-soft text-brand-ink",
  warning: "border-amber-500/40 bg-amber-500/10 text-amber-800 dark:text-amber-300",
};

// Mensaje de estado (error / éxito / aviso). No se muestra si no hay contenido.
export default function Alert({ kind = "error", children, onClose }) {
  if (!children) return null;
  return (
    <div className={`rounded-xl border px-4 py-2.5 text-sm flex items-start justify-between gap-3 ${ALERT_STYLE[kind]}`}>
      <div className="min-w-0 break-words">{children}</div>
      {onClose && (
        <button onClick={onClose} aria-label="Cerrar" className="font-bold opacity-70 hover:opacity-100 shrink-0">
          ✕
        </button>
      )}
    </div>
  );
}
