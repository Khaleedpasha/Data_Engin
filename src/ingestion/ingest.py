from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "src" / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "src" / "data" / "processed"