import { Navigate, useLocation } from "react-router-dom";

// Una sola forma válida de cada URL: en minúsculas (/BONNIE/Wiesner -> /bonnie/wiesner).
// Si ya es canónica, muestra la página normalmente.
export default function CanonicalPath({ children }) {
  const { pathname, search, hash } = useLocation();
  const canonica = pathname.toLowerCase();
  if (pathname !== canonica) return <Navigate to={`${canonica}${search}${hash}`} replace />;
  return children;
}
