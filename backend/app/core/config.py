from typing import List

# Constantes del Servidor y CORS
ALLOWED_ORIGINS: List[str] = ["*"]

# Tolerancias del Motor Físico (Pulgadas)
EPSILON_SOLAPE: float = 0.01            # solape horizontal mínimo para considerar contacto
TOLERANCIA_ALTURA_SOPORTE: float = 0.15  # una caja inferior "sostiene" si su techo está a esta distancia
UMBRAL_MINIMO_SOPORTE: float = 0.65      # 65% de la base debe estar apoyada (regla única del proyecto)
TOLERANCIA_DESBALANCE_COG: float = 0.15  # Máximo 15% de desviación del centro

# Límites Operativos de Pallets por Defecto (pallet GMA #2 four-way, 48x40 in)
DEFAULT_MAX_WEIGHT_LBS = None  # sin límite hasta confirmar la regla de negocio
DEFAULT_BASE_HEIGHT_IN: float = 5.5
DEFAULT_MAX_TOTAL_HEIGHT_IN: float = 85.0

# Referencia de tráiler de 53' (valores de industria, NO reglas de negocio confirmadas)
TRAILER_FLOOR_POSITIONS: int = 26         # pallets 48x40 en una sola capa
TRAILER_PAYLOAD_REF_LBS: float = 45000.0  # carga útil típica de un dry van de 53' (42,000-45,000 lb)
