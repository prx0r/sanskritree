from __future__ import annotations

from ..alignment.spans import add_alignment
from ..semantics.extraction import persist_frame
from ..semantics.schema import Entity, SemanticFrame
from ..translation.candidates import record_candidate, start_blind_run


def apply_annotations(conn, annotations: dict) -> dict[str, int]:
    """Apply explicit review records; no inference is performed here."""
    passage_id = annotations["passage_id"]
    translation_id = annotations["translation_id"]
    reading_id = annotations["reading_id"]
    if conn.execute("SELECT 1 FROM passage_readings WHERE reading_id=?", (reading_id,)).fetchone() is None:
        raise KeyError(f"unknown reading: {reading_id}")
    if conn.execute("SELECT 1 FROM translations WHERE translation_id=?", (translation_id,)).fetchone() is None:
        raise KeyError(f"unknown translation: {translation_id}")
    counts = {"alignments": 0, "candidates": 0, "frames": 0}
    for item in annotations.get("alignments", []):
        add_alignment(conn, translation_id, item["source_start"], item["source_end"], item["target_start"], item["target_end"], item["relation"], item.get("confidence"), item["evidence"], item.get("review_status", "unreviewed"))
        counts["alignments"] += 1
    candidates = annotations.get("blind_candidates", [])
    if candidates:
        run = start_blind_run(conn, passage_id, [candidate["profile"] for candidate in candidates], annotations.get("retrieval_results", []), model=None, prompt_version=annotations.get("prompt_version", "human-seed-v1"))
        for candidate in candidates:
            record_candidate(conn, run, candidate["profile"], candidate["text"], senses=candidate.get("senses", []), parses=candidate.get("parses", []), ranking=candidate["ranking"])
            counts["candidates"] += 1
    for item in annotations.get("semantic_frames", []):
        frame = SemanticFrame(item["frame_id"], passage_id, item["source_span"], item["discourse_mode"], Entity(**item["subject"]), item["relation"], Entity(**item["object"]), item["explicitness"], item["confidence"], item.get("alternatives", []))
        persist_frame(conn, frame, item.get("review_status", "unreviewed"))
        counts["frames"] += 1
    return counts
