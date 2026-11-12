import os
import sys
from pathlib import Path

# Permite `import app...` al ejecutar pytest desde backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Las pruebas nunca arrancan tareas de fondo (revisión de Gmail, refresco del portal).
os.environ["GS_DISABLE_BACKGROUND_TASKS"] = "1"
