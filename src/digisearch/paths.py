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
CANONICAL_DIR = DATA_DIR / "canonical"
CANONICAL_PRODUCTS_DIR = CANONICAL_DIR / "products"
SEARCH_DOCUMENTS_DIR = DATA_DIR / "search_documents"
SEARCH_DOCUMENTS_PRODUCT_DIR = SEARCH_DOCUMENTS_DIR / "products"


for directory in (DATA_DIR, LOG_DIR, CANONICAL_DIR, CANONICAL_PRODUCTS_DIR,SEARCH_DOCUMENTS_DIR, SEARCH_DOCUMENTS_PRODUCT_DIR):
    directory.mkdir(parents=True, exist_ok=True)
