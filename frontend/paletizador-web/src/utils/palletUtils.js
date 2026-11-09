export const agruparPallets = (pallets) => {
  const grupos = {};

  pallets.forEach((pallet) => {
    const cajasHuella = pallet.placed_items.map(item => {
      const p = item.position || { x: 0, y: 0, z: 0 };
      const d = item.rendered_dimensions || { width_in: 0, height_in: 0, length_in: 0 };
      return `${item.sku}|${Number(p.x).toFixed(1)}|${Number(p.y).toFixed(1)}|${Number(p.z).toFixed(1)}|${Number(d.width_in).toFixed(1)}|${Number(d.height_in).toFixed(1)}|${Number(d.length_in).toFixed(1)}`;
    });

    cajasHuella.sort();
    const huellaDigital = cajasHuella.join('##');

    if (!grupos[huellaDigital]) {
      grupos[huellaDigital] = {
        count: 0,
        cantidad: 0,
        pallet: pallet,
      };
    }
    grupos[huellaDigital].count += 1;
    grupos[huellaDigital].cantidad += 1;
  });

  const arrayOrdenado = Object.values(grupos).sort((a, b) => b.count - a.count);

  return arrayOrdenado.map((grupo, index) => ({
    ...grupo,
    layoutId: `Layout ${String.fromCharCode(65 + index)}`
  }));
};

export function calculateCenteredOffsets(palletData, palletWidth = 40, palletLength = 48) {
  if (!palletData || !palletData.placed_items.length) {
    return { x: 0, z: 0 };
  }
  let maxX = 0;
  let maxZ = 0;
  palletData.placed_items.forEach((item) => {
    const endX = item.position.x + item.rendered_dimensions.width_in;
    const endZ = item.position.z + item.rendered_dimensions.length_in;
    if (endX > maxX) maxX = endX;
    if (endZ > maxZ) maxZ = endZ;
  });
  return {
    x: Math.max(0, (palletWidth - maxX) / 2),
    z: Math.max(0, (palletLength - maxZ) / 2),
  };
}