// Selector de vista en celular: formulario de carga o visor 3D.
export default function MobileViewSwitch({ vista, setVista, totalPallets, t }) {
  const opciones = [
    ["data", t.tabCargo],
    ["3d", `${t.tab3d}${totalPallets ? ` · ${totalPallets}` : ""}`],
  ];
  return (
    <div className="md:hidden flex gap-1 p-1 m-2 mb-0 rounded-xl bg-surface border border-line shrink-0">
      {opciones.map(([id, texto]) => (
        <button
          key={id}
          onClick={() => setVista(id)}
          className={`flex-1 py-2 rounded-lg text-sm font-extrabold transition ${
            vista === id ? "bg-brand text-on-brand shadow-sm" : "text-muted hover:text-ink"
          }`}
        >
          {texto}
        </button>
      ))}
    </div>
  );
}
