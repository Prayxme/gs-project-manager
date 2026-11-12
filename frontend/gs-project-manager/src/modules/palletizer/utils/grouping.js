// Agrupación de pallets con el mismo armado ("Layout A", "Layout B", ...).

// Huella de una caja: SKU|x|y|z|w|h|d normalizados a un decimal (evita 10.000000000000002 vs 10.0).
function huellaCaja(item) {
  const p = item.position || { x: 0, y: 0, z: 0 };
  const d = item.rendered_dimensions || { width_in: 0, height_in: 0, length_in: 0 };
  return [item.sku, p.x, p.y, p.z, d.width_in, d.height_in, d.length_in]
    .map((v, i) => (i === 0 ? String(v) : Number(v).toFixed(1)))
    .join("|");
}

// La PO/DC forma parte de la huella: pallets idénticos de órdenes distintas
// no se agrupan, para conservar la trazabilidad.
function huellaPallet(pallet) {
  const cajas = pallet.placed_items.map(huellaCaja).sort();
  return `${pallet.ship_to_dc || ""}@@${pallet.po || ""}@@${cajas.join("##")}`;
}

/**
 * Grupos ordenados por frecuencia: [{ pallet, po, dc, count, cantidad, layoutId }].
 * `.count` y `.cantidad` valen lo mismo y se mantienen ambos por compatibilidad con la UI.
 */
export function agruparPallets(pallets) {
  const grupos = {};
  pallets.forEach((pallet) => {
    const huella = huellaPallet(pallet);
    if (!grupos[huella]) {
      grupos[huella] = { count: 0, cantidad: 0, pallet, po: pallet.po || "", dc: pallet.ship_to_dc || "" };
    }
    grupos[huella].count += 1;
    grupos[huella].cantidad += 1;
  });

  return Object.values(grupos)
    .sort((a, b) => b.count - a.count)
    .map((grupo, index) => ({ ...grupo, layoutId: `Layout ${String.fromCharCode(65 + index)}` }));
}
