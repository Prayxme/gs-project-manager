# Arquitectura — Golden State Project Manager (Wiesner)

Plataforma modular: un **shell** común y **módulos** independientes (Paletizador, Monitor de Órdenes
Abiertas, Ingreso de Órdenes, …). Este documento fija dónde va cada cosa para que el proyecto crezca
sin archivos gigantes ni código duplicado.

## Reglas de modularidad

1. **Una responsabilidad por archivo.** Si un archivo mezcla HTTP, reglas, base de datos y
   presentación, se divide. Como referencia, un archivo que pasa de ~200 líneas es señal de revisar.
2. **Los módulos no se importan entre sí.** Lo que necesiten dos módulos va a la capa compartida
   (`backend/app/shared`, `frontend/.../src/shared`).
3. **El shell y `shared` no dependen de ningún módulo.** Los módulos dependen de `shared`, nunca al revés.
4. **Las reglas de negocio son funciones puras** (sin red, sin base de datos) para poder probarlas solas.
5. **La capa HTTP solo valida y delega.** Los routers no contienen lógica de negocio.
6. **Cada carpeta expone su API en `__init__.py` / `index.js`**; fuera de la carpeta se importa desde ahí.

## Backend (`backend/app`)

```text
app/
├── main.py                 FastAPI: monta los módulos registrados y arranca sus tareas de fondo
├── core/                   infraestructura de la plataforma
│   ├── config.py           nombre, versión, CORS
│   ├── settings.py         env(): variables de backend/.env (cargado una sola vez)
│   ├── database.py         engine de PostgreSQL (get_engine)
│   ├── dependencies.py     repository_dependency(): repositorio perezoso, 503 si no hay base
│   ├── errors.py           http_errors(): excepciones -> HTTPException por reglas
│   └── registry.py         carga automática de app/modules/<id>/module.py
├── shared/                 utilidades reutilizables (sin dependencias de módulos)
│   ├── dates.py  text.py  containers.py  spreadsheet.py  db.py
│   ├── google/             credenciales OAuth (auth.py, config.py) y lectura de Gmail (gmail.py)
│   └── pick_ticket/        lector del PDF de Pick Tickets (patterns, item_line, page, parser, schemas)
└── modules/<id>/
    ├── module.py           ModuleSpec(id, router, background_tasks) -> registro automático
    ├── config.py           configuración propia del módulo
    ├── router.py           endpoints /api/<id>/... (solo HTTP)
    ├── dependencies.py     dependencias FastAPI del módulo (repositorio, clientes externos)
    ├── models.py           tablas SQLAlchemy (schema propio en PostgreSQL)
    ├── repository.py       acceso a base de datos
    ├── rules/              reglas de negocio puras, un tema por archivo
    └── services/           casos de uso que combinan reglas + repositorio + clientes externos
```

Módulos actuales:

| Módulo | Ruta API | Piezas principales |
|---|---|---|
| `palletizer` | `/api/palletizer` | `services/`: `models`, `layer_patterns`, `placement`, `group_packer`, `physics_engine`, `packing_service` (entrada) |
| `open_orders` | `/api/open-orders` | `rules/` (window, cfrm, status, changes), `services/` (refresh, views, history_import), `portal_client`, `parser`, `scheduler` |
| `order_intake` | `/api/order-intake` | `rules/` (columns, received, revision, inbox), `services/` (analysis, writer, gmail_sync, inbox), `sheets_client`, `inbox_repository`, `inbox_router`, `scheduler` (revisión de Gmail) |

### Agregar un módulo de backend

1. Crear `app/modules/<id>/` con `router.py` y `module.py`:
   ```python
   from app.core.registry import ModuleSpec
   from app.modules.<id>.router import router
   MODULE = ModuleSpec(id="<id>", router=router)
   ```
2. Importar su `MODULE` en `load_modules()` de `app/core/registry.py` y sumarlo a la lista.
3. Si usa base de datos: `models.py` con su propio schema, migración de Alembic en `backend/migrations`,
   `repository.py` y `get_repository = repository_dependency(MiRepositorio)` en `dependencies.py`.
4. Pruebas en `backend/tests/<id>/` (nombres de archivo únicos en todo `tests/`).

## Frontend (`frontend/gs-project-manager/src`)

```text
src/
├── main.jsx                arranque: router + AppSettingsProvider
├── index.css               tokens de color (claro/oscuro) y utilidades (card, input, btn-*)
├── app/                    shell de la plataforma
│   ├── App.jsx             rutas generadas desde el registro (almacén -> cliente -> módulo)
│   ├── registry/           modules.js (catálogo de herramientas) y warehouses.js (almacenes,
│   │                       clientes y qué módulos tiene cada cliente; redirecciones de rutas viejas)
│   ├── routing/            paths.js (construir/validar URLs), breadcrumbs.js, CanonicalPath (minúsculas)
│   ├── i18n.js             textos del shell (almacenes, clientes, módulos)
│   ├── components/         Layout, Navbar, Breadcrumbs, LanguageSwitch, ThemeToggle, NavCard, CardGridPage
│   └── pages/              WarehousesPage (/), WarehousePage, ClientPage, ComingSoonPage, NotFound
├── shared/                 reutilizable por todos los módulos
│   ├── api/                createApiClient(prefijo), jsonBody, fileBody, API_BASE_URL
│   ├── settings/           AppSettingsProvider, useAppSettings, useTranslations
│   ├── components/         Alert, Badge, DataTable, FileButton, PageHeader, Tabs (index.js)
│   ├── hooks/              useBusyTask (ocupado + error de una tarea asíncrona)
│   ├── i18n/format.js      fmt("{n} órdenes", { n })
│   └── utils/              dates.js, storage.js
└── modules/<id>/
    ├── <Nombre>Page.jsx    solo compone: hooks + componentes
    ├── constants/          i18n.js, estilos/estados, configuración (index.js)
    ├── services/           cliente HTTP del módulo (usa createApiClient)
    ├── hooks/              estado y acciones (datos, filtros, formularios)
    ├── columns/            definiciones de columnas para DataTable
    ├── components/         piezas visuales del módulo
    └── utils/              funciones puras del módulo
```

### URLs: almacén / cliente / módulo

```text
/                                   almacenes
/<almacén>                          clientes del almacén (o "Próximamente" si aún no tiene)
/<almacén>/<cliente>                herramientas del cliente
/<almacén>/<cliente>/<módulo>       la herramienta       p. ej. /bonnie/wiesner/order-intake
```

Las rutas salen SOLO de `app/registry/warehouses.js`: lo que no esté declarado muestra 404, y una
URL con mayúsculas redirige a su forma en minúsculas. Las rutas anteriores (`/palletizer`, …)
redirigen a `/bonnie/wiesner/...`.

- **Habilitar un módulo existente para otro cliente:** añadir su id en `modules` del cliente.
- **Nuevo cliente:** agregarlo en `clients` de su almacén + descripción en `app/i18n.js` (`clients.<id>`).
- **Abrir un almacén:** `status: "active"` y al menos un cliente.

> Hoy el backend de los módulos está configurado para Wiesner (hojas, portal, Gmail). Para usar un
> módulo con otro cliente habrá que parametrizar esa configuración por cliente.
>
> En producción, el servidor web debe devolver `index.html` para cualquier ruta (SPA), para que
> los enlaces directos como `/bonnie/wiesner/open-orders` funcionen.

### Agregar un módulo de frontend

1. Crear `src/modules/<id>/<Nombre>Page.jsx` siguiendo la estructura anterior.
2. Añadir la entrada en `src/app/registry/modules.js`, sus textos en `src/app/i18n.js` (`modules.<id>`)
   y habilitarlo para los clientes que lo usen en `src/app/registry/warehouses.js`.
3. Cliente HTTP: `const request = createApiClient("/<id>");`.
4. Textos: `const t = useTranslations(I18N);` con `I18N = { es: {...}, en: {...} }`.

### Tareas de fondo

Un módulo declara tareas en `ModuleSpec(background_tasks=[...])` (p. ej. el refresco del portal o la
revisión de Gmail). Arrancan con el servidor; `GS_DISABLE_BACKGROUND_TASKS=1` las apaga, y las
pruebas lo activan en `tests/conftest.py` para no tocar servicios reales.

## Verificación

- Backend: `cd backend && venv\Scripts\python -m pytest`
- Frontend: `cd frontend/gs-project-manager && npm run lint && npm run build`
