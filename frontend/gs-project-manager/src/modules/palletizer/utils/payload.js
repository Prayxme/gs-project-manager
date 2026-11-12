import { LOGISTICS_DEFAULTS } from "../constants/logisticsConfig";

export const lineaVacia = () => ({ width: 0, length: 0, height: 0, weight: 0, qty: 0, sku: "" });

// Una línea del formulario por cada SKU de cada PikTik; conserva PO/PikTik/DC
// para que el motor nunca mezcle órdenes distintas en un mismo pallet.
export function formDesdePdf(pdf) {
  const orders = pdf.orders || [];
  return {
    orderInfo: {
      po: orders.map((o) => o.po).join(", "),
      piktik: orders.map((o) => o.piktik).join(", "),
      company: pdf.company,
      custNo: pdf.cust_no,
    },
    items: orders.flatMap((order) =>
      order.items.map((item, idx) => ({
        sku: item.sku || `ITEM-${idx + 1}`,
        qty: item.qty,
        length: item.l,
        width: item.w,
        height: item.h,
        weight: item.weight,
        po: order.po,
        piktik: order.piktik,
        dc: order.ship_to_dc,
      }))
    ),
  };
}

// Solicitud para POST /api/palletizer/pack a partir del formulario.
export function buildPackingPayload(orderInfo, items) {
  return {
    order_id: orderInfo.po || "PO-ONLINE",
    pallet_config: {
      length_in: LOGISTICS_DEFAULTS.PALLET_LENGTH,
      width_in: LOGISTICS_DEFAULTS.PALLET_WIDTH,
      base_height_in: LOGISTICS_DEFAULTS.PALLET_BASE_HEIGHT,
      max_total_height_in: LOGISTICS_DEFAULTS.MAX_TOTAL_HEIGHT,
      // Sin max_weight_lbs: el límite de peso por pallet aún no es regla de negocio.
    },
    items: items
      .filter((i) => Number(i.qty) > 0)
      .map((i, idx) => ({
        sku: i.sku || `ITEM-${idx + 1}`,
        quantity: Number(i.qty),
        dimensions: {
          length_in: Number(i.length),
          width_in: Number(i.width),
          height_in: Number(i.height),
        },
        weight_lbs: Number(i.weight),
        po: i.po || null,
        piktik: i.piktik || null,
        ship_to_dc: i.dc || null,
      })),
  };
}
