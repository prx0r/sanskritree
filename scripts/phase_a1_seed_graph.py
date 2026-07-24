"""Phase A1: Apply ontology migration and seed from existing token_analyses."""
from __future__ import annotations

import json
import hashlib
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect, migrate


def features_hash(features: dict) -> str:
    """Deterministic hash of grammatical features for dedup."""
    raw = json.dumps(features, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def seed_lexemes(conn):
    """Extract unique lemmas from token_analyses into lexeme table."""
    rows = conn.execute("""
        SELECT DISTINCT ta.lemma
        FROM token_analyses ta
        WHERE ta.lemma IS NOT NULL AND ta.lemma != ''
    """).fetchall()

    count = 0
    for (lemma,) in rows:
        lid = f"lex_{lemma}"
        conn.execute("""INSERT OR IGNORE INTO lexeme
            (lexeme_id, lemma_slp1, pos, created_at)
            VALUES (?, ?, ?, ?)""",
            (lid, lemma, "unknown", datetime.now(timezone.utc).isoformat()))
        count += 1
    print(f"  Lexemes: {count} unique lemmas seeded")


def seed_analysis_types(conn):
    """Extract unique (lemma + features) combos as reusable analysis types."""
    rows = conn.execute("""
        SELECT DISTINCT ta.lemma, ta.features_json
        FROM token_analyses ta
        WHERE ta.lemma IS NOT NULL AND ta.lemma != ''
    """).fetchall()

    count = 0
    for lemma, feat_json in rows:
        features = json.loads(feat_json) if feat_json else {}
        fhash = features_hash(features)
        lid = f"lex_{lemma}"
        aid = f"mat_{lemma}_{fhash}"
        conn.execute("""INSERT OR IGNORE INTO morph_analysis_type
            (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
            VALUES (?, ?, ?, ?, ?)""",
            (aid, lid, json.dumps(features, sort_keys=True), fhash,
             datetime.now(timezone.utc).isoformat()))
        count += 1
    print(f"  Analysis types: {count} unique (lemma + features) combos")


def seed_occurrences_and_hypotheses(conn):
    """Create token_occurrence rows and link to analysis types via hypotheses."""
    # Get all tokens with their analyses
    rows = conn.execute("""
        SELECT t.token_id, t.reading_id, t.token_index, t.surface,
               t.start_offset, t.end_offset, ta.analysis_id, ta.engine,
               ta.lemma, ta.features_json, ta.confidence
        FROM tokens t
        JOIN token_analyses ta ON ta.token_id = t.token_id
        ORDER BY t.reading_id, t.token_index, ta.analysis_id
    """).fetchall()

    occurrences = {}  # (reading_id, token_index) → occurrence_id
    hyp_count = 0
    occ_count = 0

    for tid, rid, idx, surface, start, end, aid, engine, lemma, feat_json, conf in rows:
        okey = (rid, idx)
        if okey not in occurrences:
            oid = f"occ_{rid}_{idx}"
            conn.execute("""INSERT OR IGNORE INTO token_occurrence
                (occurrence_id, passage_reading_id, token_index, surface, start_offset, end_offset)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (oid, rid, idx, surface, start, end))
            occurrences[okey] = oid
            occ_count += 1
        else:
            oid = occurrences[okey]

        # Find matching analysis type
        if lemma and lemma != '':
            features = json.loads(feat_json) if feat_json else {}
            fhash = features_hash(features)
            atype_id = f"mat_{lemma}_{fhash}"
            # Ensure it exists
            lid = f"lex_{lemma}"
            conn.execute("""INSERT OR IGNORE INTO morph_analysis_type
                (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (atype_id, lid, json.dumps(features, sort_keys=True), fhash,
                 datetime.now(timezone.utc).isoformat()))
        else:
            atype_id = None

        hid = f"hyp_{aid}"
        conn.execute("""INSERT OR IGNORE INTO token_analysis_hypothesis
            (hypothesis_id, occurrence_id, analysis_type_id, engine, confidence, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
            (hid, oid, atype_id, engine, conf, datetime.now(timezone.utc).isoformat()))
        hyp_count += 1

    print(f"  Occurrences: {occ_count}")
    print(f"  Hypotheses: {hyp_count}")


def main():
    print("=" * 60)
    print("PHASE A1 — Graph ontology seed")
    print("=" * 60)

    db_path = BASE / "data" / "sanskritree-v2.db"
    conn = connect(str(db_path))
    migrate(conn, BASE / "migrations")

    print("\n[1] Seeding lexemes...")
    seed_lexemes(conn)
    conn.commit()

    print("\n[2] Seeding analysis types...")
    seed_analysis_types(conn)
    conn.commit()

    print("\n[3] Seeding occurrences + hypotheses...")
    seed_occurrences_and_hypotheses(conn)
    conn.commit()

    # Stats
    for table in ["lexeme", "morph_analysis_type", "token_occurrence", "token_analysis_hypothesis"]:
        n = conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        print(f"\n  {table}: {n} rows")

    # Verify token_analysis_hypothesis linked to old token_analyses count
    old = conn.execute("SELECT count(*) FROM token_analyses").fetchone()[0]
    print(f"  token_analyses (original): {old} rows")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
