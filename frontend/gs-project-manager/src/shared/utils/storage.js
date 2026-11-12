// localStorage seguro: si el navegador lo bloquea (modo privado, permisos), no rompe la app.

export function leerPreferencia(clave, porDefecto) {
  try {
    const v = localStorage.getItem(clave);
    return v === null ? porDefecto : JSON.parse(v);
  } catch {
    return porDefecto;
  }
}

export function guardarPreferencia(clave, valor) {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch {
    // Sin almacenamiento disponible: la preferencia solo dura la sesión.
  }
}

// sessionStorage seguro: datos de trabajo que deben sobrevivir al cambiar de módulo o recargar la
// pestaña, pero no entre sesiones (p. ej. el plan de Routing mientras se mira el Paletizador).
export function leerSesion(clave, porDefecto) {
  try {
    const v = sessionStorage.getItem(clave);
    return v === null ? porDefecto : JSON.parse(v);
  } catch {
    return porDefecto;
  }
}

export function guardarSesion(clave, valor) {
  try {
    sessionStorage.setItem(clave, JSON.stringify(valor));
  } catch {
    // Sin almacenamiento disponible (o lleno): el dato solo dura mientras la página está abierta.
  }
}
