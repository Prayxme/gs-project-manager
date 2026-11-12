"""Reglas de negocio del Routing (RTS) de Wiesner, confirmadas por el usuario el 2026-11-12."""

# Pallet americano estándar GMA #2 four-way: 48 x 40 in, base 5.5 in, tope 85 in contando la base.
PALLET_ANCHO_IN = 40.0
PALLET_LARGO_IN = 48.0
PALLET_BASE_IN = 5.5
PALLET_ALTURA_MAX_IN = 85.0
PALLET_PESO_LB = 45                 # se suma por cada pallet enrutado

# CFT declarado = factor x nº de pallets.
CFT_POR_PALLET = {"BURL": 90, "MODE": 90}
CFT_POR_PALLET_DEFECTO = 130

# Máximo de pallets por RTS.
LIMITE_PALLETS = {"ROSS": 26, "DDSD": 26}
LIMITE_PALLETS_DEFECTO = 28

# ROSS / DDSD: un RTS debe declarar al menos esta cantidad de lb (ver rules/min_weight.py).
PESO_MINIMO_LB = {"ROSS": 3100, "DDSD": 3100}

# Clientes cuyos 2 primeros dígitos de la PO indican el DC: solo se juntan POs del mismo prefijo.
PREFIJO_PO_DC = ("TJMA", "MARS", "NEWT")
LARGO_PREFIJO_PO = 2
