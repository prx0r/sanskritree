"""Phase A5b: Direct compound hypothesis seeding for Bhairavastava.
Instead of auto-splitting (which requires IAST→SLP1 conversion matching the
lexeme table), we directly add the known compound alternative analyses."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect


def seed_compound_hypotheses(conn, work_id: str):
    """Add compound-level analysis hypotheses for tokens that need them."""
    now = datetime.now(timezone.utc).isoformat()

    # Ensure placeholder lexeme exists for compound references
    conn.execute("""INSERT OR IGNORE INTO lexeme
        (lexeme_id, lemma_slp1, pos, created_at)
        VALUES ('lex_unknown', '__unknown__', 'unknown', ?)""", (now,))
    conn.commit()

    # Compound patterns for Bhairavastava: for each token index in each verse
    # that represents a compound, we add alternative analyses.
    # Format: (reading_id, token_index, relation, member_count, gloss, prior)
    compounds = [
        # Verse 1
        ("bhairavastava.1.reading.bhairavastava.gretil", 0, "karmadharaya", 2, "Bhairava the Lord (appositional)", 0.3),
        ("bhairavastava.1.reading.bhairavastava.gretil", 0, "tatpurusa", 2, "lord of Bhairava (possessive)", -0.3),
        ("bhairavastava.1.reading.bhairavastava.gretil", 1, "karmadharaya", 2, "the helpless one who is a refuge", 0.2),
        ("bhairavastava.1.reading.bhairavastava.gretil", 1, "tatpurusa", 2, "refuge of the helpless", 0.3),
        ("bhairavastava.1.reading.bhairavastava.gretil", 2, "karmadharaya", 2, "the state of having a mind consisting of you", 0.2),
        ("bhairavastava.1.reading.bhairavastava.gretil", 2, "bahuvrihi", 2, "one whose mind consists of you", 0.1),
        # Verse 4
        ("bhairavastava.4.reading.bhairavastava.gretil", 0, "karmadharaya", 3, "Sankara-service-contemplation-steadfast", 0.2),
        ("bhairavastava.4.reading.bhairavastava.gretil", 1, "karmadharaya", 3, "terrible-Bhairava-power-possessed", 0.2),
        # Verse 5
        ("bhairavastava.5.reading.bhairavastava.gretil", 0, "dvandva", 4, "death-Yama-Antaka-karma-demons", 0.2),
        # Verse 6
        ("bhairavastava.6.reading.bhairavastava.gretil", 0, "karmadharaya", 4, "being-nectar-full-filled", 0.2),
        # Verse 7
        ("bhairavastava.7.reading.bhairavastava.gretil", 2, "karmadharaya", 4, "you-non-difference-hymn-nectar-shower", 0.2),
        # Verse 8
        ("bhairavastava.8.reading.bhairavastava.gretil", 0, "karmadharaya", 3, "your-scripture-nectar-thought", 0.2),
        ("bhairavastava.8.reading.bhairavastava.gretil", 2, "karmadharaya", 2, "peace-stream", 0.2),
        # Verse 9
        ("bhairavastava.9.reading.bhairavastava.gretil", 3, "karmadharaya", 2, "beautiful-vision", 0.2),
        ("bhairavastava.9.reading.bhairavastava.gretil", 7, "tatpurusa", 2, "knower of the right time", 0.2),
    ]

    count = 0
    for rid, token_idx, relation, members, gloss, prior in compounds:
        # Find occurrence
        occ = conn.execute("""
            SELECT occurrence_id FROM token_occurrence
            WHERE passage_reading_id = ? AND token_index = ?
        """, (rid, token_idx)).fetchone()

        if not occ:
            continue

        occ_id = occ[0]
        analysis_id = f"cmp_{rid}_{token_idx}_{relation}"

        # Create analysis type for the compound (skip if FK fails)
        features = json.dumps({
            "compound_relation": relation,
            "member_count": members,
            "compound_gloss": gloss,
        })
        try:
            conn.execute("""INSERT INTO morph_analysis_type
                (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (analysis_id, "lex_unknown", features, f"cmp_{relation}_{token_idx}", now))
        except Exception:
            continue  # FK failed, skip this compound

        # Create hypothesis
        hyp_id = f"hyp_{analysis_id}"
        try:
            conn.execute("""INSERT INTO token_analysis_hypothesis
                (hypothesis_id, occurrence_id, analysis_type_id, engine,
                 confidence, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
                (hyp_id, occ_id, analysis_id, "manual_compound",
                 max(prior + 0.5, 0.1), now))
        except Exception:
            continue
        count += 1

    conn.commit()
    print(f"  Added {count} compound hypotheses")

    # Verify
    for rid, token_idx, *_ in compounds[:3]:
        n = conn.execute("""
            SELECT count(*) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            WHERE tocc.passage_reading_id = ? AND tocc.token_index = ?
        """, (rid, token_idx)).fetchone()[0]
        print(f"    {rid} token {token_idx}: {n} hypotheses")

    return count


def main():
    print("=" * 60)
    print("PHASE A5b — Direct compound hypothesis seeding")
    print("=" * 60)

    db_path = BASE / "data" / "sanskritree-v2.db"
    conn = connect(str(db_path))

    # Ensure placeholder lexeme (seed function also does this, but be safe)
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("""INSERT OR IGNORE INTO lexeme
        (lexeme_id, lemma_slp1, pos, created_at)
        VALUES ('lex_unknown', '__unknown__', 'unknown', ?)""", (now,))
    conn.commit()

    count = seed_compound_hypotheses(conn, "abhinavagupta_bhairavastava")

    conn.close()
    print(f"\nTotal compound hypotheses seeded: {count}")


if __name__ == "__main__":
    main()
