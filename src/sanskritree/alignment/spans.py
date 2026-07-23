from __future__ import annotations
import json
import uuid

RELATIONS = {"one_to_one", "one_to_many", "many_to_one", "many_to_many", "implicit", "expanded", "omitted", "commentarial", "uncertain"}


def add_alignment(conn, translation_id: str, source_start: int, source_end: int, target_start: int, target_end: int, relation: str, confidence: float | None, evidence: dict, review_status: str = "unreviewed") -> str:
    if relation not in RELATIONS:
        raise ValueError(f"unknown alignment relation: {relation}")
    if source_start > source_end or target_start > target_end:
        raise ValueError("alignment spans must be ordered")
    alignment_id = str(uuid.uuid4())
    conn.execute("INSERT INTO alignments VALUES (?,?,?,?,?,?,?,?,?,?)", (alignment_id, translation_id, source_start, source_end, target_start, target_end, relation, confidence, json.dumps(evidence, sort_keys=True), review_status))
    conn.commit()
    return alignment_id
