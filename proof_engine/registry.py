"""
Term registry per Schema v3 §4.4.
Tradition-scoped: same IAST, different tradition → different TID.
"""

from typing import Optional
from . import db


def ensure_registered(conn, iast: str, tradition: str, **kw) -> int:
    """Register term if not exists. Return tid."""
    t = db.get_term(conn, iast, tradition)
    if t:
        return t.get("tid") or 0
    return db.register_term(conn, iast, tradition, **kw)


def register_dharmakirti_terms(conn) -> list[int]:
    """Bootstrap Dharmakīrti Phase 1 terms."""
    terms = [
        ("pratyakṣa", "dharmakirti"),
        ("kalpanā", "dharmakirti"),
        ("svalakṣaṇa", "dharmakirti"),
        ("arthakriyā", "dharmakirti"),
        ("pramāṇa", "dharmakirti"),
    ]
    return [ensure_registered(conn, iast, trad) for iast, trad in terms]


def register_nyaya_terms(conn) -> list[int]:
    """Bootstrap Nyāya Phase 1 terms."""
    terms = [
        ("pramāṇa", "nyaya"),
        ("saṃśaya", "nyaya"),
        ("vyāpti", "nyaya"),
        ("anumāna", "nyaya"),
        ("nigrahasthāna", "nyaya"),
    ]
    return [ensure_registered(conn, iast, trad) for iast, trad in terms]


def check_terms(conn, iast: str, tradition: str) -> Optional[int]:
    """Return tid if registered, else None. Pipeline blocks on unregistered."""
    t = db.get_term(conn, iast, tradition)
    return t.get("tid") if t else None
