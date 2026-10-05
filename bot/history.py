import sqlite3
from datetime import date

from .models import Offer


def connect(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute(
        """CREATE TABLE IF NOT EXISTS prijzen (
            datum TEXT, winkel TEXT, item TEXT, product TEXT, prijs REAL, normaal_prijs REAL,
            UNIQUE(datum, winkel, item, product))"""
    )
    return db


def lowest_known(db: sqlite3.Connection, item: str) -> float | None:
    row = db.execute("SELECT MIN(prijs) FROM prijzen WHERE item = ?", (item,)).fetchone()
    return row[0]


def record(db: sqlite3.Connection, offers: list[Offer]) -> None:
    today = date.today().isoformat()
    db.executemany(
        "INSERT OR IGNORE INTO prijzen VALUES (?,?,?,?,?,?)",
        [(today, o.winkel, o.item, o.product, o.prijs, o.normaal_prijs) for o in offers],
    )
    db.commit()
