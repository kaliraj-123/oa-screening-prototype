from pathlib import Path
import sys

project_root = Path(__file__).resolve().parents[1]
backend_path = project_root / "backend"

sys.path.insert(0, str(backend_path))

from app.main import app