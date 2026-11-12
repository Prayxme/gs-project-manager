import { fmt } from "../../../shared/i18n/format";
import { addressLine } from "./format";

// Carga de un RTS para verla en el Paletizador 3D (contrato en shared/handoff/palletPreview.js).
export function vistaDeRts(rts, t, returnTo) {
  return {
    title: `${fmt(t.rts, { n: rts.number })} · ${rts.family}`,
    subtitle: [rts.ship_to?.name, addressLine(rts.ship_to)].filter(Boolean).join(" · "),
    returnTo,
    returnLabel: t.backToRouting,
    items: rts.pos.flatMap((po) =>
      (po.items || []).map((i) => ({
        sku: i.sku, qty: i.qty, length: i.l, width: i.w, height: i.h, weight: i.weight,
        po: po.po, piktik: i.piktik,
      })),
    ),
    pos: rts.pos.map((po) => ({ po: po.po, estimated: po.estimated_pallets, pallets: po.pallets })),
    totals: { pallets: rts.pallets, weight: rts.weight, cft: rts.cft },
  };
}
