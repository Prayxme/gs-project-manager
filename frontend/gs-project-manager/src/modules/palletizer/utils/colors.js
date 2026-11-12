import { colorPorIndice } from "../constants/palette";

// Clave de color: PO + SKU. El color identifica la mercancía de UNA orden.
export const colorKey = (po, sku) => `${po || ""}|${(sku || "").trim()}`;

// SKU de una línea del formulario (o un nombre por defecto si está vacío).
export const skuDeLinea = (item, idx) => item.sku?.trim() || `ITEM-${idx + 1}`;

// Un color único por combinación PO + SKU: el mismo SKU en dos POs distintas
// recibe colores distintos, y ningún color se repite entre POs.
export function buildSkuColorMap(items) {
  const map = {};
  items.forEach((item, idx) => {
    const key = colorKey(item.po, skuDeLinea(item, idx));
    if (!map[key]) {
      map[key] = colorPorIndice(Object.keys(map).length);
    }
  });
  return map;
}
