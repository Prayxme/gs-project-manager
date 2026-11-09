# BITÁCORA DEL PROYECTO — 3D Pallet Optimizer & WMS Router

Registro corto y cronológico de cambios y decisiones. Lo más reciente arriba.
Formato: fecha · qué se hizo · por qué · cómo se verificó · pendiente.
(Contexto técnico completo: `claude.md`. Este archivo es solo el recorrido.)

## Reglas de negocio vigentes
- Un pallet NUNCA mezcla POs/DCs distintos. Dentro de una misma PO sí se mezclan SKU para rellenar huecos.
- Lo más pesado va como base (una caja no descansa sobre otra más liviana).
- Pallet GMA #2 four-way 48x40 in, base 5.5 in, altura total máx. 85 in (79.5 útil).
- Límite de peso por pallet: DESACTIVADO hasta confirmar la regla.
- Soporte basal mínimo 65 %; sin colisiones; todo dentro de los límites del pallet.
- PDF: una página por PikTik (o varias si hay muchos SKU). PikTik = id interno; PO = orden del cliente; cada PikTik tiene 1 PO y 1 destino (DC).

## Estructura actual (desde v0.10.0)
```
backend/app/
  main.py                      → incluye un router por módulo
  core/config.py               → configuración global (nombre, versión, CORS)
  modules/palletizer/          → router.py, schemas.py, config.py, services/
backend/tests/palletizer/      → pruebas del módulo
frontend/gs-project-manager/src/
  app/                         → shell: rutas, inicio, registro de módulos (modules.js), idioma/tema
  shared/                      → Navbar, tema, URL del API
  modules/palletizer/          → página, componentes, servicios, utilidades del paletizador
  modules/open-orders/         → (en construcción)
```
Agregar un módulo: carpeta en `frontend/.../modules/<id>/` + entrada en `app/modules.js` + textos en `app/i18n.js`;
en backend `app/modules/<id>/router.py` incluido en `main.py` con prefijo `/api/<id>`.

## Registro

### 2026-11-09 · Base de datos de la plataforma: PostgreSQL (v0.12.0)
- **Hecho:** base `gs_project_manager` (usuario `gs_app`), `alembic upgrade head` OK (schema `open_orders` con 5 tablas),
  sincronización inicial (535 órdenes) e importación del histórico ROUTING_COMPLETED (790 filas, 0 errores). Backend en vivo leyendo PostgreSQL.
- `.env.example` eliminado a pedido del usuario (no recrear).
- Pendiente de decisión: reclasificar 75 filas importadas REMOVED → COMPLETED (formatos LOAD ID #, CITI, FedEx), guardando el valor original.
- Decisión del usuario: PostgreSQL (servicio local `postgresql-x64-18`) como base única de la plataforma, pensando en módulos futuros.
- `app/core/database.py`: conexión compartida (SQLAlchemy 2 + psycopg 3) desde `DATABASE_URL` en `.env`.
- Cada módulo usa su propio *schema* PostgreSQL (`open_orders.*`). Estructura versionada con **Alembic** (`backend/migrations`, migración `0001_open_orders`).
- Se eliminó la base SQLite temporal. Las pruebas usan SQLite en memoria con el mismo código; producción usa PostgreSQL.
- Nota: el usuario eliminó `backend/.env.example` (commit "fixing") y pidió mantenerlo así.

### 2026-11-09 · Módulo Monitor de Órdenes Abiertas / Routing Wiesner (v0.11.0)
- Porta el Google Apps Script (scraper de wpinyweb.com) a `backend/app/modules/open_orders/` + `frontend/.../modules/open-orders/`.
- **Solo lectura del portal:** únicamente `ajcmd_show_list` (esa página también permite escribir routing). Credenciales SOLO en `backend/.env` (plantilla `.env.example`).
- **Primera base de datos:** SQLite en `backend/data/gs.db` (fuera de Git): órdenes actuales, historial de eventos con hora, órdenes cerradas, bitácora de actualizaciones.
- **Reglas:** ventana por cliente (BURL −5 días naturales/no antes del Ship; ROSS/DDSD ship−21; MACY ship−7; resto Cancel), estados OVERDUE/LAST DAY/ATTENTION(≤3)/SAFE/TOO EARLY/ROUTED.
  "Hoy" = fecha del navegador del usuario; reloj en vivo con hora de California en la página.
- **Errores del Apps Script corregidos:** historial duplicado cada 5 min; KPIs "hoy" que no eran de hoy; tabla vacía marcaba todo como cancelado (ahora se aborta y se conserva la foto);
  solo 1 cambio por corrida (ahora todos); día de menos por cambio de horario; cliente `S&JS` leído como `S`;
  `LOAD ID # 123`, `Load ID : 123`, cargas CITI y guías FedEx se trataban como routing → salían como "REMOVED" en vez de "SHIPPED".
- **Formatos Cfrm vistos en el portal real:** cita = CS…, LOAD ID…, CT…, tracking/guía ≥10 dígitos; routing = RTS…, REF#…, D…, PJ#…, 6–9 dígitos (BURL/NEWT, sin cita). CONFIRMADO por el usuario.
- **Actualización:** botón manual + casilla "Auto cada 5 min" (corre en el backend mientras esté encendido). Importación del histórico `ROUTING_COMPLETED` por CSV desde la pestaña "Cerradas".
- **Verificado:** conexión real OK (535 órdenes leídas, primera sincronización hecha). 80 pruebas pasan. Build y lint OK.
- **Importante:** el backend debe correr con el venv (`backend\venv\Scripts\python -m uvicorn ...`); el Python global no tiene httpx/tzdata/dotenv.
- **Pendiente:** importar el CSV del histórico (lo hace el usuario con el botón); revisión visual; el Google Sheet queda como respaldo.

### 2026-11-09 · Plataforma modular "Golden State Project Manager - Wiesner" (v0.10.0)
- Renombrado: `frontend/paletizador-web` → `frontend/gs-project-manager` (con `git mv`, historial conservado). Títulos de app y API actualizados.
- Frontend convertido en shell con React Router (`react-router-dom` 7): inicio con tarjetas de módulos (`/`), Paletizador (`/palletizer`), Órdenes abiertas (`/open-orders`, en construcción). Idioma y tema globales, recordados en el navegador.
- Backend reorganizado por módulo; endpoints movidos a `/api/palletizer/parse-pdf` y `/api/palletizer/pack` (las rutas viejas `/api/pack` ya no existen).
- Corregido: el cliente API leía el cuerpo de la respuesta dos veces en errores. Lint del frontend limpio (antes 8 errores).
- Verificado: 28 pruebas pasan, `npm run build` OK, `npm run lint` OK, flujo PDF → pack por API OK. Pendiente: revisión visual en navegador.
- `.claude/settings.local.json` fuera de Git.

### 2026-11-09 · Legibilidad del sidebar
- Fuentes del sidebar más grandes (etiquetas 9-10px → 11-12px, campos → 14px); PO/DC de cada SKU como etiqueta visible. Sidebar 390 → 420px. Build OK.
- En discusión: convertir el frontend en un "shell" con módulos (Paletizador + Órdenes abiertas Wiesner) y renombrar a "Golden State Project Manager - Wiesner".

### 2026-11-09 · Colores por PO + SKU
- **Bug corregido:** el color se asignaba solo por SKU; el mismo SKU en dos POs (p. ej. 6B4543MS en 02530856 y 02530857) salía del mismo color. Ahora la clave de color es PO + SKU y nunca se repite (paleta de 30 + tonos generados).
- Leyenda del visor: solo lo presente en el pallet visible, con su PO.
- Aclarado con el usuario: la PO es lo que separa la mercancía. Una misma PO puede venir en varios PikTik (cantidades distintas) y esos SÍ se combinan; POs distintas nunca.
- Pallets a media altura en MARS125 (layouts E–I): son remanentes de POs con UN solo SKU; no hay otro SKU de la misma PO para completarlos y el conteo ya es el mínimo posible (p. ej. 1000/60 → 17). No es un defecto del motor.
- Pruebas: 28 pasan (nuevas: misma PO en 2 PikTik comparte pallet; POs distintas no). Build OK.

### 2026-11-09 · Motor de empaque propio + parser multi-PikTik (v0.9.0)
- **Motor nuevo** (`layer_patterns.py`, `packing_service.py`, `physics_engine.py`): se elimina `py3dbp`.
  Patrón de capas óptimo por SKU (DP guillotina) + capas con orientaciones mixtas cuando suman cajas;
  remanentes se colocan caja a caja en huecos de pallets existentes (gravedad + soporte + peso);
  consolidación que vacía pallets poco llenos. Agrupa por (DC, PO).
- **Bug grave corregido:** `py3dbp` duplicaba cajas en pallets mixtos (MARS125: 1.913 colocadas vs 1.785 pedidas, 39 pallets).
  Ahora 1.785/1.785 y 32 pallets, ocupación de volumen 85 %.
- **Parser PDF** (`pdf_service.py`): agrupa páginas por PikTik → `orders[]` con PO, DC, destino e ítems.
  Cantidad = columna "Cases" (la fila "Cartons" redondea por talla). SKU limpio (sin MPO/color/descripción);
  variantes del mismo código se desambiguan. Advierte si la suma no cuadra con el TOTAL del PDF.
- **API:** `/api/parse-pdf` devuelve `{company, cust_no, orders[], warnings[]}`. `/api/pack` acepta `po/piktik/ship_to_dc`
  por ítem y devuelve además `unplaced`, `groups`, `summary`; cada pallet trae `po`, `ship_to_dc`, `pallet_type`, `volume_utilization_pct`.
- **Frontend:** modal de revisión por PikTik; filas con PO/DC; huella de layouts incluye PO/DC (trazabilidad);
  ya no se envía `max_weight_lbs`; aviso si hay cajas sin colocar.
- **Config:** `UMBRAL_MINIMO_SOPORTE` unificado en 0.65 (antes 0.65 y 0.75 a la vez).
- **Pruebas:** `backend/tests` (pytest, 26 pruebas pasan). PDFs reales opcionales vía `PIKTIK_PDF_DIR`.
  `npm run build` OK. Lint: 8 errores PREEXISTENTES en App.jsx/palletApi.js (no tocados).
- **Resultados (pallets, antes → ahora):** MARS125 39→32 · MARS120 32→25 · MARS240 8→18 (antes inflado: 151 cajas por 103 reales) · TJMA043 8→4.
- **Sin verificar:** dibujo 3D en navegador (solo validado geométricamente con tests).
- **Pendiente / decisiones abiertas:**
  - Rotación: se permiten las 6 orientaciones (cajas acostadas en capas). Confirmar si algún SKU exige "de pie" (hay parámetro `solo_de_pie`).
  - Segregación por DC en tráileres, partición de 26 posiciones y pestañas por tráiler.
  - `CFT_POR_PALLET = 130` es fijo en el frontend; usar volumen real del pallet.
  - Referencia tráiler 53': 26 pallets, ~42.000–45.000 lb de carga útil (`config.py`, sin confirmar como regla).
  - Lint preexistente; `claude.md` está en `.gitignore` y se llama en minúscula.

### 2026-11-09 · Línea base
- Diagnóstico del código heredado de Gemini: Top-Off, Fase 3 y nivelador de capas descritos en `claude.md` NO existían en el código.
- Se instaló pytest en el venv. Sin tests previos.
