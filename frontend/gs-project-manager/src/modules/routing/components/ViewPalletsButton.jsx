import { useLocation, useNavigate } from "react-router-dom";
import { PREVIEW_SOURCE, guardarVistaPallets } from "../../../shared/handoff";
import { vistaDeRts } from "../utils/palletPreview";

// Abre el Paletizador 3D con la carga de este RTS (armado de los pallets + pallets de margen).
// El plan de Routing queda guardado en la sesión: al volver se muestra igual.
export default function ViewPalletsButton({ rts, t }) {
  const navigate = useNavigate();
  const { pathname, search } = useLocation();
  const hayLineas = rts.pos.some((po) => po.items?.length);

  const abrir = () => {
    guardarVistaPallets(vistaDeRts(rts, t, pathname + search));
    navigate(`../palletizer?source=${PREVIEW_SOURCE}`, { relative: "path" });
  };

  return (
    <button type="button" className="btn-secondary text-xs px-3 py-1.5" disabled={!hayLineas} onClick={abrir}>
      🧱 {t.viewPallets}
    </button>
  );
}
