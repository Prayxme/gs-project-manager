import sys
from pathlib import Path

# Permite `import app...` al ejecutar pytest desde backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
