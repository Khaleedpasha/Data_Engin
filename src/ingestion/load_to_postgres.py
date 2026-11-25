import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from src.utils.config import (
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, PROCESSED_DIR,
)
from src.utils.logger import get_logger

logger = get_logger("load")


def get_engine():
    url = URL.create(
        "postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
    )
    return create_engine(url)


def main():
    files = sorted(PROCESSED_DIR.glob("*_clean.csv"))
    if not files:
        logger.error("No clean files in %s. Run the cleaning step first.", PROCESSED_DIR)
        return

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS staging"))

    for path in files:
        table = path.stem.replace("_clean", "")
        try:
            df = pd.read_csv(path)
            df.to_sql(
                table, engine, schema="staging",
                if_exists="replace", index=False, chunksize=10000,
            )
            logger.info("Loaded staging.%s (%s rows)", table, len(df))
        except Exception as e:
            logger.error("Failed to load %s: %s", table, e)


if __name__ == "__main__":
    main()