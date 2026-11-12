import { MODULE_BY_ID } from "../registry/modules";
import { WAREHOUSES } from "../registry/warehouses";

export const warehousePath = (w) => `/${w.id}`;
export const clientPath = (w, c) => `/${w.id}/${c.id}`;
export const modulePath = (w, c, m) => `/${w.id}/${c.id}/${m.slug}`;

// Módulos (del catálogo) habilitados para un cliente.
export const clientModules = (c) => c.modules.map((id) => MODULE_BY_ID[id]).filter(Boolean);

/**
 * Ubica una URL dentro del registro: { warehouse, client, module, valid }.
 * valid=false si algún segmento no existe (la URL no corresponde a nada declarado).
 */
export function resolvePath(pathname) {
  const [wId, cId, mSlug, ...resto] = pathname.split("/").filter(Boolean);
  const vacio = { warehouse: null, client: null, module: null };
  if (!wId) return { ...vacio, valid: true };
  const warehouse = WAREHOUSES.find((w) => w.id === wId) || null;
  const client = warehouse?.clients.find((c) => c.id === cId) || null;
  const module = client ? clientModules(client).find((m) => m.slug === mSlug) || null : null;
  const valid =
    Boolean(warehouse) && (!cId || Boolean(client)) && (!mSlug || Boolean(module)) && resto.length === 0;
  return { warehouse, client, module, valid };
}
