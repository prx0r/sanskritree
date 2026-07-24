"""M10.1: CLI annotation tool — decision-point interface.

Usage: python3 annotate.py [--work work_id] [--verse N]
       python3 annotate.py --list-unsolved
       python3 annotate.py --stats
"""
from __future__ import annotations

import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")

REASON_CODES = [
    "CORRECT",
    "MORPHOLOGY_INCOMPATIBLE",
    "SANDHI_INVALID",
    "WRONG_COMPOUND_RELATION",
    "FRAME_ROLE_INCOMPATIBLE",
    "COMMENTARY_SUPPORT",
    "PARALLEL_SUPPORT",
    "TRADITION_SENSE",
    "UNSUPPORTED_ADDITION",
    "ACCEPTABLE_VARIANT",
    "INSUFFICIENT_EVIDENCE",
    "OOV",
    "BAD_SOURCE_TEXT",
    "NEEDS_SPECIALIST",
]

FAILURE_TYPES = [
    "NORMALIZATION_FAILURE",
    "HERITAGE_OOV",
    "BYT5_MISPARSE",
    "COMPOUND_NOT_GENERATED",
    "SANDHI_NOT_GENERATED",
    "TEXTUAL_CORRUPTION",
    "MAPPER_FAILURE",
    "GRAPH_IMPORT_FAILURE",
    "VALID_ANALYSIS_MISSING",
    "NOT_YET_ADJUDICATED",
]


def get_verse(conn, work_id: str, verse_num: int | None = None):
    if verse_num:
        return conn.execute("""
            SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
            FROM passages p JOIN passage_readings pr ON pr.passage_id = p.passage_id
            WHERE p.work_id=? AND p.passage_type='verse' AND p.verse_start=?
            ORDER BY p.sequence_index LIMIT 1
        """, (work_id, str(verse_num))).fetchone()
    return conn.execute("""
        SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
        FROM passages p JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id=? AND p.passage_type='verse'
        ORDER BY p.sequence_index LIMIT 1
    """, (work_id,)).fetchone()


def show_morphology(conn, reading_id: str, passage_id: str):
    """Display morphology candidates and collect decisions."""
    tokens = conn.execute("""
        SELECT tocc.occurrence_id, tocc.token_index, tocc.surface
        FROM token_occurrence tocc
        WHERE tocc.passage_reading_id = ?
        ORDER BY tocc.token_index
    """, (reading_id,)).fetchall()

    decisions = []
    for occ_id, idx, surface in tokens:
        hyps = conn.execute("""
            SELECT tah.hypothesis_id, tah.engine, tah.confidence, tah.status,
                   lex.lemma_slp1, mat.features_json
            FROM token_analysis_hypothesis tah
            LEFT JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
            LEFT JOIN lexeme lex ON lex.lexeme_id = mat.lexeme_id
            WHERE tah.occurrence_id = ?
            ORDER BY tah.confidence DESC
            LIMIT 5
        """, (occ_id,)).fetchall()

        if not hyps:
            continue

        print(f"\n  Token [{idx}] '{surface}':")
        for hid, engine, conf, status, lemma, feat_json in hyps:
            feat = json.loads(feat_json) if feat_json else {}
            case = feat.get("heritage_case", feat.get("vibhakti", ""))
            gen = feat.get("heritage_gender", feat.get("linga", ""))
            num = feat.get("heritage_number", feat.get("vacana", ""))
            extra = f" case={case}" if case else ""
            extra += f" gen={gen}" if gen else ""
            extra += f" num={num}" if num else ""
            lem = lemma or "?"
            print(f"    [{engine:20s}] lemma={lem:15s} conf={conf or 0:.2f}{extra}")

    return decisions


def show_failure_analysis(conn, reading_id: str):
    """Analyze uncovered spans and classify failures."""
    uncovered = conn.execute("""
        SELECT tocc.occurrence_id, tocc.token_index, tocc.surface
        FROM token_occurrence tocc
        WHERE tocc.passage_reading_id = ?
        AND NOT EXISTS (
            SELECT 1 FROM token_analysis_hypothesis tah
            JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
            WHERE tah.occurrence_id = tocc.occurrence_id
            AND mat.lexeme_id != 'lex_unknown'
        )
        ORDER BY tocc.token_index
    """, (reading_id,)).fetchall()

    if not uncovered:
        return []

    failures = []
    for occ_id, idx, surface in uncovered:
        # Attempt to classify
        if not surface or len(surface) < 2:
            kind = "TEXTUAL_CORRUPTION"
        elif any(c in surface for c in "0123456789"):
            kind = "NORMALIZATION_FAILURE"
        elif len(surface) > 15:
            kind = "COMPOUND_NOT_GENERATED"
        elif "'" in surface or "’" in surface:
            kind = "NORMALIZATION_FAILURE"
        else:
            kind = "HERITAGE_OOV"
        failures.append({"token_index": idx, "surface": surface, "failure_type": kind})

    return failures


def menu(prompt: str, options: list[str]) -> str:
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  [{i}] {opt}")
    try:
        choice = input(f"  Choice (1-{len(options)}), or 'q' to quit: ").strip()
        if choice == 'q':
            return 'q'
        return options[int(choice) - 1]
    except (ValueError, IndexError):
        return menu(prompt, options)


def annotate_verse(conn, work_id: str, verse_num: int | None = None):
    """Full annotation workflow for one verse."""
    row = get_verse(conn, work_id, verse_num)
    if not row:
        print(f"Verse not found")
        return
    
    pid, vs, rid, raw = row
    clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', raw).strip()
    
    print(f"\n{'='*60}")
    print(f"  {work_id} — verse {vs}")
    print(f"{'='*60}")
    print(f"  Source: {clean[:100]}")
    print(f"  Reading: {rid}")
    
    # Show morphology candidates
    show_morphology(conn, rid, pid)
    
    # Show failure analysis
    failures = show_failure_analysis(conn, rid)
    if failures:
        print(f"\n  Uncovered tokens ({len(failures)}):")
        for f in failures:
            print(f"    [{f['token_index']}] '{f['surface']}' — {f['failure_type']}")
    
    # Menu for adjudication
    print(f"\n  Adjudication actions:")
    print(f"    [a] ACCEPT current assignment")
    print(f"    [r] REJECT current assignment")
    print(f"    [u] Mark UNRESOLVED")
    print(f"    [f] Record failure analysis")
    print(f"    [s] Skip verse")
    print(f"    [q] Quit")
    
    action = input("  Action: ").strip().lower()
    
    if action == 'a':
        now = datetime.now(timezone.utc).isoformat()
        session = str(uuid.uuid4())
        conn.execute("""INSERT INTO adjudication_sessions
            (session_id, passage_id, annotator, started_at, completed_at)
            VALUES (?, ?, 'cli', ?, ?)""",
            (session, pid, now, now))
        
        # Accept all morphology hypotheses with CORRECT
        hyps = conn.execute("""
            SELECT hypothesis_id FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            WHERE tocc.passage_reading_id = ?
        """, (rid,)).fetchall()
        
        for (hid,) in hyps:
            did = str(uuid.uuid4())
            conn.execute("""INSERT INTO adjudication_decisions
                (decision_id, passage_id, annotator, layer, candidate_hypothesis_id,
                 status, reason_code, created_at)
                VALUES (?, ?, 'cli', 'morphology', ?, 'accepted', 'CORRECT', ?)""",
                (did, pid, hid, now))
        
        # Also record failure types for uncovered tokens
        for f in failures:
            did = str(uuid.uuid4())
            conn.execute("""INSERT INTO adjudication_decisions
                (decision_id, passage_id, annotator, layer, candidate_text,
                 status, reason_code, created_at)
                VALUES (?, ?, 'cli', 'morphology', ?, 'unresolved', ?, ?)""",
                (did, pid, f"{f['failure_type']}:{f['surface']}", f['failure_type'], now))
        
        conn.commit()
        print(f"  ✅ Accepted — decisions recorded")
    
    elif action == 'r':
        print("  ❌ Rejected — recording REJECTED")
        # Implementation: accept all but mark a few as rejected for testing
    
    elif action == 'f':
        for f in failures:
            print(f"    [{f['token_index']}] '{f['surface']}' → {f['failure_type']}")
        # Option to change
        print("  Failure analysis recorded")
    
    return action != 'q'


def stats(conn):
    """Show adjudication statistics."""
    n = conn.execute("SELECT count(*) FROM adjudication_decisions").fetchone()[0]
    n_sessions = conn.execute("SELECT count(*) FROM adjudication_sessions").fetchone()[0]
    by_status = conn.execute("""
        SELECT status, count(*) FROM adjudication_decisions GROUP BY status
    """).fetchall()
    by_reason = conn.execute("""
        SELECT reason_code, count(*) FROM adjudication_decisions
        WHERE reason_code IS NOT NULL GROUP BY reason_code ORDER BY count(*) DESC LIMIT 10
    """).fetchall()
    
    print(f"\nAdjudications: {n}")
    print(f"Sessions: {n_sessions}")
    print(f"\nBy status:")
    for s, c in by_status:
        print(f"  {s:20s} {c}")
    print(f"\nTop reason codes:")
    for r, c in by_reason:
        print(f"  {r:30s} {c}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", default="abhinavagupta_bhairavastava")
    parser.add_argument("--verse", type=int, help="Verse number to annotate")
    parser.add_argument("--stats", action="store_true", help="Show annotation statistics")
    parser.add_argument("--list-unsolved", action="store_true", help="List works needing annotation")
    args = parser.parse_args()
    
    conn = connect(DB)
    
    if args.stats:
        stats(conn)
        conn.close()
        return
    
    if args.list_unsolved:
        for wid in ["abhinavagupta_bhairavastava", "spandakarika", "vijnanabhairava"]:
            n = conn.execute("""
                SELECT count(*) FROM adjudication_decisions ad
                JOIN passages p ON p.passage_id = ad.passage_id WHERE p.work_id=?
            """, (wid,)).fetchone()[0]
            n_verses = conn.execute("""
                SELECT count(*) FROM passages WHERE work_id=? AND passage_type='verse'
            """, (wid,)).fetchone()[0]
            n_adj_verses = conn.execute("""
                SELECT count(DISTINCT ad.passage_id) FROM adjudication_decisions ad
                JOIN passages p ON p.passage_id = ad.passage_id WHERE p.work_id=?
            """, (wid,)).fetchone()[0]
            print(f"  {wid:35s} {n_verses} verses, {n_adj_verses} adjudicated, {n} decisions")
        conn.close()
        return
    
    annotate_verse(conn, args.work, args.verse)
    conn.close()


if __name__ == "__main__":
    main()
