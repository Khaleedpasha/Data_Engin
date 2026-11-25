import logging
import os
import sys

import psycopg2
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("quality")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

CHECKS = {
    "staging.orders is not empty":
        "SELECT COUNT(*) = 0 FROM staging.orders",
    "no null order_id in staging.order_items":
        "SELECT COUNT(*) > 0 FROM staging.order_items WHERE order_id IS NULL",
    "no duplicate (order_id, order_item_id) in staging.order_items":
        """SELECT COUNT(*) > 0 FROM (
               SELECT order_id, order_item_id
               FROM staging.order_items
               GROUP BY order_id, order_item_id
               HAVING COUNT(*) > 1) d""",
}
# Each query returns TRUE when the check FAILS.


def main() -> None:
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )
    failed = False
    with conn.cursor() as cur:
        for name, query in CHECKS.items():
            cur.execute(query)
            if cur.fetchone()[0]:
                log.error("FAILED: %s", name)
                failed = True
            else:
                log.info("PASSED: %s", name)
    conn.close()
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()