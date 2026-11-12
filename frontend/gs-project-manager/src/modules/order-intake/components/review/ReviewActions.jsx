import { fmt } from "../../../../shared/i18n/format";

// Acciones de la revisión (fijas abajo en celular).
export default function ReviewActions({ review, busy, t }) {
  const { dirty, verificar, escribir, aEscribir } = review;
  return (
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
  );
}
