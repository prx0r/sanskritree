"""Heritage compound mapping: API splits → graph ontology hypotheses."""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect
from vidyut.lipi import transliterate, Scheme
from heritage.heritage import HeritagePlatform, SolutionAnalysis

DB = str(BASE / "data" / "sanskritree-v2.db")


def get_heritage_verse_split(iast_text: str) -> list[list[str]] | None:
    """Call Heritage on IAST text, return best split as list of word groups."""
    import re
    clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', iast_text).strip()
    deva = transliterate(clean, Scheme.Iast, Scheme.Devanagari)
    platform = HeritagePlatform(method="web")
    result = platform.get_analysis(deva, sentence=True, structured=True)
    if not result:
        return None
    # Get first solution
    for sol_id in sorted(result.keys()):
        sol = result[sol_id]
        if isinstance(sol, SolutionAnalysis) and sol.words:
            words = [str(w.text) for w in sol.words]
            return words
    return None


def seed_heritage_for_passage(conn, reading_id: str, iast_text: str) -> int:
    """Seed Heritage compound hypotheses for a passage."""
    now = datetime.now(timezone.utc).isoformat()
    heritage_words = get_heritage_verse_split(iast_text)
    if not heritage_words:
        return 0

    # Get original token occurrences
    tokens = conn.execute("""
        SELECT token_index, surface FROM token_occurrence
        WHERE passage_reading_id = ? ORDER BY token_index
    """, (reading_id,)).fetchall()

    if not tokens:
        return 0

    # Map Heritage word groups to original tokens
    # Heritage may split one token into multiple words
    # We need to align by position
    hyp_count = 0
    
    # For each original token, try to find if Heritage split it
    for idx, surface in tokens:
        # Check if token already has a non-unknown lemma hypothesis
        has_lemma = conn.execute("""
            SELECT 1 FROM token_analysis_hypothesis tah
            JOIN morph_analysis_type mat ON mat.analysis_type_id = tah.analysis_type_id
            WHERE tah.occurrence_id = (SELECT occurrence_id FROM token_occurrence 
                WHERE passage_reading_id = ? AND token_index = ?)
              AND mat.lexeme_id != 'lex_unknown' LIMIT 1
        """, (reading_id, idx)).fetchone()

        if has_lemma:
            continue  # Already has analysis

        # Find this token's surface in the Heritage output
        # Heritage returns Devanagari, convert token surface for matching
        try:
            token_deva = transliterate(surface, Scheme.Iast, Scheme.Devanagari)
        except Exception:
            continue

        # Check if Heritage split this token
        deva_members = []
        i = 0
        while i < len(heritage_words):
            # Try to match token against one or more Heritage words
            matched = False
            for j in range(1, min(5, len(heritage_words) - i + 1)):
                combined = ''.join(heritage_words[i:i+j])
                # Remove trailing 'a' that Heritage adds
                combined_stripped = combined.rstrip('a')
                if combined_stripped == token_deva.rstrip('a') or combined == token_deva:
                    deva_members = heritage_words[i:i+j]
                    heritage_words = heritage_words[:i] + heritage_words[i+j:]
                    matched = True
                    break
            if matched:
                break
            i += 1

        if len(deva_members) < 2:
            continue  # Not split or only 1 member

        # Convert members back to IAST
        try:
            iast_members = [transliterate(w, Scheme.Devanagari, Scheme.Iast) for w in deva_members]
        except Exception:
            iast_members = deva_members

        member_len = len(iast_members)
        if member_len == 2:
            # Create both karmadharaya and tatpurusa hypotheses
            for rel, prior in [("karmadharaya", 0.3), ("tatpurusa", 0.1)]:
                hyp_id = f"her_{reading_id}_{idx}_{rel}"
                atype_id = f"mat_her_{reading_id}_{idx}_{rel}"
                features = json.dumps({
                    "compound_members": iast_members,
                    "compound_relation": rel,
                    "heritage_split": deva_members,
                })
                conn.execute("""INSERT OR IGNORE INTO morph_analysis_type
                    (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                    VALUES (?, 'lex_unknown', ?, ?, ?)""",
                    (atype_id, features, f"her_{rel}_{idx}", now))
                occ = conn.execute("""
                    SELECT occurrence_id FROM token_occurrence
                    WHERE passage_reading_id = ? AND token_index = ?
                """, (reading_id, idx)).fetchone()
                if occ:
                    conn.execute("""INSERT OR IGNORE INTO token_analysis_hypothesis
                        (hypothesis_id, occurrence_id, analysis_type_id, engine,
                         confidence, status, created_at)
                        VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
                        (hyp_id, occ[0], atype_id, "heritage_compound",
                         prior + 0.4, now))
                    hyp_count += 1
        elif member_len >= 3:
            # Multi-member compound — add dvandva or karmadharaya with note
            hyp_id = f"her_{reading_id}_{idx}_dvandva"
            atype_id = f"mat_her_{reading_id}_{idx}_dv"
            features = json.dumps({
                "compound_members": iast_members,
                "compound_relation": "multi_member",
                "member_count": member_len,
                "heritage_split": deva_members,
            })
            conn.execute("""INSERT OR IGNORE INTO morph_analysis_type
                (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                VALUES (?, 'lex_unknown', ?, ?, ?)""",
                (atype_id, features, f"her_multi_{idx}", now))
            occ = conn.execute("""
                SELECT occurrence_id FROM token_occurrence
                WHERE passage_reading_id = ? AND token_index = ?
            """, (reading_id, idx)).fetchone()
            if occ:
                conn.execute("""INSERT OR IGNORE INTO token_analysis_hypothesis
                    (hypothesis_id, occurrence_id, analysis_type_id, engine,
                     confidence, status, created_at)
                    VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
                    (hyp_id, occ[0], atype_id, "heritage_compound", 0.5, now))
                hyp_count += 1

    conn.commit()
    return hyp_count


def process_work(conn, work_id: str, max_passages: int | None = None):
    """Process all verses in a work through Heritage mapping."""
    verses = conn.execute("""
        SELECT p.passage_id, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """, (work_id,)).fetchall()

    if max_passages:
        verses = verses[:max_passages]

    total = 0
    errors = 0
    for pid, rid, raw in verses:
        try:
            n = seed_heritage_for_passage(conn, rid, raw)
            total += n
        except Exception as e:
            errors += 1

    return total, errors


def main():
    print("Heritage compound mapping\n")
    conn = connect(DB)

    for wid in ["abhinavagupta_bhairavastava", "spandakarika"]:
        total, errors = process_work(conn, wid, max_passages=20)
        print(f"  {wid}: {total} hypotheses, {errors} errors")

    # Verify coverage improvement
    for wid in ["abhinavagupta_bhairavastava", "spandakarika"]:
        verses = conn.execute(
            "SELECT count(*) FROM passages WHERE work_id=? AND passage_type='verse'",
            (wid,)).fetchone()[0]
        with_hyp = conn.execute("""
            SELECT count(DISTINCT tocc.occurrence_id) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id=?
        """, (wid,)).fetchone()[0]
        tot_tokens = conn.execute("""
            SELECT count(*) FROM token_occurrence tocc
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id=?
        """, (wid,)).fetchone()[0]
        print(f"\n  {wid}: {with_hyp}/{tot_tokens} tokens with hypotheses ({with_hyp/max(tot_tokens,1)*100:.0f}%)")

    # Show engine distribution
    engines = conn.execute("""
        SELECT tah.engine, count(*) FROM token_analysis_hypothesis tah
        GROUP BY tah.engine ORDER BY count(*) DESC
    """).fetchall()
    print(f"\n  Engine distribution:")
    for eng, cnt in engines:
        print(f"    {eng}: {cnt}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
