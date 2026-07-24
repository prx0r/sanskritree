"""Phase C3c: Heritage integration — exhaustive sandhi splitting for Tantric compounds.

Takes IAST passages, converts to Devanagari, calls Heritage Reader, parses
solutions, and seeds results into the graph ontology tables.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parents[1]
sys.path.insert(0, str(BASE / "src"))

from sanskritree.database import connect


def heritage_segment(iast_text: str) -> list[list[dict]] | None:
    """Call Heritage Reader via Python wrapper, return list of solutions.

    Each solution is a list of word analyses: [{word, root, analyses, ...}]
    """
    from vidyut.lipi import transliterate, Scheme
    from heritage.heritage import HeritagePlatform, SolutionAnalysis

    deva = transliterate(iast_text, Scheme.Iast, Scheme.Devanagari)
    platform = HeritagePlatform(method="web")
    result = platform.get_analysis(deva, sentence=True, unsandhied=False, structured=True)

    if not result or not isinstance(result, dict):
        return None

    solutions = []
    for sol_id in sorted(result.keys()):
        sol = result[sol_id]
        if not isinstance(sol, SolutionAnalysis) or not sol.words:
            continue

        words_analysis = []
        for w in sol.words:
            word_data = {
                "text": str(w.text),
                "root": None,
                "analyses": [],
            }
            if hasattr(w, 'candidates') and w.candidates:
                candidates = list(w.candidates)
                if candidates:
                    word_data["root"] = str(candidates[0].root)
                    for c in candidates:
                        if hasattr(c, 'analyses'):
                            for a in list(c.analyses)[:3]:
                                word_data["analyses"].append([str(x) for x in a])
            words_analysis.append(word_data)
        solutions.append(words_analysis)

    return solutions if solutions else None


def seed_heritage_results(conn, work_id: str, max_verses: int | None = None):
    """Run Heritage on all verses in a work and seed results."""
    now = datetime.now(timezone.utc).isoformat()

    verses = conn.execute("""
        SELECT p.passage_id, p.verse_start, pr.reading_id, pr.sanskrit_raw
        FROM passages p
        JOIN passage_readings pr ON pr.passage_id = p.passage_id
        WHERE p.work_id = ? AND p.passage_type = 'verse'
        ORDER BY p.sequence_index
    """, (work_id,)).fetchall()

    if max_verses:
        verses = verses[:max_verses]

    total_solutions = 0
    total_hyps = 0
    errors = 0

    for pid, vs, rid, raw in verses:
        # Clean verse text
        import re
        clean = re.sub(r'\|\|\s*(?:AgBhaist|vspk)_?[\d.]+\s*\|\|?$', '', raw).strip()

        try:
            solutions = heritage_segment(clean)
        except Exception as e:
            errors += 1
            continue

        if not solutions:
            continue

        # Use the first solution (most likely correct parse)
        best = solutions[0]
        total_solutions += 1

        # For each word in the solution, find or create the token occurrence
        token_offset = 0
        for wi, word_data in enumerate(best):
            surface_deva = word_data["text"]
            root = word_data["root"]
            if not root:
                continue

            # Convert root Devanagari → IAST → SLP1 for lexeme lookup
            from vidyut.lipi import transliterate, Scheme
            try:
                root_iast = transliterate(root, Scheme.Devanagari, Scheme.Iast)
                root_slp1 = transliterate(root, Scheme.Devanagari, Scheme.Slp1)
            except Exception:
                root_iast = root
                root_slp1 = root

            # Find or create lexeme
            lid = f"lex_heritage_{root_slp1}"
            conn.execute("""INSERT OR IGNORE INTO lexeme
                (lexeme_id, lemma_slp1, lemma_iast, lemma_devanagari, pos, created_at)
                VALUES (?, ?, ?, ?, 'heritage_analysis', ?)""",
                (lid, root_slp1, root_iast, root, now))

            # Find matching token_occurrence
            occ = conn.execute("""
                SELECT occurrence_id FROM token_occurrence
                WHERE passage_reading_id = ? AND token_index = ?
                  AND surface LIKE ?
                LIMIT 1
            """, (rid, token_offset, f"%{surface_deva[:20]}%")).fetchone()

            if not occ:
                continue

            occ_id = occ[0]

            # Extract grammatical features
            features = {}
            if word_data["analyses"]:
                first = word_data["analyses"][0]
                if len(first) >= 3:
                    features["heritage_gender"] = first[0]  # नपुं, पुं, स्त्री
                    features["heritage_case"] = first[1]    # 1-8 (vibhakti)
                    features["heritage_number"] = first[2]  # एक, द्वि, बहु

            # Create analysis type
            feat_json = json.dumps(features)
            fhash = root_slp1[:16]
            atype_id = f"mat_heritage_{rid}_{wi}_{root_slp1}"
            conn.execute("""INSERT OR IGNORE INTO morph_analysis_type
                (analysis_type_id, lexeme_id, features_json, features_hash, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (atype_id, lid, feat_json, fhash, now))

            # Create hypothesis
            hyp_id = f"hyp_heritage_{rid}_{wi}"
            conn.execute("""INSERT OR IGNORE INTO token_analysis_hypothesis
                (hypothesis_id, occurrence_id, analysis_type_id, engine,
                 confidence, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'proposed', ?)""",
                (hyp_id, occ_id, atype_id, "heritage", 0.7, now))
            total_hyps += 1

        token_offset += 1

    conn.commit()
    return total_solutions, total_hyps, errors


def main():
    print("=" * 60)
    print("PHASE C3c — Heritage integration")
    print("=" * 60)

    db_path = BASE / "data" / "sanskritree-v2.db"
    conn = connect(str(db_path))

    # Test heritage on a single verse first
    print("\n[1] Testing Heritage on Bhairavastava verse 1...")
    test = "bhairavanātham anāthaśaraṇyaṃ tvanmayacittatayā hṛdi vande"
    solutions = heritage_segment(test)
    if solutions:
        best = solutions[0]
        print(f"  {len(solutions)} solutions found")
        for w in best:
            print(f"    {w['text']:20s} → root={w['root'] or '-':15s} analyses={w['analyses'][:2]}")
    else:
        print("  Heritage returned no solutions")

    print("\n[2] Seeding Heritage results for all active works...")
    for wid in ["abhinavagupta_bhairavastava", "spandakarika"]:
        print(f"\n  --- {wid} ---")
        n_sol, n_hyp, n_err = seed_heritage_results(conn, wid, max_verses=5)
        print(f"  Solutions: {n_sol}, Hypotheses: {n_hyp}, Errors: {n_err}")

    # Verify coverage improvement
    for wid in ["abhinavagupta_bhairavastava", "spandakarika"]:
        verses = conn.execute("""
            SELECT count(*) FROM passages p
            JOIN passage_readings pr ON pr.passage_id = p.passage_id
            WHERE p.work_id = ? AND p.passage_type = 'verse'
        """, (wid,)).fetchone()[0]
        hyps = conn.execute("""
            SELECT count(*) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            JOIN passages p ON p.passage_id = pr.passage_id
            WHERE p.work_id = ? AND tah.engine = 'heritage'
        """, (wid,)).fetchone()[0]
        engines = conn.execute("""
            SELECT tah.engine, count(*) FROM token_analysis_hypothesis tah
            JOIN token_occurrence tocc ON tah.occurrence_id = tocc.occurrence_id
            JOIN passage_readings pr ON pr.reading_id = tocc.passage_reading_id
            WHERE pr.reading_id LIKE (SELECT reading_id FROM passage_readings pr2
                JOIN passages p2 ON p2.passage_id = pr2.passage_id
                WHERE p2.work_id = ? LIMIT 1)
            GROUP BY tah.engine
        """, (wid,)).fetchall()
        print(f"  {wid}: {verses} verses, {hyps} heritage hyps")
        for eng, cnt in engines:
            print(f"    engine={eng}: {cnt}")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
