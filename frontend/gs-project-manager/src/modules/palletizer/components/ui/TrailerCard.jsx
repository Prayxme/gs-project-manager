export default function TrailerCard({ totalPalletsGenerados, numRTs, totalCubeFeet, totalGrossWeight, maxCft, t }) {
  if (totalPalletsGenerados <= 0) return null;
  const excede = totalCubeFeet > maxCft;

  const fila = "flex justify-between items-baseline gap-3 px-2.5 py-2 rounded-xl text-xs bg-surface-2";
  return (
    <div className="card p-4 w-full bg-surface/95 backdrop-blur-md">
      <span className="text-[10px] font-extrabold uppercase tracking-widest text-brand block mb-0.5">
        {t.logisticsRouting}
      </span>
      <h3 className="text-sm font-black text-ink mb-3">{t.trailerEstimation}</h3>

      <div className="space-y-1.5">
        <div className={fila}>
          <span className="font-bold text-muted">{t.totalPallets}</span>
          <span className="font-extrabold font-mono text-ink">
            {totalPalletsGenerados} <span className="font-normal text-muted ml-1">({numRTs} {t.rtsReq})</span>
          </span>
        </div>
        <div className={`${fila} ${excede ? "!bg-red-500/10 ring-1 ring-red-500/40" : ""}`}>
          <span className="font-bold text-muted">{t.totalCft}</span>
          <span className={`font-extrabold font-mono ${excede ? "text-red-600 dark:text-red-400" : "text-ink"}`}>
            {totalCubeFeet} <span className="font-normal text-muted ml-1">{t.maxCft}</span>
          </span>
        </div>
        <div className={fila}>
          <span className="font-bold text-muted">{t.grossWeight}</span>
          <span className="font-extrabold font-mono text-brand">
            {totalGrossWeight.toLocaleString()} <span className="font-normal text-muted">{t.lbs}</span>
          </span>
        </div>
      </div>
    </div>
  );
}
