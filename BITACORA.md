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

## Registro

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
