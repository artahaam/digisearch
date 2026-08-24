from pathlib import Path

def find_project_root() -> Path:
    marker = "pyproject.toml"
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / marker).exists():
            return parent
    raise RuntimeError(f"Could not find {marker}")

PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
LOG_DIR = DATA_DIR / "logs"
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_PRODUCTS_DIR = PROCESSED_DIR / "products"


for directory in (DATA_DIR, LOG_DIR, PROCESSED_DIR, PROCESSED_PRODUCTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
