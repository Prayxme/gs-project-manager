import { useRef } from "react";

// Botón que abre el selector de archivos y entrega la lista elegida a onFiles([File, ...]).
// El input se limpia cada vez para poder volver a elegir el mismo archivo.
export default function FileButton({ accept, multiple = false, onFiles, className = "btn-secondary", disabled, children }) {
  const ref = useRef(null);
  const alElegir = (ev) => {
    const lista = Array.from(ev.target.files || []);
    ev.target.value = null;
    if (lista.length) onFiles(lista);
  };
  return (
    <>
      <input ref={ref} type="file" accept={accept} multiple={multiple} className="hidden" onChange={alElegir} />
      <button type="button" className={className} disabled={disabled} onClick={() => ref.current?.click()}>
        {children}
      </button>
    </>
  );
}
