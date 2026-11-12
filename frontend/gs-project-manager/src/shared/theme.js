// Clases del tema. Los colores reales viven en src/index.css como tokens (claro y oscuro);
// aquí solo se nombran los usos para que todos los módulos se vean igual.
const THEME = {
  bgApp: "bg-canvas text-ink",
  bgHeader: "bg-header text-on-header border-black/10",
  bgSidebar: "bg-surface border-line",
  bgSidebarFooter: "bg-surface-2 border-line",
  bgCard: "card hover:border-brand/50",
  textTitle: "text-ink",
  textSubtitle: "text-brand",
  textMuted: "text-muted",
  inputBg: "bg-surface text-ink border-line focus:border-brand",
  viewportBg: "bg-viewport",
  hudCard: "bg-surface/95 border-line text-ink shadow-card",
};

// Se conserva la firma (isDarkMode) por compatibilidad; los tokens ya cambian solos.
export function buildTheme() {
  return THEME;
}
