"""Token/span alignment between Sanskrit source and English translation."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone


def record_alignment(
    conn,
    translation_id: str,
    *,
    source_token_id: str | None = None,
    source_span_start: int = 0,
    source_span_end: int = 0,
    english_span: str = "",
    lexical_sense_id: str | None = None,
    relation: str = "direct",
    confidence: float = 1.0,
) -> str:
    """Record one alignment between a source span and an English span."""
    aid = str(uuid.uuid4())
    conn.execute("""INSERT OR REPLACE INTO translation_alignment
        (alignment_id, translation_id, source_token_id,
         source_span_start, source_span_end,
         english_span, lexical_sense_id,
         relation, confidence, review_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'unreviewed')""",
        (aid, translation_id, source_token_id,
         source_span_start, source_span_end,
         english_span, lexical_sense_id,
         relation, confidence))
    conn.commit()
    return aid


def align_from_assignment(
    conn,
    translation_id: str,
    passage_reading_id: str,
    assignment: dict,
    english_segments: list[dict],
):
    """Create alignments from a factor graph assignment + English segments.

    english_segments: list of dicts with keys:
        - text: the English span
        - source_token_indices: list of token indices covered
        - relation: direct|implicit|paraphrase|omitted|added
        - confidence: float
    """
    for seg in english_segments:
        source_token_id = None
        span_start = 0
        span_end = 0

        # Find source token IDs for the referenced indices
        for idx in seg.get("source_token_indices", []):
            var_name = f"token_{idx}"
            choice = assignment.get(var_name)
            if choice:
                occ_id = choice.payload.get("occurrence_id", "")
                if occ_id:
                    row = conn.execute(
                        "SELECT token_id FROM tokens WHERE token_id LIKE ?",
                        (f"{passage_reading_id}.t{idx}",)
                    ).fetchone()
                    if row:
                        source_token_id = row[0]

        record_alignment(
            conn, translation_id,
            source_token_id=source_token_id,
            source_span_start=span_start,
            source_span_end=span_end,
            english_span=seg["text"],
            relation=seg.get("relation", "direct"),
            confidence=seg.get("confidence", 0.8),
        )


def get_alignments_for_translation(conn, translation_id: str) -> list[dict]:
    """Get all alignments for a translation, grouped by relation type."""
    rows = conn.execute("""
        SELECT alignment_id, source_token_id, english_span,
               relation, confidence, review_status
        FROM translation_alignment
        WHERE translation_id = ?
        ORDER BY source_span_start
    """, (translation_id,)).fetchall()

    return [dict(r) for r in rows]


def alignment_coverage_report(conn, translation_id: str, n_source_tokens: int) -> dict:
    """Report what percentage of source tokens are covered by alignments."""
    alignments = get_alignments_for_translation(conn, translation_id)
    covered_tokens = set()
    relations = {}

    for a in alignments:
        if a["source_token_id"]:
            covered_tokens.add(a["source_token_id"])
        rel = a["relation"]
        relations[rel] = relations.get(rel, 0) + 1

    return {
        "total_alignments": len(alignments),
        "covered_tokens": len(covered_tokens),
        "total_tokens": n_source_tokens,
        "coverage_pct": round(len(covered_tokens) / max(n_source_tokens, 1) * 100, 1),
        "relation_counts": relations,
    }
