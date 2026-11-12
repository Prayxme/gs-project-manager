// Etiqueta pequeña; el color lo da className (p. ej. los estilos de estado de cada módulo).
export default function Badge({ className = "", children }) {
  return (
    <span className={`inline-block px-2 py-0.5 rounded-md text-xs font-extrabold whitespace-nowrap ${className}`}>
      {children}
    </span>
  );
}
