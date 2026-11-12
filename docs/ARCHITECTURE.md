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
│   ├── google/             credenciales OAuth (auth.py, config.py)
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
| `order_intake` | `/api/order-intake` | `rules/` (columns, received, revision), `services/` (analysis, writer), `sheets_client` |

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
│   ├── App.jsx             rutas: inicio + una por módulo
│   ├── modules.js          registro de módulos (id, ruta, icono, página perezosa)
│   ├── i18n.js             textos del shell
│   ├── components/         Layout, Navbar, LanguageSwitch, ThemeToggle, ModuleCard
│   └── pages/              Home, NotFound
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

### Agregar un módulo de frontend

1. Crear `src/modules/<id>/<Nombre>Page.jsx` siguiendo la estructura anterior.
2. Añadir la entrada en `src/app/modules.js` y sus textos en `src/app/i18n.js` (`modules.<id>`).
3. Cliente HTTP: `const request = createApiClient("/<id>");`.
4. Textos: `const t = useTranslations(I18N);` con `I18N = { es: {...}, en: {...} }`.

## Verificación

- Backend: `cd backend && venv\Scripts\python -m pytest`
- Frontend: `cd frontend/gs-project-manager && npm run lint && npm run build`
