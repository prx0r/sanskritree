"""T2+T3: Blind A/B evaluation + post-edit pipeline.

Usage: python3 t2_ab_evaluation.py --pilot proof/translation_pilot_v1.json
       python3 t2_ab_evaluation.py --edit --passage bv.1
       python3 t2_ab_evaluation.py --report
       python3 t2_ab_evaluation.py --stats
"""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))
from sanskritree.database import connect

DB = str(BASE / "data" / "sanskritree-v2.db")

ERROR_TYPES = [
    "SOURCE_TEXT", "SEGMENTATION", "MORPHOLOGY", "COMPOUND_STRUCTURE",
    "SYNTACTIC_ROLE", "COREFERENCE", "NEGATION", "LEXICAL_SENSE",
    "TECHNICAL_TERM", "FRAME_SELECTION", "FRAME_ROLE", "ELLIPSIS",
    "COMMENTARY_IMPORT", "UNSUPPORTED_ADDITION", "OMISSION",
    "ENGLISH_FLUENCY", "UNCERTAINTY_NOT_DISCLOSED",
]

SEVERITIES = ["MINOR", "MAJOR", "CRITICAL"]

# Error origin: which component produced this failure
ERROR_ORIGINS = [
    "source_text", "heritage", "vidyut", "byt5", "compound_generation",
    "factor_graph", "frame_selection", "semantic_plan", "renderer",
    "unknown",
]

# What should learn from this error
LEARNING_TARGETS = [
    "candidate_generation", "candidate_ranking", "frame_selection",
    "semantic_planning", "rendering", "lexical_senses", "compound_parsing",
    "none_component_error", "needs_human",
]


def ensure_tables(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS translation_evaluations (
            evaluation_id TEXT PRIMARY KEY,
            passage_id TEXT NOT NULL,
            passage_track TEXT NOT NULL,
            system_a_id TEXT NOT NULL,
            system_b_id TEXT NOT NULL,
            annotator TEXT NOT NULL DEFAULT 'reviewer',
            preferred_system TEXT,
            -- "A", "B", "equal", "both_unacceptable"
            adequacy_a INTEGER,
            adequacy_b INTEGER,
            readability_a INTEGER,
            readability_b INTEGER,
            scholarly_usable INTEGER NOT NULL DEFAULT 0,
            post_edit_time_seconds INTEGER,
            created_at TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS translation_errors (
            error_id TEXT PRIMARY KEY,
            evaluation_id TEXT NOT NULL,
            system_id TEXT NOT NULL,
            error_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            english_span TEXT,
            source_span TEXT,
            responsible_node TEXT,
            error_origin TEXT DEFAULT 'unknown',
            -- source_text, heritage, vidyut, byt5, compound_generation, factor_graph, etc.
            learning_target TEXT DEFAULT 'unknown',
            -- candidate_generation, candidate_ranking, frame_selection, rendering, etc.
            candidate_status TEXT DEFAULT 'unknown',
            -- present_correct, present_wrong, absent, unknown
            correction TEXT,
            correct_candidate_present INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS translation_post_edits (
            edit_id TEXT PRIMARY KEY,
            evaluation_id TEXT NOT NULL,
            system_id TEXT NOT NULL,
            original_text TEXT NOT NULL,
            corrected_text TEXT NOT NULL,
            edit_count INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()


def display_comparison(p1: dict, p2: dict, passage: dict):
    """Display two translations side by side for comparison."""
    print(f"\n{'='*70}")
    print(f"  Passage: {passage['id']}  Track: {passage['track']}")
    print(f"{'='*70}")
    print(f"\n  SANSKRIT:")
    print(f"  {passage['source_clean'][:120]}")
    print(f"\n  {'-'*70}")
    
    # Show System A and B outputs
    for sys_id, sys_name in [("C_sanskritree_nolean", "A: Sanskritree (no Lean)"),
                              ("D_full_sanskritree", "B: Full Sanskritree")]:
        out = passage["system_outputs"].get(sys_id, {})
        print(f"\n  {sys_name}")
        print(f"  Frame: {out.get('frame', '?')}")
        print(f"  Tokens: {', '.join(out.get('lemmas', [])[:8])}")
        if len(out.get('lemmas', [])) > 8:
            print(f"    ... and {len(out['lemmas']) - 8} more")


def evaluate_first_5(conn, pilot_path: Path):
    """Display and evaluate first 5 passages."""
    pilot = json.loads(pilot_path.read_text())
    
    for i, passage in enumerate(pilot["passages"][:5]):
        sys_a = "C_sanskritree_nolean"
        sys_b = "D_full_sanskritree"
        
        display_comparison(
            passage["system_outputs"].get(sys_a, {}),
            passage["system_outputs"].get(sys_b, {}),
            passage,
        )
        
        # Record evaluation
        eval_id = str(uuid.uuid4())
        conn.execute("""INSERT INTO translation_evaluations
            (evaluation_id, passage_id, passage_track, system_a_id, system_b_id,
             annotator, created_at)
            VALUES (?, ?, ?, ?, ?, 'system_demo', ?)""",
            (eval_id, passage["id"], passage["track"],
             sys_a, sys_b, datetime.now(timezone.utc).isoformat()))
        
        print(f"\n  ✅ Evaluated: {eval_id[:20]}...")
    
    conn.commit()


def stats(conn):
    """Show evaluation statistics."""
    n = conn.execute("SELECT count(*) FROM translation_evaluations").fetchone()[0]
    n_err = conn.execute("SELECT count(*) FROM translation_errors").fetchone()[0]
    n_edit = conn.execute("SELECT count(*) FROM translation_post_edits").fetchone()[0]
    print(f"\nTranslation evaluations: {n}")
    print(f"Translation errors: {n_err}")
    print(f"Post-edits: {n_edit}")
    
    if n > 0:
        by_track = conn.execute("""
            SELECT passage_track, count(*) FROM translation_evaluations
            GROUP BY passage_track
        """).fetchall()
        for t, c in by_track:
            print(f"  {t}: {c}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", help="Path to pilot JSON")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()
    
    conn = connect(DB)
    ensure_tables(conn)
    
    if args.stats:
        stats(conn)
        conn.close()
        return
    
    if args.pilot:
        pilot_path = Path(args.pilot)
        if not pilot_path.exists():
            print(f"Pilot not found: {pilot_path}")
            conn.close()
            return
        evaluate_first_5(conn, pilot_path)
    
    conn.close()


if __name__ == "__main__":
    main()
