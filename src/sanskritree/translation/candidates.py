from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone


def start_blind_run(conn, passage_id: str, profiles: list[str], retrieval_results: list[dict], model: str | None = None, prompt_version: str = "v2") -> str:
    run_id = str(uuid.uuid4())
    conn.execute("INSERT INTO translation_runs VALUES (?,?,?,?,?,?,?,?)", (run_id, passage_id, "blind", model, prompt_version, json.dumps(retrieval_results, sort_keys=True), datetime.now(timezone.utc).isoformat(), None))
    conn.commit()
    return run_id


def record_candidate(conn, run_id: str, profile: str, text: str, *, senses: list[dict], parses: list[dict], ranking: dict) -> str:
    if not ranking.get("evidence"):
        raise ValueError("every candidate requires retrieval or philological evidence")
    candidate_id = str(uuid.uuid4())
    conn.execute("INSERT INTO translation_candidates VALUES (?,?,?,?,?,?,?,?)", (candidate_id, run_id, profile, text, json.dumps(senses), json.dumps(parses), json.dumps(ranking, sort_keys=True), 1))
    conn.commit()
    return candidate_id


def reveal_reference(conn, run_id: str) -> None:
    row = conn.execute("SELECT reference_revealed_at FROM translation_runs WHERE run_id=?", (run_id,)).fetchone()
    if row is None:
        raise KeyError(run_id)
    if row[0] is not None:
        raise ValueError("reference already revealed; blind record remains immutable")
    conn.execute("UPDATE translation_runs SET reference_revealed_at=? WHERE run_id=?", (datetime.now(timezone.utc).isoformat(), run_id))
    conn.commit()
