"""Phase A5: Rule-based compound splitter. Generates candidate splits for
unsplit compounds by checking against the existing lexeme table."""
from __future__ import annotations

import json
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect


def load_lexeme_lemmas(conn) -> set[str]:
    rows = conn.execute("SELECT lemma_slp1 FROM lexeme").fetchall()
    return {r[0] for r in rows}


def iast_to_slp1(text: str) -> str:
    """Rough IAST→SLP1 for checking against lexeme table."""
    m = {
        'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṛ': 'f', 'ṝ': 'F',
        'ḷ': 'x', 'ḹ': 'X', 'ṃ': 'M', 'ḥ': 'H',
        'ñ': 'Y', 'ṭ': 'T', 'ḍ': 'D', 'ṇ': 'N',
        'ś': 'S', 'ṣ': 'z', 'ḻ': 'L',
    }
    result = []
    for c in text:
        if c in m:
            result.append(m[c])
        elif unicodedata.category(c).startswith('L'):
            result.append(c)
    return ''.join(result)


def generate_splits(token: str, lemmas: set[str], min_len: int = 2) -> list[list[str]]:
    """Generate all possible compound splits where each member is in lemma set."""
    token_slp1 = iast_to_slp1(token)
    n = len(token_slp1)
    results = []

    def backtrack(pos: int, parts: list[str]):
        if pos == n:
            if len(parts) >= 2:
                results.append(list(parts))
            return
        for end in range(pos + min_len, min(n, pos + 20) + 1):
            candidate = token_slp1[pos:end]
            if candidate in lemmas:
                parts.append(candidate)
                backtrack(end, parts)
                parts.pop()
        # Also try the full remaining as one member
        remaining = token_slp1[pos:]
        if remaining in lemmas and len(parts) >= 1:
            parts.append(remaining)
            results.append(list(parts))
            parts.pop()

    backtrack(0, [])
    return results


def add_compound_hypotheses(conn, work_id: str):
    """For each passage in the work, generate compound split candidates
    for tokens that lack lemma analyses."""
    lemmas = load_lexeme_lemmas(conn)

    passages = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ?
        ORDER BY p.sequence_index
    """, (work_id,)).fetchall()

    total_hypotheses = 0
    total_compounds = 0

    for pid, rid, raw in passages:
        # Normalize: strip metadata like || AgBhaist_N
        import re
        clean = re.sub(r'\|\|\s*AgBhaist_\d+\s*\|\|?$', '', raw).strip()

        tokens = clean.split()
        for idx, token in enumerate(tokens):
            # Check if token already has lemma hypotheses
            has_lemma = conn.execute("""
                SELECT 1 FROM token_occurrence tocc
                JOIN token_analysis_hypothesis tah ON tah.occurrence_id = tocc.occurrence_id
                JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
                JOIN lexeme l ON l.lexeme_id = mat.lexeme_id
                WHERE tocc.passage_reading_id = ? AND tocc.token_index = ?
                LIMIT 1
            """, (rid, idx)).fetchone()

            if has_lemma:
                continue  # already has morphological analysis

            # Try to split
            splits = generate_splits(token, lemmas)
            if not splits:
                continue

            for split in splits:
                # Ensure each compound member exists as a lexeme
                member_ids = []
                for m in split:
                    mid = f"lex_cmp_{m}"
                    conn.execute("""INSERT OR IGNORE INTO lexeme
                        (lexeme_id, lemma_slp1, pos, created_at)
                        VALUES (?, ?, 'compound_member', ?)""",
                        (mid, m, datetime.now(timezone.utc).isoformat()))
                    member_ids.append(mid)

                # Create analysis type for this compound
                split_str = "+".join(split)
                atype_id = f"cmp_{pid}_{idx}_{split_str}"
                features = {
                    "compound_members": split,
                    "compound_relation": "unknown",
                    "compound_gloss": " + ".join(split),
                }
                conn.execute("""INSERT OR IGNORE INTO morph_analysis_type
                    (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)""",
                    (atype_id, member_ids[0], json.dumps(features),
                     split_str[:16], datetime.now(timezone.utc).isoformat()))

                # Create hypothesis for each occurrence
                occs = conn.execute("""
                    SELECT occurrence_id FROM token_occurrence
                    WHERE passage_reading_id = ? AND token_index = ?
                """, (rid, idx)).fetchall()

                for (occ_id,) in occs:
                    hyp_id = f"hyp_compound_{pid}_{idx}_{split_str}"
                    conn.execute("""INSERT OR IGNORE INTO token_analysis_hypothesis
                        (hypothesis_id, occurrence_id, analysis_type_id, engine,
                         confidence, status, created_at)
                        VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
                        (hyp_id, occ_id, atype_id, "compound_splitter",
                         0.3, datetime.now(timezone.utc).isoformat()))
                    total_hypotheses += 1
                total_compounds += 1

    conn.commit()
    print(f"  Compounds split: {total_compounds}")
    print(f"  Hypotheses added: {total_hypotheses}")


def main():
    print("=" * 60)
    print("PHASE A5 — Compound splitting")
    print("=" * 60)

    db_path = BASE / "data" / "sanskritree-v2.db"
    conn = connect(str(db_path))

    # Ensure placeholder lexeme exists for compound members not in DB
    conn.execute("""INSERT OR IGNORE INTO lexeme
        (lexeme_id, lemma_slp1, pos, created_at)
        VALUES ('lex_unknown', '__unknown__', 'unknown', ?)""",
        (datetime.now(timezone.utc).isoformat(),))

    for wid in ["abhinavagupta_bhairavastava"]:
        print(f"\n  Work: {wid}")
        add_compound_hypotheses(conn, wid)

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
