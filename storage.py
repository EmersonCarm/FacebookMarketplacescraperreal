import sqlite3
from contextlib import contextmanager
from statistics import median

import config


SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    listing_id TEXT PRIMARY KEY,
    search_term TEXT NOT NULL,
    title TEXT,
    price INTEGER,
    url TEXT,
    location TEXT,
    first_seen TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(SCHEMA)
        conn.commit()


def is_new(listing_id: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM listings WHERE listing_id = ?", (listing_id,)
        ).fetchone()
        return row is None


def price_history(search_term: str) -> list[int]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT price FROM listings WHERE search_term = ? AND price IS NOT NULL",
            (search_term,),
        ).fetchall()
        return [r[0] for r in rows]


def median_price(search_term: str) -> float | None:
    hist = price_history(search_term)
    return median(hist) if hist else None


def save_listing(listing_id, search_term, title, price, url, location):
    with get_conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO listings
               (listing_id, search_term, title, price, url, location)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (listing_id, search_term, title, price, url, location),
        )
        conn.commit()
