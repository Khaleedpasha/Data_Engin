import pandas as pd

from src.utils.config import RAW_DIR, PROCESSED_DIR
from src.utils.logger import get_logger

logger = get_logger("ingestion")


def inspect_file(path):
    """Read one CSV and return a dict of basic quality stats."""
    df = pd.read_csv(path)
    stats = {
        "file": path.name,
        "rows": len(df),
        "columns": len(df.columns),
        "null_cells": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }
    logger.info(
        "%s | rows=%s cols=%s nulls=%s dups=%s",
        stats["file"], stats["rows"], stats["columns"],
        stats["null_cells"], stats["duplicate_rows"],
    )
    return stats


def main():
    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        logger.error("No CSV files found in %s", RAW_DIR)
        return

    logger.info("Found %s CSV files", len(csv_files))

    results = []
    for path in csv_files:
        try:
            results.append(inspect_file(path))
        except Exception as e:
            logger.error("Failed to read %s: %s", path.name, e)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(results)
    summary.to_csv(PROCESSED_DIR / "ingestion_summary.csv", index=False)
    logger.info("Summary saved to data/processed/ingestion_summary.csv")


if __name__ == "__main__":
    main()
    