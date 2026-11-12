// Pallets de margen de una vista externa (p. ej. un RTS): los que se enrutan por encima de los
// que el motor armó. Se muestran como un layout extra de pallets vacíos.

// [{ po, built, margin, pallets }] — armados por el motor, margen y total a enrutar de cada PO.
export function margenPorPo(grupos, pos = []) {
  const armados = {};
  grupos.forEach((g) => {
    if (!g.margen) armados[g.po] = (armados[g.po] || 0) + g.count;
  });
  return pos.map((p) => {
    const built = armados[p.po] || 0;
    return { po: p.po, built, margin: Math.max(0, p.pallets - built), pallets: Math.max(p.pallets, built) };
  });
}

// Grupos del motor + un grupo "margen" con los pallets vacíos (conserva .count y .cantidad).
export function conPalletsDeMargen(grupos, pos = []) {
  const margen = margenPorPo(grupos, pos).reduce((s, p) => s + p.margin, 0);
  if (!grupos.length || margen <= 0) return grupos;
  const vacio = { pallet_id: "MARGEN", po: "", placed_items: [] };
  return [...grupos, { pallet: vacio, po: "", dc: "", count: margen, cantidad: margen, margen: true }];
}
