// Rellena una plantilla de traducción: fmt("{n} órdenes", { n: 3 }) -> "3 órdenes".
export const fmt = (s, vars) => s.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");
