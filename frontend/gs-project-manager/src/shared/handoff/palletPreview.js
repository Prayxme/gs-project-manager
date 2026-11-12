// Contrato para ver en el Paletizador 3D una carga calculada en otro módulo (hoy: un RTS de Routing).
// Los módulos no se importan entre sí: el origen guarda aquí la carga y abre el Paletizador con
// ?source=preview; el Paletizador la lee y ofrece volver a `returnTo`.
//
// Vista = {
//   title, subtitle,            texto del encabezado (p. ej. "RTS 3 · BURL120" y el destino)
//   returnTo, returnLabel,      URL y texto del botón para regresar al módulo de origen
//   items: [{ sku, qty, length, width, height, weight, po, piktik }],
//   pos:   [{ po, estimated, pallets }],   pallets = los que se enrutan (estimados + margen)
//   totals: { pallets, weight, cft },
// }
import { guardarSesion, leerSesion } from "../utils/storage";

const CLAVE = "gs.palletPreview";

export const PREVIEW_SOURCE = "preview";

export const guardarVistaPallets = (vista) => guardarSesion(CLAVE, vista);

export const leerVistaPallets = () => leerSesion(CLAVE, null);
