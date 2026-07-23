"""SQLite migration runner and small, explicit persistence API for the V2 pilot."""
from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path


def source_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def migrate(conn: sqlite3.Connection, migrations_dir: str | Path) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)")
    applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}
    for path in sorted(Path(migrations_dir).glob("*.sql")):
        if path.name in applied:
            continue
        conn.executescript(path.read_text(encoding="utf-8"))
        conn.execute("INSERT INTO schema_migrations VALUES (?, datetime('now'))", (path.name,))
        conn.commit()
