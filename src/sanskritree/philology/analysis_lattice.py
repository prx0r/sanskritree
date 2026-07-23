from __future__ import annotations
import re
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Analysis:
    engine: str
    lemma: str | None
    features: dict
    confidence: float | None
    detail: dict


def whitespace_lattice(text: str) -> list[tuple[str, int, int, list[Analysis]]]:
    """Safe fallback: marks forms unknown instead of inventing parses."""
    return [(m.group(), m.start(), m.end(), [Analysis("fallback", None, {}, 0.0, {"reason": "no analyser configured"})]) for m in re.finditer(r"\S+", text)]


def persist_lattice(conn, reading_id: str, lattice: list[tuple[str, int, int, list[Analysis]]]) -> int:
    count = 0
    for index, (surface, start, end, analyses) in enumerate(lattice):
        token_id = f"{reading_id}.t{index}"
        conn.execute("INSERT OR REPLACE INTO tokens VALUES (?,?,?,?,?,?)", (token_id, reading_id, index, surface, start, end))
        for analysis in analyses:
            conn.execute("INSERT INTO token_analyses VALUES (?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), token_id, analysis.engine, analysis.lemma, __import__("json").dumps(analysis.features), __import__("json").dumps(analysis.detail), analysis.confidence, "unreviewed", None))
            count += 1
    conn.commit()
    return count
