// Clases Tailwind del tema claro/oscuro, compartidas por el shell y todos los módulos.
export function buildTheme(isDarkMode) {
  return {
    bgApp: isDarkMode ? "bg-[#090A0F] text-slate-200" : "bg-[#F1F5F9] text-slate-800",
    bgHeader: isDarkMode ? "bg-[#11131F] border-[#1E2235]" : "bg-white border-slate-200 shadow-sm",
    bgSidebar: isDarkMode ? "bg-[#0E101A] border-[#1E2235]" : "bg-white border-slate-200 shadow-xl z-20",
    bgSidebarFooter: isDarkMode ? "bg-[#11131F] border-[#1E2235]" : "bg-slate-50 border-slate-200",
    bgCard: isDarkMode
      ? "bg-[#11131F] border-[#1E2235] hover:border-[#38BDF8]/60"
      : "bg-white border-slate-200 shadow-sm hover:border-[#0284C7]/60 hover:shadow-md",
    textTitle: isDarkMode ? "text-white" : "text-slate-900",
    textSubtitle: isDarkMode ? "text-[#38BDF8]" : "text-[#0284C7]",
    textMuted: isDarkMode ? "text-slate-400" : "text-slate-500",
    inputBg: isDarkMode
      ? "bg-[#171A29] text-white border-[#272C42]"
      : "bg-white text-slate-900 border-slate-300 focus:border-[#0284C7] shadow-sm",
    viewportBg: isDarkMode ? "bg-[#07080C]" : "bg-[#E2E8F0]",
    hudCard: isDarkMode
      ? "bg-[#111422]/95 border-[#272C42] text-white"
      : "bg-white/95 border-slate-200 text-slate-800 shadow-xl",
  };
}
