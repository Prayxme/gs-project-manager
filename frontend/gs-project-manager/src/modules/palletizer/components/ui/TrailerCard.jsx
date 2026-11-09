export default function TrailerCard({
  totalPalletsGenerados,
  numRTs,
  totalCubeFeet,
  totalGrossWeight,
  maxCft,
  isDarkMode,
  t,
  theme,
}) {
  if (totalPalletsGenerados <= 0) return null;

  return (
    <div className={`p-4 rounded-2xl border w-full backdrop-blur-md shadow-lg ${theme.hudCard}`}>
      <div className="flex justify-between items-start mb-3">
        <div>
          <span className="text-[9px] font-extrabold uppercase tracking-widest text-emerald-500 block mb-0.5">
            {t.logisticsRouting}
          </span>
          <h3 className={`text-sm font-black ${theme.textTitle}`}>{t.trailerEstimation}</h3>
        </div>
      </div>

      <div className="space-y-2">
        <div className={`flex justify-between p-2 rounded-xl text-xs ${isDarkMode ? "bg-black/30" : "bg-slate-100"}`}>
          <span className="font-bold text-slate-400">{t.totalPallets}</span>
          <span className="font-extrabold font-mono">
            {totalPalletsGenerados}{" "}
            <span className="font-normal text-slate-400 ml-1">
              ({numRTs} {t.rtsReq})
            </span>
          </span>
        </div>

        <div
          className={`flex justify-between p-2 rounded-xl text-xs border ${
            totalCubeFeet > maxCft
              ? "border-red-500/50 bg-red-500/10"
              : isDarkMode
              ? "border-transparent bg-black/30"
              : "border-transparent bg-slate-100"
          }`}
        >
          <span className="font-bold text-slate-400">{t.totalCft}</span>
          <span className={`font-extrabold font-mono ${totalCubeFeet > maxCft ? "text-red-500" : theme.textTitle}`}>
            {totalCubeFeet} <span className="font-normal text-slate-400 ml-1">{t.maxCft}</span>
          </span>
        </div>

        <div className={`flex justify-between p-2 rounded-xl text-xs ${isDarkMode ? "bg-black/30" : "bg-slate-100"}`}>
          <span className="font-bold text-slate-400">{t.grossWeight}</span>
          <span className="font-extrabold font-mono text-[#0284C7]">
            {totalGrossWeight.toLocaleString()}{" "}
            <span className="font-normal text-slate-400">{t.lbs}</span>
          </span>
        </div>
      </div>
    </div>
  );
}