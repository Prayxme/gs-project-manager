import { clientPath, modulePath, resolvePath, warehousePath } from "./paths";

/**
 * Migas de pan de una URL: [{ label, to }] desde el almacén hasta la página actual, y la
 * ruta del nivel superior (para el botón "volver"). Una URL inválida no tiene migas.
 */
export function breadcrumbs(pathname, t) {
  const { warehouse: w, client: c, module: m, valid } = resolvePath(pathname);
  if (!valid || !w) return { items: [], parent: null };
  const items = [{ label: w.name, to: warehousePath(w) }];
  if (c) items.push({ label: c.name, to: clientPath(w, c) });
  if (m) items.push({ label: t.modules[m.id].name, to: modulePath(w, c, m) });
  const parent = items.length > 1 ? items[items.length - 2].to : "/";
  return { items, parent };
}
