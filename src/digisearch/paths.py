from pathlib import Path

def find_project_root() -> Path:
    marker = "pyproject.toml"
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / marker).exists():
            return parent
    raise RuntimeError(f"Could not find {marker}")

PROJECT_ROOT = find_project_root()
print(PROJECT_ROOT)
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = DATA_DIR / "logs"

for directory in (DATA_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)
