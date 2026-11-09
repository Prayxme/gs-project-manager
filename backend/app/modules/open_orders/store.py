"""
Persistencia del monitor en SQLite (archivo local backend/data/gs.db, fuera de Git).

Tablas:
  orders         foto actual de las órdenes abiertas (una fila por pick ticket)
  events         historial de cambios, con fecha y hora (UTC)
  closed_orders  órdenes que salieron del portal (enviadas, removidas, canceladas)
  runs           bitácora de cada actualización (éxito/error)
  settings       preferencias (p. ej. actualización automática)
"""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from app.modules.open_orders import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    pick_ticket     TEXT PRIMARY KEY,
    data            TEXT NOT NULL,
    first_seen      TEXT NOT NULL,
    last_seen       TEXT NOT NULL,
    last_change     TEXT NOT NULL DEFAULT '',
    last_change_at  TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ts           TEXT NOT NULL,
    pick_ticket  TEXT NOT NULL,
    po           TEXT,
    cust         TEXT,
    event        TEXT NOT NULL,
    old_value    TEXT,
    new_value    TEXT
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
CREATE TABLE IF NOT EXISTS closed_orders (
    pick_ticket   TEXT PRIMARY KEY,
    date_removed  TEXT NOT NULL,
    removed_at    TEXT,
    final_status  TEXT NOT NULL,
    reason        TEXT NOT NULL,
    po            TEXT, cust TEXT, ship_date TEXT, cancel_date TEXT,
    cfrm_number   TEXT, appt_date TEXT, notes TEXT,
    source        TEXT NOT NULL DEFAULT 'monitor'
);
CREATE TABLE IF NOT EXISTS runs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at   TEXT NOT NULL,
    finished_at  TEXT,
    trigger      TEXT NOT NULL,
    ok           INTEGER NOT NULL DEFAULT 0,
    total        INTEGER, new_count INTEGER, changed_count INTEGER, removed_count INTEGER,
    error        TEXT
);
CREATE TABLE IF NOT EXISTS settings (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);
"""


class Store:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path or config.DB_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.conn() as c:
            c.executescript(SCHEMA)

    @contextmanager
    def conn(self) -> Iterator[sqlite3.Connection]:
        c = sqlite3.connect(self.path, timeout=30)
        c.row_factory = sqlite3.Row
        try:
            yield c
            c.commit()
        except Exception:
            c.rollback()
            raise
        finally:
            c.close()

    # -- órdenes -----------------------------------------------------------------
    def load_orders(self) -> Dict[str, Dict]:
        with self.conn() as c:
            rows = c.execute("SELECT * FROM orders").fetchall()
        out = {}
        for r in rows:
            d = json.loads(r["data"])
            d.update(first_seen=r["first_seen"], last_seen=r["last_seen"],
                     last_change=r["last_change"], last_change_at=r["last_change_at"])
            out[r["pick_ticket"]] = d
        return out

    # -- configuración ---------------------------------------------------------------
    def get_setting(self, key: str, default: str = "") -> str:
        with self.conn() as c:
            r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

    def set_setting(self, key: str, value: str) -> None:
        with self.conn() as c:
            c.execute("INSERT INTO settings(key, value) VALUES(?, ?) "
                      "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    # -- consultas -------------------------------------------------------------------
    def events(self, limit: int = 500, since: Optional[str] = None) -> List[Dict]:
        q, args = "SELECT * FROM events", []
        if since:
            q += " WHERE ts >= ?"
            args.append(since)
        q += " ORDER BY ts DESC, id DESC LIMIT ?"
        args.append(limit)
        with self.conn() as c:
            return [dict(r) for r in c.execute(q, args).fetchall()]

    def closed(self, limit: int = 2000) -> List[Dict]:
        with self.conn() as c:
            rows = c.execute("SELECT * FROM closed_orders ORDER BY date_removed DESC, pick_ticket DESC LIMIT ?",
                             (limit,)).fetchall()
        return [dict(r) for r in rows]

    def closed_pick_tickets(self) -> set:
        with self.conn() as c:
            return {r[0] for r in c.execute("SELECT pick_ticket FROM closed_orders").fetchall()}

    def last_runs(self, limit: int = 1) -> List[Dict]:
        with self.conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

    def last_ok_run(self) -> Optional[Dict]:
        with self.conn() as c:
            r = c.execute("SELECT * FROM runs WHERE ok=1 ORDER BY id DESC LIMIT 1").fetchone()
        return dict(r) if r else None
